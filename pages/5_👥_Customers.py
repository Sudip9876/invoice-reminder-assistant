"""
pages/5_👥_Customers.py - Customer Directory, CRM Profiles & Credit Limits (INR)
View client credit reliability, GSTIN details, credit limit utilization, and complete CRM interaction history.
"""

import streamlit as st
import pandas as pd
from datetime import date
import database
import ml_model

st.set_page_config(page_title="Customer CRM Profiles (INR)", page_icon="👥", layout="wide")

database.init_db()

st.title("👥 Customer CRM Directory & Credit Scorecards (INR)")
st.caption("Manage customer profiles, Indian GSTINs, credit limit utilization, and audit complete CRM communication timelines.")

tab_list, tab_add, tab_crm_timeline = st.tabs(["📋 Client Profiles & Credit Limits", "➕ Add New Business Customer", "📞 Full CRM Activity Log"])

with tab_list:
    customers = database.get_all_customers()
    if not customers:
        st.info("ℹ️ No customers found in the database. Add a customer in the 'Add New Customer' tab, or click **'🇮🇳 Load Demo'** in the sidebar.")
        st.stop()

    client_cards = []
    for c in customers:
        stats = database.get_customer_stats(c["id"])
        
        if not stats["has_history"]:
            rating = "🆕 New Client (No data)"
            rating_color = "#64748B"
        elif stats["late_rate"] == 0.0:
            rating = "⭐ ⭐ ⭐ ⭐ ⭐ Perfect Payer"
            rating_color = "#10B981"
        elif stats["late_rate"] < 0.35:
            rating = "⭐ ⭐ ⭐ ⭐ Reliable"
            rating_color = "#3B82F6"
        elif stats["late_rate"] < 0.70:
            rating = "⭐ ⭐ ⭐ Occasional Delays"
            rating_color = "#F59E0B"
        else:
            rating = "⚠️ Chronic Late Payer"
            rating_color = "#EF4444"

        credit_limit = c.get("credit_limit") or 150000.0
        outstanding = stats.get("outstanding") or 0.0
        utilization = min(100.0, (outstanding / credit_limit * 100)) if credit_limit > 0 else 0.0

        client_cards.append({
            "id": c["id"],
            "name": c["name"],
            "company": c["company"],
            "email": c["email"],
            "phone": c["phone"],
            "gstin": c.get("gstin") or "Not Registered",
            "credit_limit": credit_limit,
            "outstanding": outstanding,
            "utilization": utilization,
            "tags": c.get("tags") or "Active",
            "total_invoices": stats["total_invoices"],
            "late_count": stats["late_count"],
            "on_time_count": stats["on_time_count"],
            "avg_delay": stats["avg_delay"],
            "rating": rating,
            "rating_color": rating_color
        })

    # Render Client Cards
    for client in client_cards:
        with st.container():
            st.markdown(f"""
            <div style="border-left: 5px solid {client['rating_color']}; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.2rem; margin-bottom: 0.8rem; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: #0F172A;">{client['company']}</h4>
                        <span style="color: #64748B; font-size: 0.95rem;">
                            Contact: <strong>{client['name']}</strong> &nbsp;|&nbsp; ✉️ {client['email']} &nbsp;|&nbsp; 📱 {client['phone']}
                        </span><br>
                        <span style="font-size: 0.85rem; color: #475569;">
                            GSTIN: <code>{client['gstin']}</code> &nbsp;|&nbsp; Tags: <strong>{client['tags']}</strong>
                        </span>
                    </div>
                    <div>
                        <span style="font-weight: bold; color: {client['rating_color']}; font-size: 1rem;">{client['rating']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Credit Limit", database.format_inr(client['credit_limit']))
            c2.metric("Current Outstanding", database.format_inr(client['outstanding']), delta=f"{client['utilization']:.0f}% utilized", delta_color="inverse" if client['utilization'] > 75 else "normal")
            c3.metric("On-Time / Late", f"{client['on_time_count']} / {client['late_count']}")
            delay_str = f"+{client['avg_delay']:.0f} days" if client['avg_delay'] > 0 else f"{client['avg_delay']:.0f} days"
            c4.metric("Avg Payment Delay", delay_str, delta_color="inverse" if client['avg_delay'] > 0 else "normal")
            
            # Credit utilization progress bar
            st.progress(client['utilization'] / 100.0)
            st.markdown("---")

    # Client Payment History & CRM Drilldown
    st.subheader("🔍 Client Detail Drilldown (Ledger & CRM Timeline)")
    client_choices = {f"{c['company']} ({c['name']})": c["id"] for c in customers}
    selected_client_label = st.selectbox("Select Client to inspect:", list(client_choices.keys()))
    selected_client_id = client_choices[selected_client_label]

    subtab1, subtab2 = st.tabs(["💳 Payment Settlement Ledger", "💬 CRM Interaction History"])

    with subtab1:
        conn = database.get_connection()
        history_df = pd.read_sql_query("""
            SELECT 
                amount,
                term_days as terms,
                due_date,
                paid_date,
                delay_days,
                CASE WHEN was_late = 1 THEN '⚠️ Late' ELSE '✅ On-Time' END as payment_status
            FROM payment_history
            WHERE customer_id = ?
            ORDER BY id DESC
        """, conn, params=(selected_client_id,))
        conn.close()

        if not history_df.empty:
            history_df["amount"] = history_df["amount"].apply(database.format_inr)
            history_df.columns = ["Amount (₹)", "Terms (Days)", "Due Date", "Paid Date", "Delay (Days)", "Status"]
            st.dataframe(history_df, width="stretch", hide_index=True)
        else:
            st.info("No recorded payment history yet for this client.")

    with subtab2:
        interactions = database.get_crm_interactions(customer_id=selected_client_id)
        if interactions:
            for item in interactions:
                p_date_badge = f" | 🗓️ <strong>Payment Promised For:</strong> {item['promised_payment_date']}" if item.get("promised_payment_date") else ""
                st.markdown(f"""
                <div style="background: #F8FAFC; border-left: 4px solid #6366F1; padding: 0.8rem 1rem; border-radius: 6px; margin-bottom: 0.6rem;">
                    <strong>{item['interaction_type']}</strong> — <span style="color: #64748B;">{item['interaction_date']}</span> {p_date_badge}<br>
                    <span style="color: #1E293B;">{item['summary']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No CRM interactions logged for this customer yet. Use 'Smart Reminders' to log WhatsApp or email outreach.")

with tab_add:
    st.subheader("➕ Register a New Business Customer & CRM Profile (₹)")
    st.caption("Add a client contact with GSTIN, credit limits, and Indian banking details.")

    with st.form("new_customer_form"):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            name = st.text_input("Contact Person Name", placeholder="e.g. Rajesh Sharma")
            company = st.text_input("Company / Business Legal Name", placeholder="e.g. Apex Tech Solutions LLP")
            email = st.text_input("Email Address", placeholder="e.g. accounts@apextech.in")
            phone = st.text_input("WhatsApp Phone (with +91 country code)", placeholder="e.g. +919876543210")
            gstin = st.text_input("GSTIN Number (optional)", placeholder="e.g. 27AAACA1234F1Z1")

        with col_c2:
            credit_limit = st.number_input("Approved Credit Limit in INR (₹)", min_value=10000.0, value=200000.0, step=25000.0)
            payment_terms = st.selectbox("Default Payment Terms (Net Days)", [15, 30, 45, 60], index=1)
            upi_id = st.text_input("Customer UPI ID (optional)", placeholder="e.g. apex@okhdfcbank")
            bank_details = st.text_input("Bank Details (optional)", placeholder="e.g. HDFC Bank | A/C: 5020... | IFSC: HDFC0000...")
            tags = st.text_input("CRM Tags", value="Active, Retainer", placeholder="e.g. VIP, Advance-Only, Slow Payer")

        submitted = st.form_submit_button("💾 Save Customer to CRM", type="primary")

        if submitted:
            if not name.strip() or not company.strip() or not email.strip() or not phone.strip():
                st.error("Please fill in all required fields (Name, Company, Email, Phone).")
            else:
                new_id = database.add_customer(
                    name=name,
                    company=company,
                    email=email,
                    phone=phone,
                    gstin=gstin,
                    credit_limit=credit_limit,
                    payment_terms=payment_terms,
                    upi_id=upi_id,
                    bank_details=bank_details,
                    tags=tags
                )
                st.success(f"Customer **{company}** ({name}) added successfully with {database.format_inr(credit_limit)} credit limit!")
                st.rerun()

with tab_crm_timeline:
    st.subheader("📞 Master CRM Outreach & Follow-up Timeline")
    st.caption("Complete company-wide communication log across all clients.")

    all_logs = database.get_crm_interactions()
    if all_logs:
        log_df = pd.DataFrame(all_logs)
        display_log = log_df[["interaction_date", "customer_company", "interaction_type", "summary", "promised_payment_date"]].copy()
        display_log.columns = ["Date", "Client Company", "Channel", "Notes", "Promised Date"]
        st.dataframe(display_log, width="stretch", hide_index=True)
    else:
        st.info("No communication logged yet. Log reminders and calls from the 'Smart Reminders' page.")
