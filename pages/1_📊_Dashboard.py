"""
pages/1_📊_Dashboard.py - Executive Accounts Receivable & Cash Flow Dashboard (INR & CRM)
Provides high-level financial metrics in INR (₹), aging analysis, CRM follow-ups, and predictive risk distribution.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

import database
import ml_model

st.set_page_config(page_title="Executive Dashboard (INR)", page_icon="📊", layout="wide")

database.init_db()
database.refresh_invoice_statuses()

st.title("📊 Executive Receivables & Cash-Flow Dashboard (INR)")
st.caption("Real-time financial health, overdue aging analysis, CRM follow-ups, and predictive credit risk in Indian Rupees (₹).")

# Load Invoices
all_invoices = database.get_all_invoices()
if not all_invoices:
    st.info("ℹ️ No invoice records found in the database. You have a clean slate! Create an invoice on the 'Invoices' page, or click **'🇮🇳 Load Demo'** in the sidebar to populate sample data.")
    st.stop()

df = pd.DataFrame(all_invoices)
today = date.today()

# Enrich DataFrame with days past due and ML risk scores
def compute_metrics(row):
    due = datetime.strptime(row["due_date"], "%Y-%m-%d").date()
    days_diff = (today - due).days
    
    if row["status"] in ("Pending", "Overdue"):
        risk = ml_model.predict_invoice_risk(row["customer_id"], row["amount"], row["term_days"])
        risk_level = risk["risk_level"]
        risk_prob = risk["risk_probability"]
    else:
        risk_level = "Paid"
        risk_prob = 0.0

    if row["status"] == "Paid":
        bucket = "Paid"
    elif days_diff <= 0:
        bucket = "Current (Not Due)"
    elif 1 <= days_diff <= 15:
        bucket = "1 - 15 Days Overdue"
    elif 16 <= days_diff <= 30:
        bucket = "16 - 30 Days Overdue"
    else:
        bucket = "30+ Days Overdue (Critical)"

    return pd.Series([days_diff, bucket, risk_level, risk_prob], index=["days_overdue", "aging_bucket", "risk_level", "risk_prob"])

df[["days_overdue", "aging_bucket", "risk_level", "risk_prob"]] = df.apply(compute_metrics, axis=1)

# Summary Stats in INR
total_invoiced = df["amount"].sum()
total_paid = df[df["status"] == "Paid"]["amount"].sum()
unpaid_df = df[df["status"] != "Paid"]
total_outstanding = unpaid_df["amount"].sum()
overdue_df = df[df["status"] == "Overdue"]
total_overdue = overdue_df["amount"].sum()
high_risk_amount = df[df["risk_level"] == "High"]["amount"].sum()

collection_rate = (total_paid / total_invoiced * 100) if total_invoiced > 0 else 0

# Metric Cards Row
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Invoiced", database.format_inr(total_invoiced), f"{len(df)} total invoices")
kpi2.metric("Total Outstanding", database.format_inr(total_outstanding), f"{len(unpaid_df)} open invoices")
kpi3.metric("Overdue Balance", database.format_inr(total_overdue), f"{len(overdue_df)} overdue", delta_color="inverse")
kpi4.metric("At-Risk Capital (ML)", database.format_inr(high_risk_amount), "High Risk Late Payers", delta_color="inverse")
kpi5.metric("Collection Rate", f"{collection_rate:.1f}%", "Cash Realization")

st.markdown("---")

# Visual Charts: 2 Columns
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader("⏳ Accounts Receivable Aging Buckets (INR)")
    st.caption("Distribution of open capital across overdue delinquency intervals.")
    
    bucket_order = ["Current (Not Due)", "1 - 15 Days Overdue", "16 - 30 Days Overdue", "30+ Days Overdue (Critical)"]
    aging_summary = unpaid_df.groupby("aging_bucket")["amount"].sum().reindex(bucket_order).fillna(0).reset_index()
    
    color_map = {
        "Current (Not Due)": "#3B82F6",
        "1 - 15 Days Overdue": "#F59E0B",
        "16 - 30 Days Overdue": "#F97316",
        "30+ Days Overdue (Critical)": "#EF4444"
    }

    fig_aging = px.bar(
        aging_summary,
        x="aging_bucket",
        y="amount",
        labels={"amount": "Outstanding (₹)", "aging_bucket": "Aging Interval"},
        text_auto=",.0f",
        color="aging_bucket",
        color_discrete_map=color_map
    )
    fig_aging.update_layout(showlegend=False, height=350, margin=dict(l=20, r=20, t=20, b=20), yaxis_title="Outstanding Amount (₹)")
    st.plotly_chart(fig_aging, width="stretch")

with col_right:
    st.subheader("🛡️ ML Late Payer Risk Exposure")
    st.caption("AI breakdown of pending capital according to default/delay probability.")
    
    risk_summary = unpaid_df.groupby("risk_level")["amount"].sum().reset_index()
    risk_color_map = {
        "Low": "#10B981",
        "Medium": "#F59E0B",
        "High": "#EF4444"
    }

    fig_risk = px.pie(
        risk_summary,
        names="risk_level",
        values="amount",
        hole=0.45,
        color="risk_level",
        color_discrete_map=risk_color_map
    )
    fig_risk.update_traces(textposition='inside', textinfo='percent+label')
    fig_risk.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_risk, width="stretch")

st.markdown("---")

# Bottom Section: Top Debtors and Urgent Action Table
bcol1, bcol2 = st.columns([1, 1.2])

with bcol1:
    st.subheader("🏢 Top Outstanding Balances by Client (₹)")
    client_balances = unpaid_df.groupby("customer_company")["amount"].sum().sort_values(ascending=True).reset_index()
    
    fig_clients = px.bar(
        client_balances,
        y="customer_company",
        x="amount",
        orientation="h",
        labels={"amount": "Unpaid Balance (₹)", "customer_company": "Client Company"},
        text_auto=",.0f",
        color_discrete_sequence=["#6366F1"]
    )
    fig_clients.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Unpaid Balance (₹)")
    st.plotly_chart(fig_clients, width="stretch")

with bcol2:
    st.subheader("🚨 Critical Invoices Requiring Follow-Up")
    urgent_items = unpaid_df[(unpaid_df["status"] == "Overdue") | (unpaid_df["risk_level"] == "High")].sort_values(by="days_overdue", ascending=False)
    
    if not urgent_items.empty:
        display_urgent = urgent_items[["invoice_number", "customer_company", "amount", "due_date", "days_overdue", "risk_level"]].copy()
        display_urgent.columns = ["Invoice #", "Company", "Amount", "Due Date", "Days Late", "Risk"]
        display_urgent["Amount"] = display_urgent["Amount"].apply(database.format_inr)
        st.dataframe(display_urgent, width="stretch", hide_index=True)
        st.caption("💡 *Tip: Head to **Smart Reminders** to send a 1-click WhatsApp or Email reminder with your UPI & Bank details.*")
    else:
        st.success("No critical overdue or high-risk invoices currently! Your collections are fully up to date.")
