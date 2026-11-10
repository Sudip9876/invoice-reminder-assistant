"""
app.py - Invoice & Payment-Reminder Assistant (INR & CRM Edition)
Main entrypoint and navigation hub for small business cash-flow, CRM follow-ups & payment tracking.
"""

import streamlit as st
import datetime
import database
import ml_model

# Page configuration
st.set_page_config(
    page_title="Invoice & Payment-Reminder Assistant (INR)",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database schema
database.init_db()
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
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/bill.png", width=60)
    st.title("Invoice Flow AI (₹)")
    st.caption("AI Invoicing, CRM Follow-ups & Reminders")
    st.divider()

    st.markdown("**Navigation Pages:**")
    st.markdown("1. 📊 **Executive Dashboard**")
    st.markdown("2. 📄 **Track Invoices**")
    st.markdown("3. 🤖 **ML Late Payer Predictor**")
    st.markdown("4. 💬 **Smart Reminders & CRM Log**")
    st.markdown("5. 👥 **Customer CRM & Scorecards**")
    st.markdown("6. 🎓 **Novice Guide (Learn Step-by-Step)**")
    st.divider()

    # System Quick Stats
    all_invoices = database.get_all_invoices()
    overdue_count = sum(1 for i in all_invoices if i["status"] == "Overdue")
    pending_count = sum(1 for i in all_invoices if i["status"] == "Pending")
    crm_logs = database.get_crm_interactions()
    
    st.caption("⚡ **Live Status:**")
    st.caption(f"• Currency: **INR (₹)**")
    st.caption(f"• Overdue Invoices: **{overdue_count}**")
    st.caption(f"• Pending Invoices: **{pending_count}**")
    st.caption(f"• CRM Interactions: **{len(crm_logs)} logged**")
    st.divider()

    # Database Demo Data Management (User requested feature!)
    st.markdown("🛠️ **Data Management:**")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        if st.button("🧹 Clear All", help="Wipes all invoices and demo records to start with a blank database"):
            database.clear_all_data()
            st.success("Database wiped clean!")
            st.rerun()
    with col_d2:
        if st.button("🇮🇳 Load Demo", help="Populates realistic Indian SME records in INR"):
            database.seed_indian_demo_data()
            ml_model.train_model()
            st.success("Loaded Indian demo data in INR!")
            st.rerun()

# Hero Section
st.markdown('<div class="main-header">💼 Invoice & Payment-Reminder Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automate accounts receivable, manage CRM communication logs, forecast late-payer risks with Machine Learning, and draft polite WhatsApp & Email reminders in Indian Rupees (₹).</div>', unsafe_allow_html=True)

# Top KPI Metric Cards
col1, col2, col3, col4 = st.columns(4)

total_outstanding = sum(i["amount"] for i in all_invoices if i["status"] in ("Pending", "Overdue"))
total_overdue = sum(i["amount"] for i in all_invoices if i["status"] == "Overdue")
total_paid = sum(i["amount"] for i in all_invoices if i["status"] == "Paid")
active_clients = len(database.get_all_customers())

with col1:
    st.metric("Total Outstanding", database.format_inr(total_outstanding), delta=f"{len([i for i in all_invoices if i['status'] != 'Paid'])} open invoices")

with col2:
    st.metric("Overdue Balance", database.format_inr(total_overdue), delta=f"{overdue_count} overdue", delta_color="inverse")

with col3:
    st.metric("Collected Revenue", database.format_inr(total_paid), delta="Realized in bank")

with col4:
    st.metric("Active Clients", f"{active_clients}", delta=f"{len(crm_logs)} CRM notes logged")

st.markdown("---")

# Feature Tour for Novice User
st.subheader("🧭 Core System Capabilities")

fcol1, fcol2, fcol3 = st.columns(3)

with fcol1:
    st.markdown("""
    ### 📊 1. Receivables Dashboard
    Monitor business cash flow, aging buckets (0-15d, 16-30d, 30d+), and collection trends in Indian Rupees.
    
    👉 *Go to **Dashboard** in the sidebar.*
    """)

with fcol2:
    st.markdown("""
    ### 🤖 2. ML Late Payer Predictor
    Use our Scikit-Learn Random Forest model to automatically scan pending invoices and flag likely payment delays before the due date.
    
    👉 *Go to **Late Payment Predictor**.*
    """)

with fcol3:
    st.markdown("""
    ### 💬 3. Smart Reminders & CRM
    Generate polite WhatsApp & Email reminders featuring your **UPI ID & Bank NEFT/RTGS details**, and log follow-ups to the CRM timeline.
    
    👉 *Go to **Smart Reminders**.*
    """)

st.markdown("---")

# Quick Action Center: High Priority Invoices Needing Attention
st.subheader("⚡ Action Center: High-Priority Invoices (INR)")
st.caption("Active invoices that are either already overdue or flagged by our ML model as high risk of late payment.")

priority_invoices = []
for inv in all_invoices:
    if inv["status"] in ("Pending", "Overdue"):
        risk = ml_model.predict_invoice_risk(inv["customer_id"], inv["amount"], inv["term_days"])
        if inv["status"] == "Overdue" or risk["risk_level"] == "High":
            priority_invoices.append({
                "Invoice #": inv["invoice_number"],
                "Customer": f"{inv['customer_name']} ({inv['customer_company']})",
                "Amount": database.format_inr(inv["amount"]),
                "Due Date": inv["due_date"],
                "Status": "⚠️ Overdue" if inv["status"] == "Overdue" else "⏳ Pending",
                "ML Risk Score": f"{risk['risk_probability']}% ({risk['risk_level']})",
                "Recommended Action": risk["recommended_action"]
            })

if priority_invoices:
    st.dataframe(priority_invoices, width='stretch')
else:
    st.success("🎉 All caught up! No urgent overdue or high-risk invoices currently.")

# Beginner learning note
with st.expander("💡 Novice Tip: Managing Demo Data & Indian Rupee Context"):
    st.markdown("""
    - **Clean Slate**: Use the **'🧹 Clear All'** button in the sidebar anytime you want to wipe all demo records and start inputting your own real invoices and clients.
    - **Demo Sample**: Click **'🇮🇳 Load Demo'** to instantly repopulate realistic Indian SME clients with amounts in INR (₹), GSTINs, and UPI IDs for client presentations or portfolio testing.
    - **Indian Compliance & CRM**: Invoices, customer profiles, and reminder drafts are calibrated for Indian businesses, with support for **GSTIN**, **UPI ID**, **Bank IFSC/RTGS**, and **Credit Limits**.
    """)
