"""
reminder_engine.py - Smart Tone-Adjusted WhatsApp & Email Reminder Generator (INR & UPI Support)
Generates high-converting, polite payment reminders featuring UPI ID, Bank NEFT/RTGS details,
and 1-click WhatsApp (wa.me) & Email (mailto) deep links.
"""

import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional
from database import format_inr

TONE_DESCRIPTIONS = {
    "Gentle / Friendly": "Warm, appreciative tone. Best for upcoming invoices or 1-3 days past due.",
    "Professional / Standard": "Clear, objective business reminder. Best for due date or 3-7 days past due.",
    "Firm / Assertive": "Direct, structured follow-up. Best for 7-14 days overdue or chronic late payers.",
    "Urgent / Final Notice": "Formal notice emphasizing account hold or service suspension. Best for 15+ days overdue."
}

def clean_phone_number(phone: str) -> str:
    """Strips spaces, dashes, parentheses to leave numbers and optional leading +."""
    cleaned = "".join(c for c in phone if c.isdigit() or c == "+")
    if cleaned.startswith("+"):
        return cleaned[1:]  # wa.me format expects digits without leading +
    return cleaned

def generate_reminder_content(
    invoice: Dict[str, Any],
    tone: str = "Gentle / Friendly",
    sender_name: str = "Finance Team",
    sender_company: str = "Our Business",
    upi_id: str = "business@upi",
    bank_details: str = "HDFC Bank | A/C: 50200012345678 | IFSC: HDFC0000123",
    payment_link: str = "",
    custom_note: str = ""
) -> Dict[str, Any]:
    """
    Generates both WhatsApp and Email drafts calibrated for Indian business practices in INR (₹).
    """
    customer_name = invoice.get("customer_name", "Valued Client")
    company = invoice.get("customer_company", "")
    inv_num = invoice.get("invoice_number", "INV-000")
    amount = format_inr(invoice.get("amount", 0))
    due_date = invoice.get("due_date", "")
    recipient_email = invoice.get("customer_email", "")
    phone = clean_phone_number(invoice.get("customer_phone", ""))

    try:
        due_dt = datetime.strptime(due_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        diff = (today - due_dt).days
        if diff > 0:
            status_text = f"{diff} days overdue"
        elif diff == 0:
            status_text = "due today"
        else:
            status_text = f"due in {abs(diff)} days"
    except Exception:
        status_text = f"due on {due_date}"

    note_section = f"\n*Note:* {custom_note}" if custom_note.strip() else ""
    note_email = f"\nNote: {custom_note}\n" if custom_note.strip() else ""

    payment_info_wa = f"• *UPI ID:* {upi_id}\n• *Bank Transfer:* {bank_details}"
    if payment_link.strip():
        payment_info_wa += f"\n• *Pay Online:* {payment_link}"

    payment_info_email = (
        f"Settlement Options:\n"
        f"----------------------------------------\n"
        f"UPI ID:        {upi_id}\n"
        f"Bank Transfer: {bank_details}\n"
    )
    if payment_link.strip():
        payment_info_email += f"Online Portal: {payment_link}\n"
    payment_info_email += "----------------------------------------\n"

    # ==========================
    # WhatsApp Templates (Markdown *bold*)
    # ==========================
    if tone == "Gentle / Friendly":
        wa_text = (
            f"Hi {customer_name}! 😊 Hope you're having a wonderful week.\n\n"
            f"Just a gentle reminder regarding GST invoice *{inv_num}* for *{amount}*, which is {status_text} (Due: {due_date}).\n\n"
            f"*Payment Details:*\n{payment_info_wa}{note_section}\n\n"
            f"If you've already initiated the NEFT/IMPS/UPI transfer, kindly share the UTR receipt so we can update your ledger.\n\n"
            f"Warm regards,\n*{sender_name}* | {sender_company}"
        )
        email_subject = f"Friendly Reminder: Invoice {inv_num} ({amount}) from {sender_company}"
        email_body = (
            f"Dear {customer_name},\n\n"
            f"Greetings from {sender_company}.\n\n"
            f"This is a gentle reminder that tax invoice {inv_num} issued to {company} for {amount} is currently {status_text} (Due Date: {due_date}).\n\n"
            f"{payment_info_email}{note_email}\n"
            f"If payment has already been scheduled or transferred, please accept our thanks and reply with the payment UTR number. Feel free to let us know if you require an updated statement of accounts.\n\n"
            f"Warm regards,\n\n{sender_name}\n{sender_company}"
        )

    elif tone == "Professional / Standard":
        wa_text = (
            f"Hello {customer_name},\n\n"
            f"This is a payment follow-up for invoice *{inv_num}* issued to *{company}*.\n\n"
            f"• *Amount Outstanding:* {amount}\n"
            f"• *Due Date:* {due_date} ({status_text})\n\n"
            f"*Bank / UPI Remittance Details:*\n{payment_info_wa}{note_section}\n\n"
            f"Please arrange clearance and reply with the transfer confirmation.\n\n"
            f"Regards,\n*{sender_company} Accounts Department*"
        )
        email_subject = f"Payment Reminder: Invoice {inv_num} - {amount} ({status_text})"
        email_body = (
            f"Dear {customer_name},\n\n"
            f"We are writing to follow up on outstanding invoice {inv_num} issued to {company}.\n\n"
            f"Invoice Summary:\n"
            f"----------------------------------------\n"
            f"Invoice Number: {inv_num}\n"
            f"Total Amount:   {amount}\n"
            f"Due Date:       {due_date} ({status_text})\n"
            f"----------------------------------------\n\n"
            f"{payment_info_email}{note_email}\n"
            f"Kindly confirm receipt of this notice and advise on the expected remittance date.\n\n"
            f"Sincerely,\n\nAccounts Receivable Team\n{sender_company}"
        )

    elif tone == "Firm / Assertive":
        wa_text = (
            f"Dear {customer_name},\n\n"
            f"We have not yet received payment for invoice *{inv_num}* ({amount}), which is now *{status_text}*.\n\n"
            f"Timely settlement ensures uninterrupted deliverables and active account status for *{company}*.\n\n"
            f"*Immediate Clearance Details:*\n{payment_info_wa}{note_section}\n\n"
            f"Please share the payment UTR confirmation today to avoid credit hold.\n\n"
            f"Regards,\n*{sender_name}* | {sender_company}"
        )
        email_subject = f"OVERDUE NOTICE: Invoice {inv_num} ({amount}) - Immediate Settlement Requested"
        email_body = (
            f"Dear {customer_name},\n\n"
            f"Our records indicate that payment for invoice {inv_num} in the amount of {amount} remains outstanding and is now {status_text}.\n\n"
            f"Despite our previous reminders, we have not received remittance or UTR confirmation from {company}.\n\n"
            f"To prevent any disruption to ongoing deliverables or account suspension, please arrange clearance today using the banking details below:\n\n"
            f"{payment_info_email}{note_email}\n"
            f"If there is any billing discrepancy or payment query, please contact us immediately.\n\n"
            f"Sincerely,\n\nCredit Control Department\n{sender_company}"
        )

    else:  # Urgent / Final Notice
        wa_text = (
            f"⚠️ *URGENT NOTICE: Overdue Invoice {inv_num}*\n\n"
            f"Attention: {customer_name} ({company})\n\n"
            f"Invoice *{inv_num}* for *{amount}* is seriously overdue ({status_text}). Continued delay may lead to late interest charges and suspension of ongoing services.\n\n"
            f"*Remit Immediately via:*\n{payment_info_wa}{note_section}\n\n"
            f"Please reply with the UTR transaction number immediately.\n\n"
            f"*{sender_company} Finance*"
        )
        email_subject = f"FINAL NOTICE: Immediate Settlement Required for Invoice {inv_num} ({amount})"
        email_body = (
            f"Attention: {customer_name},\n\n"
            f"This is a formal final notice regarding overdue invoice {inv_num} for {amount}, which is now {status_text}.\n\n"
            f"Your account is currently under management credit review. To avoid formal service suspension or legal escalation, please settle the outstanding balance immediately.\n\n"
            f"{payment_info_email}{note_email}\n"
            f"If payment has been remitted in the last 24 hours, kindly forward the bank transaction slip/UTR immediately so we can update your credit record.\n\n"
            f"Regards,\n\nFinance & Recovery Team\n{sender_company}"
        )

    wa_encoded = urllib.parse.quote(wa_text)
    whatsapp_url = f"https://wa.me/{phone}?text={wa_encoded}" if phone else ""

    email_subj_enc = urllib.parse.quote(email_subject)
    email_body_enc = urllib.parse.quote(email_body)
    mailto_url = f"mailto:{recipient_email}?subject={email_subj_enc}&body={email_body_enc}" if recipient_email else ""

    return {
        "tone": tone,
        "whatsapp_text": wa_text,
        "whatsapp_url": whatsapp_url,
        "email_subject": email_subject,
        "email_body": email_body,
        "mailto_url": mailto_url,
        "recipient_phone": phone,
        "recipient_email": recipient_email,
        "upi_id": upi_id,
        "bank_details": bank_details
    }
