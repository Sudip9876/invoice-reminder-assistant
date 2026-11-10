"""
pages/2_📄_Invoices.py - Invoice Management, Creation & Settlement (INR)
Track all accounts receivable, record customer payments, and create new invoices in Indian Rupees (₹).
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

import database
import ml_model

st.set_page_config(page_title="Track Invoices (INR)", page_icon="📄", layout="wide")

database.init_db()
database.refresh_invoice_statuses()

st.title("📄 Invoice Management & Tracking (INR)")
st.caption("Manage all issued invoices, mark payments as received, and create new invoices in Indian Rupees (₹).")

tab1, tab2 = st.tabs(["📋 All Invoices", "➕ Create New Invoice"])

with tab1:
    invoices = database.get_all_invoices()

    if not invoices:
        st.info("ℹ️ No invoices currently recorded in the database. Use the 'Create New Invoice' tab or click '🇮🇳 Load Demo' in the sidebar.")
        st.stop()

    col_search, col_status, col_risk = st.columns([2, 1, 1])

    with col_search:
        search_query = st.text_input("🔍 Search by Invoice #, Customer, or Company", placeholder="e.g. INV-2026 or Apex")

    with col_status:
        status_filter = st.selectbox("Status Filter", ["All", "Pending", "Overdue", "Paid"])

    with col_risk:
        risk_filter = st.selectbox("Risk Filter", ["All", "High Risk", "Medium Risk", "Low Risk"])

    rows = []
    for inv in invoices:
        risk = ml_model.predict_invoice_risk(inv["customer_id"], inv["amount"], inv["term_days"])
        rows.append({
            "id": inv["id"],
            "invoice_number": inv["invoice_number"],
            "customer_id": inv["customer_id"],
            "customer_name": inv["customer_name"],
            "company": inv["customer_company"],
            "amount": inv["amount"],
            "formatted_amount": database.format_inr(inv["amount"]),
            "issue_date": inv["issue_date"],
            "due_date": inv["due_date"],
            "term_days": inv["term_days"],
            "status": inv["status"],
            "paid_date": inv["paid_date"] or "-",
            "notes": inv["notes"] or "",
            "risk_level": risk["risk_level"],
            "risk_prob": risk["risk_probability"],
            "risk_badge": risk["risk_badge"] if inv["status"] != "Paid" else "✅ Paid"
        })

    df = pd.DataFrame(rows)

    if search_query:
        q = search_query.lower()
        df = df[df["invoice_number"].str.lower().str.contains(q) | 
                df["customer_name"].str.lower().str.contains(q) | 
                df["company"].str.lower().str.contains(q)]

    if status_filter != "All":
        df = df[df["status"] == status_filter]

    if risk_filter != "All":
        target_risk = risk_filter.replace(" Risk", "")
        df = df[df["risk_level"] == target_risk]

    st.markdown(f"**Showing {len(df)} invoices**")

    display_df = df[[
        "invoice_number", "customer_name", "company", "formatted_amount", "issue_date", "due_date", "status", "risk_badge", "paid_date", "notes"
    ]].copy()

    display_df.columns = ["Invoice #", "Client Name", "Company", "Amount (₹)", "Issued", "Due Date", "Status", "ML Risk", "Paid Date", "Notes"]

    st.dataframe(display_df, width="stretch", hide_index=True)

    st.markdown("---")
    act_col1, act_col2 = st.columns([1.5, 1])

    with act_col1:
        st.subheader("💳 Record Payment (Mark as Paid)")
        st.caption("When a payment is marked as paid, the assistant automatically records the delay in payment history, allowing the ML model to continuously learn.")

        unpaid_invoices = [inv for inv in invoices if inv["status"] in ("Pending", "Overdue")]
        if unpaid_invoices:
            inv_choices = {f"{inv['invoice_number']} - {inv['customer_company']} ({database.format_inr(inv['amount'])})": inv["id"] for inv in unpaid_invoices}
            selected_inv_label = st.selectbox("Select invoice to mark as paid:", list(inv_choices.keys()))
            selected_inv_id = inv_choices[selected_inv_label]

            p_col1, p_col2 = st.columns(2)
            with p_col1:
                payment_date = st.date_input("Settlement Date", value=date.today())
            with p_col2:
                st.write("")
                st.write("")
                if st.button("✅ Confirm Payment Received", type="primary"):
                    database.mark_invoice_as_paid(selected_inv_id, str(payment_date))
                    st.success(f"Invoice marked as Paid on {payment_date}! Payment history & CRM updated for ML model.")
                    st.rerun()
        else:
            st.info("No unpaid invoices available to mark as paid.")

    with act_col2:
        st.subheader("📥 Export Invoices")
        st.caption("Download the current invoice roster for accounting, GST filing, or spreadsheet analysis.")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download Invoices as CSV",
            data=csv,
            file_name=f"invoices_inr_export_{date.today()}.csv",
            mime="text/csv",
        )

with tab2:
    st.subheader("➕ Create a New Tax Invoice (₹)")
    st.caption("Issue an invoice to a customer. The ML model will instantly assess the risk level based on the customer's prior track record.")

    customers = database.get_all_customers()
    if not customers:
        st.warning("Please add at least one customer in the 'Customer CRM' page before creating an invoice.")
    else:
        cust_map = {f"{c['name']} ({c['company']})": c["id"] for c in customers}

        with st.form("new_invoice_form"):
            c1, c2 = st.columns(2)
            with c1:
                selected_cust = st.selectbox("Select Customer", list(cust_map.keys()))
                cust_id = cust_map[selected_cust]
                
                existing_invoices = database.get_all_invoices()
                next_num = f"INV-2026-{len(existing_invoices) + 1:03d}"
                invoice_num = st.text_input("Invoice Number", value=next_num)
                amount = st.number_input("Invoice Total in INR (₹)", min_value=100.0, value=75000.0, step=5000.0)

            with c2:
                issue_d = st.date_input("Issue Date", value=date.today())
                term_options = [15, 30, 45, 60]
                terms = st.selectbox("Payment Terms (Net Days)", term_options, index=1)
                due_d = issue_d + timedelta(days=terms)
                st.info(f"Calculated Due Date: **{due_d}** (Net {terms})")
                notes = st.text_input("Description / Services Rendered", placeholder="e.g. Monthly SEO Retainer, Cloud Consulting")

            submit_btn = st.form_submit_button("💾 Issue & Save Invoice", type="primary")

            if submit_btn:
                if not invoice_num.strip():
                    st.error("Invoice number cannot be empty.")
                else:
                    new_id = database.add_invoice(
                        invoice_number=invoice_num.strip(),
                        customer_id=cust_id,
                        issue_date=str(issue_d),
                        due_date=str(due_d),
                        amount=float(amount),
                        notes=notes.strip()
                    )
                    st.success(f"Invoice **{invoice_num}** ({database.format_inr(amount)}) successfully created!")

                    risk = ml_model.predict_invoice_risk(cust_id, float(amount), terms)
                    st.markdown(f"**⚡ Initial ML Risk Assessment:** {risk['risk_badge']} ({risk['risk_probability']}% probability of late payment)")
                    st.caption(f"Recommendation: {risk['recommended_action']}")
