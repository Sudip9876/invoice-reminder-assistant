"""
pages/4_💬_Smart_Reminders.py - Multi-Tone WhatsApp & Email Reminder Drafter
Generates high-converting, relationship-preserving payment reminders with 1-click launch links.
"""

import streamlit as st
import database
import ml_model
import reminder_engine

st.set_page_config(page_title="Smart Reminders", page_icon="💬", layout="wide")

database.init_db()
database.refresh_invoice_statuses()

st.title("💬 Smart Payment Reminder Drafter")
st.caption("Draft polite, tone-calibrated WhatsApp messages and formal emails tailored to client risk and overdue status.")

# Load Invoices
all_invoices = database.get_all_invoices()
unpaid_invoices = [i for i in all_invoices if i["status"] in ("Pending", "Overdue")]

if not unpaid_invoices:
    st.success("All invoices are paid! No reminders needed right now.")
    st.stop()

# Invoice Selection
inv_options = {
    f"{inv['invoice_number']} — {inv['customer_company']} (${inv['amount']:,.2f}) [{'⚠️ OVERDUE' if inv['status'] == 'Overdue' else 'Pending'}]": inv["id"]
    for inv in unpaid_invoices
}

col_select, col_tone = st.columns([1.5, 1])

with col_select:
    selected_label = st.selectbox("Select Invoice to Follow Up:", list(inv_options.keys()))
    selected_id = inv_options[selected_label]
    invoice = database.get_invoice_by_id(selected_id)

with col_tone:
    # Auto-recommend tone based on overdue status and ML risk!
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

# Customization Options
with st.expander("⚙️ Customize Sender & Payment Details", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        sender_name = st.text_input("Your Name / Department", value="Accounts Receivable")
        sender_company = st.text_input("Your Business Name", value="Our Business Solutions")
    with c2:
        payment_link = st.text_input("Payment Link / UPI / Bank URL", value=f"https://pay.example.com/invoice/{invoice['invoice_number']}")
        recipient_phone = st.text_input("WhatsApp Number (with country code)", value=invoice["customer_phone"])
    with c3:
        recipient_email = st.text_input("Recipient Email", value=invoice["customer_email"])
        custom_note = st.text_input("Special Note (optional)", placeholder="e.g. 5% discount if settled today")

# Update invoice dict with any custom phone/email inputs
invoice["customer_phone"] = recipient_phone
invoice["customer_email"] = recipient_email

# Generate reminder content
reminder = reminder_engine.generate_reminder_content(
    invoice=invoice,
    tone=selected_tone,
    sender_name=sender_name,
    sender_company=sender_company,
    payment_link=payment_link,
    custom_note=custom_note
)

# Output Channels Tabs
tab_wa, tab_email = st.tabs(["📱 WhatsApp Reminder", "✉️ Email Reminder"])

with tab_wa:
    st.subheader("📱 WhatsApp Message Draft")
    st.caption("Formatted with WhatsApp markdown (*bold*). Ready to send in 1 click.")

    # WhatsApp Chat bubble preview
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
        st.caption("💡 *Clicking 'Open in WhatsApp' opens WhatsApp with the message text already typed out for this contact!*")

    with st.expander("📋 Copy Raw WhatsApp Text"):
        st.code(reminder["whatsapp_text"], language="text")

with tab_email:
    st.subheader("✉️ Formal Email Draft")
    st.caption("Complete subject line and structured email body.")

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

st.markdown("---")

# Strategy Guide for Small Businesses
with st.expander("💡 Small Business Collections Strategy Guide"):
    st.markdown("""
    ### Best Practices for Getting Invoices Paid Faster
    1. **Pre-Due Gentle Reminder (-3 Days):** Send a friendly note 3 days before the due date for high-risk accounts.
    2. **Due Date Note (Day 0):** A short professional message checking if any purchase order or invoice details are needed.
    3. **First Overdue Notice (+5 Days):** Firm and direct. Acknowledge that payments occasionally get held up, but request a specific clearance date.
    4. **WhatsApp vs Email:** 
       - Email is best for enterprise audit trails and official finance records.
       - WhatsApp has a **98% open rate** within 10 minutes—ideal for quick confirmation and reaching decision makers directly!
    """)
