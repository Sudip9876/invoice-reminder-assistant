"""
reminder_engine.py - Smart Tone-Adjusted WhatsApp & Email Reminder Generator
Generates contextual, polite, and actionable payment reminders for small businesses.
Creates one-click WhatsApp (wa.me) and Email (mailto) launch links.
"""

import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional

TONE_DESCRIPTIONS = {
    "Gentle / Friendly": "Warm, appreciative tone. Best for upcoming invoices or 1-3 days past due.",
    "Professional / Standard": "Clear, objective business reminder. Best for due date or 3-7 days past due.",
    "Firm / Assertive": "Direct, structured follow-up. Best for 7-14 days overdue or chronic late payers.",
    "Urgent / Final Notice": "Formal notice emphasizing account hold or escalation. Best for 15+ days overdue."
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
    payment_link: str = "https://pay.example.com/invoice",
    custom_note: str = ""
) -> Dict[str, Any]:
    """
    Generates both WhatsApp and Email drafts calibrated for the selected tone.
    """
    customer_name = invoice.get("customer_name", "Valued Client")
    company = invoice.get("customer_company", "")
    inv_num = invoice.get("invoice_number", "INV-000")
    amount = f"${invoice.get('amount', 0):,.2f}"
    due_date = invoice.get("due_date", "")
    recipient_email = invoice.get("customer_email", "")
    phone = clean_phone_number(invoice.get("customer_phone", ""))

    # Calculate days overdue or remaining
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

    note_section = f"\nNote: {custom_note}" if custom_note.strip() else ""

    # ==========================
    # WhatsApp Templates (Markdown formatting *bold*)
    # ==========================
    if tone == "Gentle / Friendly":
        wa_text = (
            f"Hi {customer_name}! 😊 Hope you're having a productive week.\n\n"
            f"Just a quick, friendly reminder regarding invoice *{inv_num}* for *{amount}*, which is {status_text} ({due_date}).\n\n"
            f"You can review or pay easily here: {payment_link}{note_section}\n\n"
            f"If you've already sent the payment, please disregard this note. Let us know if you need any assistance!\n\n"
            f"Warm regards,\n*{sender_name}* from {sender_company}"
        )
        email_subject = f"Friendly Reminder: Invoice {inv_num} from {sender_company}"
        email_body = (
            f"Dear {customer_name},\n\n"
            f"We hope this note finds you well.\n\n"
            f"This is a gentle reminder that invoice {inv_num} for the amount of {amount} is currently {status_text} (Due Date: {due_date}).\n\n"
            f"To view invoice details and settle online, please visit:\n{payment_link}\n{note_section}\n\n"
            f"If payment has already been processed, please accept our thanks and ignore this reminder. Should you have any questions or require an updated copy, feel free to reply directly to this email.\n\n"
            f"Best regards,\n\n{sender_name}\n{sender_company}"
        )

    elif tone == "Professional / Standard":
        wa_text = (
            f"Hello {customer_name},\n\n"
            f"This is a payment reminder for invoice *{inv_num}* ({company}).\n\n"
            f"• *Amount Due:* {amount}\n"
            f"• *Due Date:* {due_date} ({status_text})\n"
            f"• *Payment Link:* {payment_link}{note_section}\n\n"
            f"Please let us know once the transfer is initiated or if you need our bank remittance details.\n\n"
            f"Thank you for your prompt attention.\n"
            f"*{sender_company} Accounts Team*"
        )
        email_subject = f"Invoice {inv_num} Payment Notice: {amount} ({status_text})"
        email_body = (
            f"Dear {customer_name},\n\n"
            f"We are writing to follow up on outstanding invoice {inv_num} issued to {company}.\n\n"
            f"Summary of Details:\n"
            f"----------------------------------------\n"
            f"Invoice Number: {inv_num}\n"
            f"Total Amount:   {amount}\n"
            f"Due Date:       {due_date} ({status_text})\n"
            f"Payment Link:   {payment_link}\n"
            f"----------------------------------------\n{note_section}\n\n"
            f"Kindly confirm receipt of this invoice and advise on the expected settlement date.\n\n"
            f"Sincerely,\n\nAccounts Receivable Department\n{sender_company}"
        )

    elif tone == "Firm / Assertive":
        wa_text = (
            f"Dear {customer_name},\n\n"
            f"We have not yet received payment for invoice *{inv_num}* ({amount}), which is now *{status_text}*.\n\n"
            f"Timely settlement ensures uninterrupted service for {company}. Please arrange immediate clearance via: {payment_link}{note_section}\n\n"
            f"Please reply with the payment confirmation or transaction UTR at your earliest convenience.\n\n"
            f"Regards,\n*{sender_name}* | {sender_company}"
        )
        email_subject = f"OVERDUE NOTICE: Invoice {inv_num} ({amount}) - Immediate Attention Requested"
        email_body = (
            f"Dear {customer_name},\n\n"
            f"Our records indicate that payment for invoice {inv_num} in the amount of {amount} remains outstanding and is now {status_text}.\n\n"
            f"Despite our previous notifications, we have not received remittance or notice of pending transfer from {company}.\n\n"
            f"To avoid any disruption to ongoing deliverables or account holds, please remit payment today using the link below:\n{payment_link}\n{note_section}\n\n"
            f"If there is any discrepancy or if you require payment plan assistance, please contact us immediately.\n\n"
            f"Sincerely,\n\nCredit Control Team\n{sender_company}"
        )

    else:  # Urgent / Final Notice
        wa_text = (
            f"⚠️ *URGENT NOTICE: Invoice {inv_num} Overdue*\n\n"
            f"Attention: {customer_name} ({company})\n\n"
            f"Invoice *{inv_num}* for *{amount}* is seriously overdue ({status_text}). Continued delay may result in late fees and suspension of ongoing services.\n\n"
            f"Please clear this balance immediately: {payment_link}{note_section}\n\n"
            f"Contact us today if you have any questions.\n"
            f"*{sender_company} Finance*"
        )
        email_subject = f"FINAL NOTICE: Urgent Settlement Required for Invoice {inv_num} ({amount})"
        email_body = (
            f"Attention: {customer_name},\n\n"
            f"This is a formal final notice regarding unpaid invoice {inv_num} for {amount}, which is now {status_text}.\n\n"
            f"Your account is currently subject to immediate credit review. To avoid service suspension or escalation to our formal collections process, please settle the outstanding balance immediately.\n\n"
            f"Secure Settlement Link:\n{payment_link}\n{note_section}\n\n"
            f"If payment has been executed within the last 24 hours, please forward the remittance slip immediately so we can update your ledger.\n\n"
            f"Regards,\n\nFinance & Recovery Team\n{sender_company}"
        )

    # WhatsApp deep-link
    wa_encoded = urllib.parse.quote(wa_text)
    whatsapp_url = f"https://wa.me/{phone}?text={wa_encoded}" if phone else ""

    # Email mailto link
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
        "recipient_email": recipient_email
    }
