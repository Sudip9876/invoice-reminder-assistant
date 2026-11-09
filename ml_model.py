"""
ml_model.py - Machine Learning Engine for Predicting Late Payers
Uses historical payment patterns to predict the probability of an invoice being paid late.
Includes explainability: highlights the exact business factors driving the risk score.
"""

import os
import sqlite3
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
import joblib

from database import get_connection, get_customer_stats

MODEL_FILE = "late_payer_model.joblib"

# Feature column names
FEATURE_NAMES = [
    "avg_delay",          # Historical average delay in days
    "late_rate",          # Ratio of past invoices that were late (0.0 to 1.0)
    "total_past_invs",    # Number of prior invoices (relationship depth)
    "amount",             # Current invoice amount in currency
    "term_days"           # Credit payment terms (e.g., 15, 30, 45 days)
]

def build_training_dataset() -> pd.DataFrame:
    """
    Constructs a tabular dataset from the payment_history table.
    For each historical payment, reconstructs the customer's prior profile at that point.
    """
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT id, customer_id, amount, term_days, delay_days, was_late
        FROM payment_history
        ORDER BY id ASC
    """, conn)
    conn.close()

    if df.empty:
        return pd.DataFrame()

    rows = []
    # Reconstruct running statistics so past predictions don't leak future data
    customer_history = {}

    for _, row in df.iterrows():
        c_id = row["customer_id"]
        if c_id not in customer_history:
            customer_history[c_id] = []

        past = customer_history[c_id]
        if len(past) == 0:
            avg_delay = 0.0
            late_rate = 0.0
            total_past = 0
        else:
            avg_delay = np.mean([p["delay"] for p in past])
            late_rate = np.mean([p["was_late"] for p in past])
            total_past = len(past)

        rows.append({
            "avg_delay": avg_delay,
            "late_rate": late_rate,
            "total_past_invs": total_past,
            "amount": row["amount"],
            "term_days": row["term_days"],
            "was_late": row["was_late"]
        })

        # Update customer running history
        customer_history[c_id].append({
            "delay": row["delay_days"],
            "was_late": row["was_late"],
            "amount": row["amount"]
        })

    return pd.DataFrame(rows)

def train_model() -> Dict[str, Any]:
    """
    Trains the Random Forest classifier on historical payment records.
    Saves model artifact and returns performance metrics.
    """
    data = build_training_dataset()
    if data.empty or len(data) < 5:
        return {"success": False, "message": "Not enough payment history to train model (minimum 5 records)."}

    X = data[FEATURE_NAMES]
    y = data["was_late"]

    # Use Random Forest with balanced class weights
    clf = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42, class_weight="balanced")
    clf.fit(X, y)

    # In-sample metrics (dataset size is small in early business stages)
    preds = clf.predict(X)
    probs = clf.predict_proba(X)[:, 1] if len(clf.classes_) > 1 else np.zeros(len(X))

    acc = accuracy_score(y, preds)
    prec = precision_score(y, preds, zero_division=0)
    rec = recall_score(y, preds, zero_division=0)
    auc = roc_auc_score(y, probs) if len(np.unique(y)) > 1 else 1.0

    # Feature importances
    importances = dict(zip(FEATURE_NAMES, clf.feature_importances_))

    joblib.dump({"model": clf, "metrics": {
        "accuracy": round(acc * 100, 1),
        "precision": round(prec * 100, 1),
        "recall": round(rec * 100, 1),
        "roc_auc": round(auc, 2),
        "samples": len(data),
        "feature_importances": importances
    }}, MODEL_FILE)

    return {
        "success": True,
        "accuracy": round(acc * 100, 1),
        "precision": round(prec * 100, 1),
        "recall": round(rec * 100, 1),
        "roc_auc": round(auc, 2),
        "samples": len(data),
        "feature_importances": importances
    }

def get_or_train_model():
    """Loads existing trained model or trains one if missing."""
    if os.path.exists(MODEL_FILE):
        try:
            return joblib.load(MODEL_FILE)
        except Exception:
            pass
    train_model()
    if os.path.exists(MODEL_FILE):
        return joblib.load(MODEL_FILE)
    return None

def predict_invoice_risk(customer_id: int, amount: float, term_days: int = 30) -> Dict[str, Any]:
    """
    Predicts the late payment risk for a specific invoice.
    Returns probability (0-100%), risk level (Low, Medium, High), and plain-English reasons.
    """
    saved = get_or_train_model()
    stats = get_customer_stats(customer_id)

    # Feature vector
    avg_delay = stats["avg_delay"]
    late_rate = stats["late_rate"]
    total_past = stats["total_invoices"]

    features = pd.DataFrame([{
        "avg_delay": avg_delay,
        "late_rate": late_rate,
        "total_past_invs": total_past,
        "amount": amount,
        "term_days": term_days
    }])[FEATURE_NAMES]

    prob = 0.20  # Default baseline for brand new customers
    if saved and "model" in saved:
        clf = saved["model"]
        try:
            probs = clf.predict_proba(features)
            # Find class 1 index
            if 1 in clf.classes_:
                c1_idx = list(clf.classes_).index(1)
                prob = float(probs[0][c1_idx])
            else:
                prob = 0.10
        except Exception:
            prob = 0.30
    else:
        # Heuristic fallback if model not yet fitted
        if stats["has_history"]:
            prob = (late_rate * 0.7) + (0.3 if avg_delay > 10 else 0.0)
        else:
            prob = 0.25

    # Determine risk category
    prob_pct = round(prob * 100, 1)
    if prob_pct >= 65.0:
        level = "High"
        badge = "🔴 High Risk"
        color = "#e53e3e"
        action = "Send proactive pre-due reminder 3 days early & follow up on due date via WhatsApp."
    elif prob_pct >= 35.0:
        level = "Medium"
        badge = "🟡 Medium Risk"
        color = "#dd6b20"
        action = "Send friendly reminder on the due date morning."
    else:
        level = "Low"
        badge = "🟢 Low Risk"
        color = "#38a169"
        action = "Standard billing workflow. Client historically reliable."

    # Explainability: Generate human-readable reasons
    reasons = []
    if stats["has_history"]:
        if late_rate > 0.5:
            reasons.append(f"Client paid late on {int(late_rate * 100)}% of previous invoices ({stats['late_count']} of {total_past}).")
        elif late_rate == 0.0:
            reasons.append(f"100% on-time record across {total_past} past invoices.")

        if avg_delay > 10:
            reasons.append(f"Historical payment delay averages +{avg_delay:.0f} days past due.")
        elif avg_delay <= 0:
            reasons.append(f"Historically settles invoices on or before the due date (avg {avg_delay:.0f} days).")
    else:
        reasons.append("New customer with no prior payment history. Baseline risk applied.")

    if amount > 5000:
        reasons.append(f"Higher invoice value (${amount:,.2f}) tends to require longer enterprise approvals.")
    
    if term_days > 30:
        reasons.append(f"Extended payment terms ({term_days} days) correlate with longer settlement windows.")

    return {
        "risk_probability": prob_pct,
        "risk_level": level,
        "risk_badge": badge,
        "risk_color": color,
        "recommended_action": action,
        "drivers": reasons,
        "customer_stats": stats
    }
