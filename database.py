"""
database.py - SQLite Database & CRM Layer (INR Currency & Indian Business Context)
Handles schema creation, Indian GST/UPI details, CRM communication logs,
and allows clearing all demo data or seeding realistic INR records.
"""

import sqlite3
import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "invoicing.db"

def get_connection():
    """Returns a SQLite connection with row_factory set to dict-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def format_inr(number: float) -> str:
    """Formats a number into Indian Rupee representation (e.g. ₹1,25,000.00)."""
    try:
        val = float(number)
        s = f"{val:,.2f}"
        return f"₹{s}"
    except Exception:
        return f"₹{number}"

def init_db():
    """Initializes database tables with full CRM support if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Customers table with CRM and Indian compliance fields
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        company TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        gstin TEXT,
        credit_limit REAL DEFAULT 150000.0,
        payment_terms INTEGER DEFAULT 30,
        upi_id TEXT,
        bank_details TEXT,
        tags TEXT DEFAULT 'Active',
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Invoices table (Amounts in INR)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT UNIQUE NOT NULL,
        customer_id INTEGER NOT NULL,
        issue_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        term_days INTEGER DEFAULT 30,
        amount REAL NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Paid', 'Pending', 'Overdue')),
        paid_date TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    );
    """)

    # Payment History table (Used to train the ML model)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        invoice_id INTEGER,
        amount REAL NOT NULL,
        term_days INTEGER DEFAULT 30,
        due_date TEXT NOT NULL,
        paid_date TEXT NOT NULL,
        delay_days INTEGER NOT NULL,
        was_late INTEGER NOT NULL CHECK(was_late IN (0, 1)),
        FOREIGN KEY (customer_id) REFERENCES customers (id),
        FOREIGN KEY (invoice_id) REFERENCES invoices (id)
    );
    """)

    # CRM Communication & Follow-up Tracker table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crm_interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        invoice_id INTEGER,
        interaction_type TEXT NOT NULL,
        interaction_date TEXT NOT NULL,
        tone TEXT,
        summary TEXT NOT NULL,
        promised_payment_date TEXT,
        status TEXT DEFAULT 'Completed',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id),
        FOREIGN KEY (invoice_id) REFERENCES invoices (id)
    );
    """)

    conn.commit()
    conn.close()

def clear_all_data():
    """Wipes all records from the database to give the user a 100% clean production slate."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM crm_interactions")
    cursor.execute("DELETE FROM payment_history")
    cursor.execute("DELETE FROM invoices")
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM sqlite_sequence")
    conn.commit()
    conn.close()

