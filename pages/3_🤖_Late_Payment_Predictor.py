"""
pages/3_🤖_Late_Payment_Predictor.py - Machine Learning Risk Radar & Simulator
Provides machine learning predictions for late payers, feature explainability, and an interactive sandbox.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

import database
import ml_model

st.set_page_config(page_title="Late Payment Predictor", page_icon="🤖", layout="wide")

database.init_db()
database.refresh_invoice_statuses()

st.title("🤖 ML Late Payment Predictor & Risk Radar")
st.caption("Predicts the likelihood of an invoice being paid late using a Scikit-Learn Random Forest model trained on customer payment history.")

# Educational Explainer for Novices
with st.expander("🎓 How does this Machine Learning model work? (Click to learn)", expanded=False):
    st.markdown("""
    ### 🧠 How Machine Learning Predicts Late Payers
    In traditional invoicing, business owners only know a client is late **after** the due date passes. 
    By using Machine Learning, we can **forecast risk on the day the invoice is issued**:
    
    1. **Historical Delay (`avg_delay`)**: Does this client usually pay on time, or do they habitually drag payments by 2-3 weeks?
    2. **Past Delinquency Rate (`late_rate`)**: What percentage of their historical invoices were paid past due?
    3. **Relationship Depth (`total_past_invs`)**: Established long-term clients with 10+ paid invoices have more predictable payment habits than first-time clients.
    4. **Invoice Ticket Size (`amount`)**: Large invoices (e.g. $10,000+) frequently encounter longer internal approval chains than smaller expenses ($500).
    5. **Credit Terms (`term_days`)**: Net-45 or Net-60 terms give clients more room for payment delays than Net-15.
    
    The algorithm outputs a **calibrated probability (0% to 100%)** that categorizes each invoice into **Low Risk 🟢**, **Medium Risk 🟡**, or **High Risk 🔴**.
    """)

tab_radar, tab_simulator, tab_model_health = st.tabs(["🎯 Live Risk Radar", "🎛️ What-If Simulator", "📊 Model Metrics & Training"])

# TAB 1: Live Risk Radar across all open invoices
with tab_radar:
    st.subheader("🎯 Risk Radar for Outstanding Invoices")
    st.caption("Active invoices scored in real-time by the trained Machine Learning model.")

    invoices = database.get_all_invoices()
    unpaid = [i for i in invoices if i["status"] in ("Pending", "Overdue")]

    if not unpaid:
        st.success("All invoices are currently marked as Paid! Create a new invoice to see the risk radar.")
    else:
        radar_items = []
        for inv in unpaid:
            risk = ml_model.predict_invoice_risk(inv["customer_id"], inv["amount"], inv["term_days"])
            radar_items.append({
                "invoice_id": inv["id"],
                "invoice_number": inv["invoice_number"],
                "customer": f"{inv['customer_name']} ({inv['customer_company']})",
                "amount": inv["amount"],
                "due_date": inv["due_date"],
                "status": inv["status"],
                "risk_probability": risk["risk_probability"],
                "risk_level": risk["risk_level"],
                "risk_badge": risk["risk_badge"],
                "drivers": risk["drivers"],
                "recommended_action": risk["recommended_action"]
            })

        # Sort with highest risk first
        radar_items.sort(key=lambda x: x["risk_probability"], reverse=True)

        for item in radar_items:
            risk_color = "#EF4444" if item["risk_level"] == "High" else ("#F59E0B" if item["risk_level"] == "Medium" else "#10B981")
            
            with st.container():
                st.markdown(f"""
                <div style="border-left: 5px solid {risk_color}; background-color: #F8FAFC; border-radius: 8px; padding: 1rem; margin-bottom: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #1E293B;">{item['invoice_number']} — {item['customer']}</h4>
                        <span style="font-size: 1.1rem; font-weight: bold; color: {risk_color};">{item['risk_badge']} ({item['risk_probability']}%)</span>
                    </div>
                    <p style="margin: 0.3rem 0; color: #475569;">
                        <strong>Amount:</strong> ${item['amount']:,.2f} &nbsp;|&nbsp; 
                        <strong>Due Date:</strong> {item['due_date']} &nbsp;|&nbsp; 
                        <strong>Status:</strong> {item['status']}
                    </p>
                    <p style="margin: 0.3rem 0; color: #334155; font-size: 0.95rem;">
                        <strong>Action:</strong> {item['recommended_action']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"🔍 View ML Driver Explanations for {item['invoice_number']}"):
                    for d in item["drivers"]:
                        st.markdown(f"• {d}")

