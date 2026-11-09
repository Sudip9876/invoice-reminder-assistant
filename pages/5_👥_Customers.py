"""
pages/5_👥_Customers.py - Customer Directory & Payment Reliability Profiles
View client credit reliability, average payment delays, and manage customer contact info.
"""

import streamlit as st
import pandas as pd
import database
import ml_model

st.set_page_config(page_title="Customer Directory", page_icon="👥", layout="wide")

database.init_db()

st.title("👥 Customer Directory & Reliability Scorecards")
st.caption("Track payment habits, customer reliability ratings, and manage client contact profiles.")

tab_list, tab_add = st.tabs(["📋 Client Profiles & Reliability", "➕ Add New Customer"])

with tab_list:
    customers = database.get_all_customers()
    if not customers:
        st.info("No customers found. Please add a customer in the next tab.")
        st.stop()

    client_cards = []
    for c in customers:
        stats = database.get_customer_stats(c["id"])
        
        # Calculate Reliability Rating
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

        client_cards.append({
            "id": c["id"],
            "name": c["name"],
            "company": c["company"],
            "email": c["email"],
            "phone": c["phone"],
            "total_invoices": stats["total_invoices"],
            "late_count": stats["late_count"],
            "on_time_count": stats["on_time_count"],
            "avg_delay": stats["avg_delay"],
            "late_rate": stats["late_rate"],
            "rating": rating,
            "rating_color": rating_color
        })

    # Display as rich customer cards
    for client in client_cards:
        with st.container():
            st.markdown(f"""
            <div style="border-left: 5px solid {client['rating_color']}; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.2rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: #0F172A;">{client['company']}</h4>
                        <span style="color: #64748B; font-size: 0.95rem;">Contact: {client['name']} &nbsp;|&nbsp; ✉️ {client['email']} &nbsp;|&nbsp; 📱 {client['phone']}</span>
                    </div>
                    <div>
                        <span style="font-weight: bold; color: {client['rating_color']}; font-size: 1rem;">{client['rating']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Historical Invoices", f"{client['total_invoices']}")
            c2.metric("On-Time Settlements", f"{client['on_time_count']}")
            c3.metric("Late Settlements", f"{client['late_count']}", delta_color="inverse")
            
            delay_str = f"+{client['avg_delay']:.0f} days" if client['avg_delay'] > 0 else f"{client['avg_delay']:.0f} days"
            c4.metric("Avg Payment Delay", delay_str, delta_color="inverse" if client['avg_delay'] > 0 else "normal")
            
            st.markdown("---")

    # Client Payment History Drilldown
    st.subheader("🔍 Client Payment History Drilldown")
    client_choices = {f"{c['company']} ({c['name']})": c["id"] for c in customers}
    selected_client_label = st.selectbox("Select Client to inspect payment log:", list(client_choices.keys()))
    selected_client_id = client_choices[selected_client_label]

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
        history_df["amount"] = history_df["amount"].map("${:,.2f}".format)
        history_df.columns = ["Amount", "Terms (Days)", "Due Date", "Paid Date", "Delay (Days)", "Status"]
        st.dataframe(history_df, use_container_width=True, hide_index=True)
    else:
        st.info("No recorded payment history yet for this client.")

with tab_add:
    st.subheader("➕ Register a New Business Customer")
    st.caption("Add a client contact. Enter the phone with country code (e.g., +1415... or +9198...) so one-click WhatsApp reminders work seamlessly.")

    with st.form("new_customer_form"):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            name = st.text_input("Contact Person Name", placeholder="e.g. John Doe")
            company = st.text_input("Company / Business Name", placeholder="e.g. Acme Innovations")
        with col_c2:
            email = st.text_input("Email Address", placeholder="e.g. billing@acme.com")
            phone = st.text_input("WhatsApp Phone (with country code)", placeholder="e.g. +14155552671 or +919876543210")

        submitted = st.form_submit_button("💾 Save Customer", type="primary")

        if submitted:
            if not name.strip() or not company.strip() or not email.strip() or not phone.strip():
                st.error("Please fill in all fields (Name, Company, Email, Phone).")
            else:
                new_id = database.add_customer(name, company, email, phone)
                st.success(f"Customer **{company}** ({name}) added successfully!")
                st.rerun()
