"""
app.py - Invoice & Payment-Reminder Assistant
Main entrypoint and navigation hub for small business cash-flow & payment tracking.
"""

import streamlit as st
import datetime
import database
import ml_model

# Page configuration
st.set_page_config(
    page_title="Invoice & Payment-Reminder Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and seed demo data on first launch
database.init_db()
database.seed_demo_data_if_empty()
database.refresh_invoice_statuses()

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border-radius: 10px;
        padding: 1.2rem;
        border-left: 4px solid #3B82F6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .feature-card {
        background-color: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem;
        height: 100%;
        transition: transform 0.15s ease-in-out;
    }
    .feature-card:hover {
        border-color: #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .badge-urgent {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/bill.png", width=60)
    st.title("Invoice Flow AI")
    st.caption("AI-Powered Receivables & Reminders")
    st.divider()

    st.markdown("**Navigation Pages:**")
    st.markdown("1. 📊 **Executive Dashboard**")
    st.markdown("2. 📄 **Track Invoices**")
    st.markdown("3. 🤖 **ML Late Payer Predictor**")
    st.markdown("4. 💬 **Smart Reminder Drafter**")
    st.markdown("5. 👥 **Customer Directory**")
    st.markdown("6. 🎓 **Novice Guide (Learn Step-by-Step)**")
    st.divider()

    # System Quick Stats
    all_invoices = database.get_all_invoices()
    overdue_count = sum(1 for i in all_invoices if i["status"] == "Overdue")
    pending_count = sum(1 for i in all_invoices if i["status"] == "Pending")
    
    st.caption(f"⚡ **Quick Status:**")
    st.caption(f"• Overdue Invoices: **{overdue_count}**")
    st.caption(f"• Pending Invoices: **{pending_count}**")
    st.caption(f"• System Date: **{datetime.date.today()}**")

# Hero Section
st.markdown('<div class="main-header">💼 Invoice & Payment-Reminder Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automate accounts receivable, forecast cash-flow risks with Machine Learning, and draft polite, high-converting WhatsApp & Email reminders.</div>', unsafe_allow_html=True)

# Top KPI Metric Cards
col1, col2, col3, col4 = st.columns(4)

total_outstanding = sum(i["amount"] for i in all_invoices if i["status"] in ("Pending", "Overdue"))
total_overdue = sum(i["amount"] for i in all_invoices if i["status"] == "Overdue")
total_paid = sum(i["amount"] for i in all_invoices if i["status"] == "Paid")
active_clients = len(database.get_all_customers())

with col1:
    st.metric("Total Outstanding", f"${total_outstanding:,.2f}", delta=f"{len([i for i in all_invoices if i['status'] != 'Paid'])} open invoices")

with col2:
    st.metric("Overdue Balance", f"${total_overdue:,.2f}", delta=f"{overdue_count} invoices", delta_color="inverse")

with col3:
    st.metric("Collected Revenue", f"${total_paid:,.2f}", delta="Historical total")

with col4:
    st.metric("Active Clients", f"{active_clients}", delta="In database")

st.markdown("---")

# Feature Tour for the Novice User
st.subheader("🧭 What would you like to do?")

fcol1, fcol2, fcol3 = st.columns(3)

with fcol1:
    st.markdown("""
    ### 📊 1. Receivables Dashboard
    Monitor business cash-flow, invoice aging buckets (0-15d, 16-30d, 30d+), and collection trends.
    
    👉 *Go to **Dashboard** in the sidebar.*
    """)

with fcol2:
    st.markdown("""
    ### 🤖 2. ML Late Payer Predictor
    Use our trained Scikit-Learn model to automatically scan pending invoices and flag high-risk late payers before they become overdue.
    
    👉 *Go to **Late Payment Predictor**.*
    """)

with fcol3:
    st.markdown("""
    ### 💬 3. Smart Reminders
    Generate ready-to-send polite WhatsApp and Email messages in 4 adjustable tones, with 1-click launch links.
    
    👉 *Go to **Smart Reminders**.*
    """)

st.markdown("---")

# Quick Action Center: High Priority Invoices Needing Attention
st.subheader("⚡ Action Center: High-Priority Invoices")
st.caption("These invoices are either already overdue or flagged by our ML model as high risk of late payment.")

priority_invoices = []
for inv in all_invoices:
    if inv["status"] in ("Pending", "Overdue"):
        risk = ml_model.predict_invoice_risk(inv["customer_id"], inv["amount"], inv["term_days"])
        if inv["status"] == "Overdue" or risk["risk_level"] == "High":
            priority_invoices.append({
                "Invoice #": inv["invoice_number"],
                "Customer": f"{inv['customer_name']} ({inv['customer_company']})",
                "Amount": f"${inv['amount']:,.2f}",
                "Due Date": inv["due_date"],
                "Status": "⚠️ Overdue" if inv["status"] == "Overdue" else "⏳ Pending",
                "ML Risk Score": f"{risk['risk_probability']}% ({risk['risk_level']})",
                "Recommended Action": risk["recommended_action"]
            })

if priority_invoices:
    st.dataframe(priority_invoices, use_container_width=True)
else:
    st.success("🎉 All caught up! No urgent overdue or high-risk invoices currently.")

# Beginner learning note
with st.expander("💡 Novice Tip: How this application is structured"):
    st.markdown("""
    This app is built as a **modular multi-page application**:
    - **`database.py`**: SQLite database storing customers, invoices, and completed payment logs.
    - **`ml_model.py`**: A Machine Learning Random Forest classifier that learns each customer's past payment delays and predicts future risks.
    - **`reminder_engine.py`**: Generates tone-adjusted WhatsApp (`wa.me`) and Email (`mailto:`) links so you can send reminders with a single click.
    - **`pages/`**: Each page in the sidebar is an independent module dedicated to a specific part of your workflow.
    - Check out the **🎓 Novice Guide** page in the sidebar for an in-depth breakdown of how everything works!
    """)