def seed_indian_demo_data():
    """Seeds realistic Indian SME & enterprise records with amounts in INR (₹)."""
    clear_all_data()
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Insert 8 realistic Indian business customers
    customers_data = [
        ("Aarav Mehta", "Apex Digital Labs LLP", "aarav@apexdigital.in", "+919876543210", "27AAACA1234F1Z1", 250000.0, 30, "apexlabs@okhdfcbank", "HDFC Bank | A/C: 50200012345678 | IFSC: HDFC0000123", "VIP, Retainer", "Prompt payer, tech agency"),
        ("Rohan Sharma", "BluePeak Logistics India", "rohan@bluepeaklogistics.in", "+919823456789", "07AABCB5678K1ZV", 500000.0, 30, "bluepeak@icici", "ICICI Bank | A/C: 001205001234 | IFSC: ICIC0000012", "Slow Payer, Freight", "Frequently requires 2-3 reminder follow-ups"),
        ("Vikram Singh", "Nova Retail Chains Ltd", "vikram@novaretail.in", "+919812345678", "06AACCB9876P1ZX", 350000.0, 15, "novaretail@axl", "Axis Bank | A/C: 914020034567890 | IFSC: UTIB0000914", "FMCG, High Volume", "Punctual on small orders, delays bulk orders"),
        ("Priya Nair", "CloudScale Tech Bangalore", "priya@cloudscale.co.in", "+919845012345", "29AACCC3456L1Z2", 400000.0, 30, "cloudscale@kotak", "Kotak Bank | A/C: 7812345678 | IFSC: KKBK0000781", "Corporate, Reliable", "Strict monthly accounts payable cycle on 5th"),
        ("Rajesh Kulkarni", "Zenith Industrial Supplies", "rajesh@zenithhardware.in", "+919765432109", "27AAACZ6543M1ZM", 200000.0, 30, "zenithsupplies@sbi", "State Bank of India | A/C: 30123456789 | IFSC: SBIN0001234", "High Risk, Credit Watch", "Frequent working capital crunches"),
        ("Kavita Rao", "Atelier Media Creative Studio", "kavita@ateliermedia.in", "+919820011223", "27AABCA9012N1ZY", 150000.0, 15, "ateliermedia@paytm", "Paytm Payments Bank | A/C: 919820011223 | IFSC: PYTM0123456", "Creative, Retainer", "Good working relationship, responds quickly on WhatsApp"),
        ("Dr. Ananya Iyer", "Pulse Biotech Labs Pune", "ananya@pulsebiotech.in", "+919823456781", "27AAECP4567Q1ZR", 600000.0, 45, "pulsebio@yesbank", "Yes Bank | A/C: 01234567890123 | IFSC: YESB0000123", "Pharma, Enterprise", "Standard 45-day payment terms, reliable"),
        ("Marcus Vance", "Vance Advisory Mumbai", "marcus@vanceadvisory.in", "+919819988776", "27AACCV7890R1ZT", 1000000.0, 30, "vance@standardchartered", "Standard Chartered | A/C: 45678901234 | IFSC: SCBL0036001", "VIP, High Ticket", "Large ticket consultancy invoices, prompt approval"),
    ]

    for name, company, email, phone, gstin, limit, terms, upi, bank, tags, notes in customers_data:
        cursor.execute("""
            INSERT INTO customers (name, company, email, phone, gstin, credit_limit, payment_terms, upi_id, bank_details, tags, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, company, email, phone, gstin, limit, terms, upi, bank, tags, notes))

    # 2. Add realistic historical paid invoices in INR (₹)
    today = datetime.date.today()
    history_records = [
        # cust_id, amount_inr, term_days, delay_days, was_late, months_ago
        # Cust 1 (Apex): Punctual IT agency
        (1, 85000.0, 30, -2, 0, 8),
        (1, 120000.0, 30, 0, 0, 6),
        (1, 95000.0, 30, 1, 0, 4),
        (1, 140000.0, 30, -1, 0, 2),
        (1, 110000.0, 30, 0, 0, 1),

        # Cust 2 (BluePeak): Chronic late payer
        (2, 280000.0, 30, 22, 1, 9),
        (2, 350000.0, 30, 35, 1, 7),
        (2, 220000.0, 30, 18, 1, 5),
        (2, 420000.0, 30, 42, 1, 3),
        (2, 310000.0, 30, 28, 1, 1),

        # Cust 3 (Nova Retail): Mixed (late when order > ₹2 Lakhs)
        (3, 75000.0, 15, 1, 0, 8),
        (3, 380000.0, 30, 19, 1, 6),
        (3, 90000.0, 15, 0, 0, 5),
        (3, 490000.0, 30, 25, 1, 3),
        (3, 110000.0, 15, 2, 0, 2),

        # Cust 4 (CloudScale): Always on time
        (4, 180000.0, 30, -3, 0, 10),
        (4, 185000.0, 30, -2, 0, 7),
        (4, 190000.0, 30, -1, 0, 4),
        (4, 185000.0, 30, 0, 0, 2),

        # Cust 5 (Zenith Hardware): High risk, frequent delays
        (5, 140000.0, 30, 15, 1, 8),
        (5, 175000.0, 30, 31, 1, 6),
        (5, 150000.0, 30, 24, 1, 4),
        (5, 190000.0, 30, 40, 1, 2),

        # Cust 6 (Atelier Media): Good, minor delay
        (6, 65000.0, 15, 2, 0, 7),
        (6, 85000.0, 30, 4, 0, 5),
        (6, 90000.0, 30, 12, 1, 3),
        (6, 95000.0, 30, 1, 0, 1),

        # Cust 7 (Pulse Biotech): Punctual enterprise
        (7, 550000.0, 45, 0, 0, 9),
        (7, 620000.0, 45, -1, 0, 6),
        (7, 580000.0, 45, 1, 0, 3),

        # Cust 8 (Vance Advisory): High value, prompt
        (8, 850000.0, 30, 0, 0, 8),
        (8, 980000.0, 30, -2, 0, 5),
        (8, 920000.0, 30, 1, 0, 2),
    ]

    for cust_id, amount, term_days, delay_days, was_late, months_ago in history_records:
        approx_due_date = today - datetime.timedelta(days=months_ago * 30)
        approx_paid_date = approx_due_date + datetime.timedelta(days=delay_days)
        cursor.execute("""
            INSERT INTO payment_history (customer_id, amount, term_days, due_date, paid_date, delay_days, was_late)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cust_id, amount, term_days, str(approx_due_date), str(approx_paid_date), delay_days, was_late))

    # 3. Create active invoices in INR (₹)
    active_invoices = [
        # inv_num, cust_id, issue_offset_days, due_offset_days, amount_inr, status, notes
        ("INV-2026-001", 1, -25, 5, 165000.0, "Pending", "Quarterly App UI/UX Design & Sprint Delivery"),
        ("INV-2026-002", 2, -45, -15, 380000.0, "Overdue", "Fleet GPS Tracking API Integration & Server Setup"),
        ("INV-2026-003", 2, -20, 10, 245000.0, "Pending", "Warehouse Dispatch Portal Maintenance"),
        ("INV-2026-004", 3, -40, -10, 420000.0, "Overdue", "POS Barcode & Billing System Cloud Migration"),
        ("INV-2026-005", 4, -20, 10, 195000.0, "Pending", "AWS Cloud Infrastructure DevOps Retainer"),
        ("INV-2026-006", 5, -50, -20, 215000.0, "Overdue", "Custom ERP Connector & Inventory Sync"),
        ("INV-2026-007", 6, -10, 20, 110000.0, "Pending", "Corporate Video Production & Brand Kit"),
        ("INV-2026-008", 7, -60, -15, 625000.0, "Overdue", "Clinical Genomics Analytics Pipeline Build"),
        ("INV-2026-009", 8, -15, 15, 950000.0, "Pending", "Annual Financial Advisory & M&A Retainer"),
        ("INV-2026-010", 1, -60, -30, 135000.0, "Paid", "Mobile Web Performance Optimization (Paid on time)"),
    ]

    for inv_num, cust_id, issue_off, due_off, amount, status, notes in active_invoices:
        issue_d = today + datetime.timedelta(days=issue_off)
        due_d = today + datetime.timedelta(days=due_off)
        paid_d = str(due_d + datetime.timedelta(days=1)) if status == "Paid" else None
        term_days = (due_d - issue_d).days

        cursor.execute("""
            INSERT INTO invoices (invoice_number, customer_id, issue_date, due_date, term_days, amount, status, paid_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (inv_num, cust_id, str(issue_d), str(due_d), term_days, amount, status, paid_d, notes))

    # 4. Insert sample CRM interactions
    sample_interactions = [
        (2, 2, "WhatsApp Reminder", str(today - datetime.timedelta(days=3)), "Firm / Assertive", "Sent firm WhatsApp reminder. Rohan responded mentioning fund release is pending from their head office.", str(today + datetime.timedelta(days=4))),
        (4, 5, "Email Reminder", str(today - datetime.timedelta(days=7)), "Gentle / Friendly", "Sent routine pre-due notification. Priya confirmed invoice is queued for approval on 15th.", str(today + datetime.timedelta(days=10))),
        (5, 6, "Phone Call", str(today - datetime.timedelta(days=2)), "Urgent / Final Notice", "Called Rajesh Kulkarni directly. Promised to RTGS 50% advance by Friday.", str(today + datetime.timedelta(days=3))),
    ]
    for cust_id, inv_id, itype, idate, tone, summary, pdate in sample_interactions:
        cursor.execute("""
            INSERT INTO crm_interactions (customer_id, invoice_id, interaction_type, interaction_date, tone, summary, promised_payment_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cust_id, inv_id, itype, idate, tone, summary, pdate))

    conn.commit()
    conn.close()

