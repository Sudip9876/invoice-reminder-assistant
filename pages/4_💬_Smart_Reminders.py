"""
pages/4_💬_Smart_Reminders.py - Multi-Tone WhatsApp & Email Reminder Drafter with CRM Logger (INR)
Generates high-converting, relationship-preserving payment reminders with UPI / Bank transfer details,
1-click deep links, and automated CRM communication history logging.
"""

import streamlit as st
from datetime import date, timedelta
import database
import ml_model
import reminder_engine

st.set_page_config(page_title="Smart Reminders & CRM (INR)", page_icon="💬", layout="wide")

database.init_db()
database.refresh_invoice_statuses()

st.title("💬 Smart Payment Reminders & CRM Log (INR)")
st.caption("Draft polite, tone-calibrated WhatsApp messages and formal emails featuring UPI / Bank details, and automatically log outreach in the CRM.")

all_invoices = database.get_all_invoices()
unpaid_invoices = [i for i in all_invoices if i["status"] in ("Pending", "Overdue")]

if not unpaid_invoices:
    st.info("ℹ️ No unpaid invoices available right now. Create an invoice or click '🇮🇳 Load Demo' in the sidebar.")
    st.stop()

inv_options = {
    f"{inv['invoice_number']} — {inv['customer_company']} ({database.format_inr(inv['amount'])}) [{'⚠️ OVERDUE' if inv['status'] == 'Overdue' else 'Pending'}]": inv["id"]
    for inv in unpaid_invoices
}

col_select, col_tone = st.columns([1.5, 1])

with col_select:
    selected_label = st.selectbox("Select Invoice to Follow Up:", list(inv_options.keys()))
    selected_id = inv_options[selected_label]
    invoice = database.get_invoice_by_id(selected_id)

with col_tone:
    risk = ml_model.predict_invoice_risk(invoice["customer_id"], invoice["amount"], invoice["term_days"])
    if invoice["status"] == "Overdue":
        default_tone_idx = 2 if risk["risk_level"] == "High" else 1
    else:
        default_tone_idx = 0

    tones = ["Gentle / Friendly", "Professional / Standard", "Firm / Assertive", "Urgent / Final Notice"]
    selected_tone = st.selectbox(
        "Communication Tone:",
        tones,
        index=default_tone_idx,
        help="Choose the right degree of firmness. Maintain good relationships while getting paid."
    )

# ML Risk & Customer Context Banner
b_col1, b_col2, b_col3, b_col4 = st.columns(4)
b_col1.markdown(f"**Customer:** {invoice['customer_name']}")
b_col2.markdown(f"**Company:** {invoice['customer_company']}")
b_col3.markdown(f"**Due Date:** {invoice['due_date']} ({invoice['status']})")
b_col4.markdown(f"**ML Late Risk:** {risk['risk_badge']} ({risk['risk_probability']}%)")

st.markdown("---")