# TAB 2: Interactive What-If Simulator
with tab_simulator:
    st.subheader("🎛️ Interactive Late Payer Risk Simulator")
    st.caption("Adjust client behavior sliders below to see how the Machine Learning model predicts risk in real time.")

    sim_col1, sim_col2 = st.columns([1.2, 1])

    with sim_col1:
        st.markdown("##### ⚙️ Input Parameters")
        sim_avg_delay = st.slider("Historical Average Payment Delay (Days past due)", min_value=-5, max_value=45, value=15, help="Negative means early, positive means late.")
        sim_late_rate = st.slider("Past Late Payment Rate (%)", min_value=0, max_value=100, value=60, help="Percentage of past invoices paid after due date.")
        sim_past_invs = st.number_input("Number of Past Completed Invoices", min_value=0, max_value=50, value=4)
        sim_amount = st.slider("Invoice Amount ($)", min_value=100, max_value=25000, value=4500, step=250)
        sim_terms = st.selectbox("Credit Terms (Net Days)", [15, 30, 45, 60], index=1)

    # Compute prediction on simulated parameters
    saved = ml_model.get_or_train_model()
    sim_df = pd.DataFrame([{
        "avg_delay": sim_avg_delay,
        "late_rate": sim_late_rate / 100.0,
        "total_past_invs": sim_past_invs,
        "amount": sim_amount,
        "term_days": sim_terms
    }])[ml_model.FEATURE_NAMES]

    sim_prob = 0.20
    if saved and "model" in saved:
        clf = saved["model"]
        try:
            probs = clf.predict_proba(sim_df)
            if 1 in clf.classes_:
                c1_idx = list(clf.classes_).index(1)
                sim_prob = float(probs[0][c1_idx])
        except Exception:
            sim_prob = 0.35

    sim_prob_pct = round(sim_prob * 100, 1)

    with sim_col2:
        st.markdown("##### 📈 Live Prediction Outcome")
        
        # Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sim_prob_pct,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Late Payment Probability (%)", 'font': {'size': 18}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#1E293B"},
                'steps': [
                    {'range': [0, 35], 'color': '#A7F3D0'},
                    {'range': [35, 65], 'color': '#FDE68A'},
                    {'range': [65, 100], 'color': '#FECACA'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': sim_prob_pct
                }
            }
        ))
        fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

        if sim_prob_pct >= 65:
            st.error(f"🔴 **HIGH RISK ({sim_prob_pct}%)**: Highly likely to experience delayed settlement.")
            st.markdown("**Suggested Action:** Schedule an automated reminder 3 days before due date and request an advance deposit next cycle.")
        elif sim_prob_pct >= 35:
            st.warning(f"🟡 **MEDIUM RISK ({sim_prob_pct}%)**: Moderate delay probability.")
            st.markdown("**Suggested Action:** Send a polite WhatsApp reminder on the due date morning.")
        else:
            st.success(f"🟢 **LOW RISK ({sim_prob_pct}%)**: Punctual payment expected.")
            st.markdown("**Suggested Action:** Follow standard automated monthly billing.")

# TAB 3: Model Health & Retraining
with tab_model_health:
    st.subheader("📊 Model Architecture, Metrics & Retraining")
    st.caption("Evaluate how well the Random Forest model performs and retrain it on updated payment logs.")

    model_data = ml_model.get_or_train_model()
    metrics = model_data.get("metrics", {}) if model_data else {}

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Training Samples", f"{metrics.get('samples', 0)} payments")
    m2.metric("Accuracy", f"{metrics.get('accuracy', 0)}%")
    m3.metric("Precision", f"{metrics.get('precision', 0)}%")
    m4.metric("Recall", f"{metrics.get('recall', 0)}%")
    m5.metric("ROC-AUC Score", f"{metrics.get('roc_auc', 0)}")

    st.markdown("---")

    col_feat, col_retrain = st.columns([1.5, 1])

    with col_feat:
        st.subheader("🏆 Feature Importance (What drives late payments?)")
        st.caption("How much weight the ML algorithm places on each client attribute.")
        
        fi = metrics.get("feature_importances", {})
        if fi:
            friendly_names = {
                "avg_delay": "Past Average Delay",
                "late_rate": "Historical Overdue Rate",
                "amount": "Invoice Amount",
                "total_past_invs": "Client Invoices Count",
                "term_days": "Payment Terms"
            }
            fi_df = pd.DataFrame([
                {"Feature": friendly_names.get(k, k), "Importance": float(v)}
                for k, v in fi.items()
            ]).sort_values(by="Importance", ascending=True)

            fig_fi = px.bar(
                fi_df,
                x="Importance",
                y="Feature",
                orientation="h",
                text_auto=".1%",
                color="Importance",
                color_continuous_scale="Blues"
            )
            fig_fi.update_layout(height=280, showlegend=False, margin=dict(l=10, r=10, t=20, b=20))
            st.plotly_chart(fig_fi, use_container_width=True)

    with col_retrain:
        st.subheader("🔄 Retrain ML Model")
        st.markdown("""
        As you mark more invoices as paid in the **Invoices** page, your payment history database grows. 
        Click below to retrain the algorithm on all current data.
        """)
        
        if st.button("🚀 Retrain Model Now", type="primary"):
            with st.spinner("Retraining Random Forest model on latest records..."):
                res = ml_model.train_model()
                if res["success"]:
                    st.success(f"Model retrained successfully! Accuracy: {res['accuracy']}% across {res['samples']} records.")
                    st.rerun()
                else:
                    st.warning(res["message"])