# CRM Interaction Helpers
def add_crm_interaction(
    customer_id: int,
    interaction_type: str,
    summary: str,
    invoice_id: Optional[int] = None,
    tone: Optional[str] = None,
    promised_payment_date: Optional[str] = None
) -> int:
    """Logs a CRM activity (call, WhatsApp reminder, email, meeting, payment promise)."""
    conn = get_connection()
    cursor = conn.cursor()
    today_str = str(datetime.date.today())
    cursor.execute("""
        INSERT INTO crm_interactions (customer_id, invoice_id, interaction_type, interaction_date, tone, summary, promised_payment_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (customer_id, invoice_id, interaction_type, today_str, tone, summary, promised_payment_date))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_crm_interactions(customer_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Retrieves CRM activity history, optionally filtered by customer."""
    conn = get_connection()
    if customer_id:
        query = """
            SELECT ci.*, c.name as customer_name, c.company as customer_company, i.invoice_number
            FROM crm_interactions ci
            JOIN customers c ON ci.customer_id = c.id
            LEFT JOIN invoices i ON ci.invoice_id = i.id
            WHERE ci.customer_id = ?
            ORDER BY ci.id DESC
        """
        rows = conn.execute(query, (customer_id,)).fetchall()
    else:
        query = """
            SELECT ci.*, c.name as customer_name, c.company as customer_company, i.invoice_number
            FROM crm_interactions ci
            JOIN customers c ON ci.customer_id = c.id
            LEFT JOIN invoices i ON ci.invoice_id = i.id
            ORDER BY ci.id DESC
        """
        rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Customer CRUD Helpers
def get_all_customers() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM customers ORDER BY name ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_customer_by_id(customer_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_customer(
    name: str,
    company: str,
    email: str,
    phone: str,
    gstin: str = "",
    credit_limit: float = 150000.0,
    payment_terms: int = 30,
    upi_id: str = "",
    bank_details: str = "",
    tags: str = "Active",
    notes: str = ""
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers (name, company, email, phone, gstin, credit_limit, payment_terms, upi_id, bank_details, tags, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name.strip(), company.strip(), email.strip(), phone.strip(), gstin.strip().upper(), float(credit_limit), int(payment_terms), upi_id.strip(), bank_details.strip(), tags.strip(), notes.strip()))
    conn.commit()
    cust_id = cursor.lastrowid
    conn.close()
    return cust_id

# Invoice CRUD Helpers
def get_all_invoices() -> List[Dict[str, Any]]:
    conn = get_connection()
    query = """
    SELECT 
        i.*,
        c.name as customer_name,
        c.company as customer_company,
        c.email as customer_email,
        c.phone as customer_phone,
        c.gstin as customer_gstin,
        c.credit_limit as customer_credit_limit,
        c.upi_id as customer_upi_id,
        c.bank_details as customer_bank_details
    FROM invoices i
    JOIN customers c ON i.customer_id = c.id
    ORDER BY i.due_date ASC
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_invoice_by_id(invoice_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    query = """
    SELECT 
        i.*,
        c.name as customer_name,
        c.company as customer_company,
        c.email as customer_email,
        c.phone as customer_phone,
        c.gstin as customer_gstin,
        c.credit_limit as customer_credit_limit,
        c.upi_id as customer_upi_id,
        c.bank_details as customer_bank_details
    FROM invoices i
    JOIN customers c ON i.customer_id = c.id
    WHERE i.id = ?
    """
    row = conn.execute(query, (invoice_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_invoice(invoice_number: str, customer_id: int, issue_date: str, due_date: str, amount: float, notes: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    d1 = datetime.datetime.strptime(issue_date, "%Y-%m-%d").date()
    d2 = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
    term_days = (d2 - d1).days
    today = datetime.date.today()
    status = "Overdue" if d2 < today else "Pending"

    cursor.execute("""
        INSERT INTO invoices (invoice_number, customer_id, issue_date, due_date, term_days, amount, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (invoice_number, customer_id, issue_date, due_date, term_days, amount, status, notes))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def mark_invoice_as_paid(invoice_id: int, paid_date: Optional[str] = None):
    conn = get_connection()
    cursor = conn.cursor()
    if not paid_date:
        paid_date = str(datetime.date.today())

    inv = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    if inv:
        d_due = datetime.datetime.strptime(inv["due_date"], "%Y-%m-%d").date()
        d_paid = datetime.datetime.strptime(paid_date, "%Y-%m-%d").date()
        delay_days = (d_paid - d_due).days
        was_late = 1 if delay_days > 5 else 0

        cursor.execute("UPDATE invoices SET status = 'Paid', paid_date = ? WHERE id = ?", (paid_date, invoice_id))
        
        cursor.execute("""
            INSERT INTO payment_history (customer_id, invoice_id, amount, term_days, due_date, paid_date, delay_days, was_late)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (inv["customer_id"], invoice_id, inv["amount"], inv["term_days"], inv["due_date"], paid_date, delay_days, was_late))

        # Log to CRM Interactions
        cursor.execute("""
            INSERT INTO crm_interactions (customer_id, invoice_id, interaction_type, interaction_date, summary, status)
            VALUES (?, ?, 'Payment Received', ?, ?, 'Completed')
        """, (inv["customer_id"], invoice_id, paid_date, f"Payment of {format_inr(inv['amount'])} received on {paid_date} (Delay: {delay_days} days)."))

    conn.commit()
    conn.close()

def refresh_invoice_statuses():
    """Auto-updates 'Pending' to 'Overdue' if due_date is in the past."""
    conn = get_connection()
    today = str(datetime.date.today())
    conn.execute("""
        UPDATE invoices
        SET status = 'Overdue'
        WHERE status = 'Pending' AND due_date < ?
    """, (today,))
    conn.commit()
    conn.close()

def get_customer_stats(customer_id: int) -> Dict[str, Any]:
    """Returns payment history stats for a specific customer."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT delay_days, was_late, amount
        FROM payment_history
        WHERE customer_id = ?
    """, (customer_id,)).fetchall()

    # Calculate current outstanding unpaid balance for credit limit calculation
    unpaid_row = conn.execute("""
        SELECT SUM(amount) as outstanding
        FROM invoices
        WHERE customer_id = ? AND status IN ('Pending', 'Overdue')
    """, (customer_id,)).fetchone()
    outstanding = unpaid_row["outstanding"] or 0.0

    conn.close()

    if not rows:
        return {
            "total_invoices": 0,
            "late_count": 0,
            "on_time_count": 0,
            "avg_delay": 0.0,
            "late_rate": 0.0,
            "has_history": False,
            "outstanding": outstanding
        }

    total = len(rows)
    late_count = sum(r["was_late"] for r in rows)
    on_time = total - late_count
    avg_delay = sum(r["delay_days"] for r in rows) / total
    late_rate = late_count / total

    return {
        "total_invoices": total,
        "late_count": late_count,
        "on_time_count": on_time,
        "avg_delay": round(avg_delay, 1),
        "late_rate": round(late_rate, 2),
        "has_history": True,
        "outstanding": outstanding
    }