# Customization Options with Indian UPI & Bank Details
with st.expander("⚙️ Customize Sender, UPI & Banking Remittance Details", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        sender_name = st.text_input("Your Name / Department", value="Finance & Accounts")
        sender_company = st.text_input("Your Business Name", value="Bioron Technologies Pvt Ltd")
        payment_link = st.text_input("Online Payment Link (optional)", placeholder="e.g. https://rzp.io/l/inv001")
    with c2:
        upi_id = st.text_input("Business UPI ID (VPA)", value="bioron@okhdfcbank")
        bank_details = st.text_input("Bank NEFT/RTGS Details", value="HDFC Bank | A/C: 50200012345678 | IFSC: HDFC0000123")
    with c3:
        recipient_phone = st.text_input("WhatsApp Number (with country code)", value=invoice["customer_phone"])
        recipient_email = st.text_input("Recipient Email", value=invoice["customer_email"])
        custom_note = st.text_input("Custom Note (optional)", placeholder="e.g. TDS deducted at 2%")

invoice["customer_phone"] = recipient_phone
invoice["customer_email"] = recipient_email

# Generate reminder content
reminder = reminder_engine.generate_reminder_content(
    invoice=invoice,
    tone=selected_tone,
    sender_name=sender_name,
    sender_company=sender_company,
    upi_id=upi_id,
    bank_details=bank_details,
    payment_link=payment_link,
    custom_note=custom_note
)

# Output Channels Tabs
tab_wa, tab_email, tab_crm_action = st.tabs(["📱 WhatsApp Reminder", "✉️ Email Reminder", "🤝 Log to CRM Activity"])

with tab_wa:
    st.subheader("📱 WhatsApp Message Draft (₹ & UPI)")
    st.caption("Formatted with WhatsApp markdown (*bold*). Features your UPI ID and Bank account for immediate clearance.")

    st.markdown(f"""
    <div style="background-color: #E2F7CB; color: #111827; padding: 1.2rem; border-radius: 12px; max-width: 650px; font-family: sans-serif; white-space: pre-wrap; line-height: 1.5; border: 1px solid #C4E2A5; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
{reminder['whatsapp_text']}
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    w_btn_col1, w_btn_col2 = st.columns([1, 1.5])
    
    with w_btn_col1:
        if reminder["whatsapp_url"]:
            st.markdown(
                f'<a href="{reminder["whatsapp_url"]}" target="_blank" style="display: inline-block; background-color: #25D366; color: white; padding: 0.6rem 1.2rem; text-decoration: none; border-radius: 6px; font-weight: bold; text-align: center;">🟢 Open in WhatsApp Web / App</a>',
                unsafe_allow_html=True
            )
        else:
            st.warning("Please specify a valid phone number with country code.")

    with w_btn_col2:
        st.caption("💡 *Clicking 'Open in WhatsApp' launches WhatsApp with the message text already typed out for this contact!*")

    with st.expander("📋 Copy Raw WhatsApp Text"):
        st.code(reminder["whatsapp_text"], language="text")

with tab_email:
    st.subheader("✉️ Formal Tax Invoice Email Draft")
    st.caption("Complete subject line and structured email body with Indian remittance banking details.")

    st.markdown(f"**Subject:** `{reminder['email_subject']}`")
    
    st.text_area("Email Body:", value=reminder["email_body"], height=280)

    e_btn_col1, e_btn_col2 = st.columns([1, 1.5])

    with e_btn_col1:
        if reminder["mailto_url"]:
            st.markdown(
                f'<a href="{reminder["mailto_url"]}" target="_blank" style="display: inline-block; background-color: #3B82F6; color: white; padding: 0.6rem 1.2rem; text-decoration: none; border-radius: 6px; font-weight: bold; text-align: center;">✉️ Open in Email Client (Mailto)</a>',
                unsafe_allow_html=True
            )
        else:
            st.warning("Please specify a valid recipient email address.")

    with e_btn_col2:
        st.caption("💡 *Clicking 'Open in Email Client' opens your default mail application (Outlook, Apple Mail, etc.) with subject and body populated.*")

# TAB 3: CRM Interaction Logging
with tab_crm_action:
    st.subheader("📝 CRM Outreach & Payment Promise Tracker")
    st.caption("Keep your entire team aligned. Log this reminder or record a payment commitment from the customer.")

    with st.form("crm_log_form"):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            comm_type = st.selectbox("Interaction Channel", ["WhatsApp Reminder", "Email Reminder", "Phone Call", "Payment Promise Received", "In-Person / Meeting"])
            summary = st.text_area("Outreach Notes / Client Response", value=f"Sent {selected_tone} {comm_type} regarding invoice {invoice['invoice_number']} ({database.format_inr(invoice['amount'])}).")
        with col_c2:
            promised_date = st.date_input("Promised Settlement Date (if client committed)", value=date.today() + timedelta(days=5))
            has_promise = st.checkbox("Client gave a specific payment commitment date?", value=False)

        submit_crm = st.form_submit_button("💾 Save Activity to Customer CRM Timeline", type="primary")

        if submit_crm:
            p_date_str = str(promised_date) if has_promise else None
            database.add_crm_interaction(
                customer_id=invoice["customer_id"],
                invoice_id=invoice["id"],
                interaction_type=comm_type,
                summary=summary.strip(),
                tone=selected_tone,
                promised_payment_date=p_date_str
            )
            st.success(f"Activity successfully logged to **{invoice['customer_company']}** CRM profile!")
