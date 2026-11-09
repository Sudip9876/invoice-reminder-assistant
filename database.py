"""
database.py - SQLite Database Layer for Invoice & Payment-Reminder Assistant
Handles schema creation, CRUD operations, and pre-populating realistic demo data.
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

def init_db():
    """Initializes database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Customers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        company TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Invoices table
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

    conn.commit()
    conn.close()

def seed_demo_data_if_empty():
    """Seeds rich, realistic data if the database is currently empty."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM customers")
    if cursor.fetchone()["count"] > 0:
        conn.close()
        return  # Already seeded

    # 1. Insert 8 realistic business customers
    customers_data = [
        ("Aarav Mehta", "Apex Digital Labs", "aarav@apexdigital.io", "+919876543210"),
        ("Sophia Ramirez", "BluePeak Logistics", "sophia@bluepeak.com", "+14155552671"),
        ("Vikram Singh", "Nova Retail Chains", "vikram@novaretail.in", "+919812345678"),
        ("Elena Rostova", "CloudScale Networks", "elena@cloudscale.net", "+12125550199"),
        ("Rajesh Kulkarni", "Zenith Hardware Supplies", "rajesh@zenithhardware.com", "+919765432109"),
        ("Chloe Dupont", "Atelier Media Studio", "chloe@ateliermedia.fr", "+33612345678"),
        ("Ananya Iyer", "Pulse Biotech Corp", "ananya@pulsebiotech.com", "+919823456781"),
        ("Marcus Vance", "Vance Capital Advisors", "marcus@vancecap.com", "+13125558900"),
    ]

    for name, company, email, phone in customers_data:
        cursor.execute(
            "INSERT INTO customers (name, company, email, phone) VALUES (?, ?, ?, ?)",
            (name, company, email, phone)
        )

    # 2. Add realistic historical paid invoices and payment habits:
    # Customer 1 (Apex Digital): Very punctual payer (delay -2 to +1 days, was_late 0)
    # Customer 2 (BluePeak): Chronic late payer (delay +15 to +40 days, was_late 1)
    # Customer 3 (Nova Retail): Occasional delay on large invoices (delay 3 to 18 days, mixed was_late)
    # Customer 4 (CloudScale): Highly punctual corporate client (always on time)
    # Customer 5 (Zenith Hardware): High risk, cash flow problems (consistently 20+ days late)
    # Customer 6 (Atelier Media): Mostly on time, small studio
    # Customer 7 (Pulse Biotech): Good payer, strict 30-day corporate cycle
    # Customer 8 (Vance Capital): Punctual, large amounts

    today = datetime.date.today()

    history_records = [
        # cust_id, amount, term_days, delay_days, was_late, months_ago
        # Cust 1 (Apex): Punctual
        (1, 1200.0, 30, -2, 0, 8),
        (1, 1500.0, 30, 0, 0, 6),
        (1, 1400.0, 30, 1, 0, 4),
        (1, 1800.0, 30, -1, 0, 2),
        (1, 1350.0, 30, 0, 0, 1),

        # Cust 2 (BluePeak): Chronic late payer
        (2, 3500.0, 30, 22, 1, 9),
        (2, 4200.0, 30, 35, 1, 7),
        (2, 2800.0, 30, 18, 1, 5),
        (2, 5100.0, 30, 42, 1, 3),
        (2, 3900.0, 30, 28, 1, 1),

        # Cust 3 (Nova Retail): Mixed (late when amount > 3000)
        (3, 1100.0, 15, 1, 0, 8),
        (3, 4800.0, 30, 19, 1, 6),
        (3, 1250.0, 15, 0, 0, 5),
        (3, 6200.0, 30, 25, 1, 3),
        (3, 1500.0, 15, 2, 0, 2),

        # Cust 4 (CloudScale): Always on time
        (4, 2500.0, 30, -3, 0, 10),
        (4, 2500.0, 30, -2, 0, 7),
        (4, 2600.0, 30, -1, 0, 4),
        (4, 2500.0, 30, 0, 0, 2),

        # Cust 5 (Zenith Hardware): High risk, frequent delays
        (5, 1800.0, 30, 15, 1, 8),
        (5, 2200.0, 30, 31, 1, 6),
        (5, 1900.0, 30, 24, 1, 4),
        (5, 2400.0, 30, 40, 1, 2),

        # Cust 6 (Atelier Media): Good, minor delay
        (6, 950.0, 15, 2, 0, 7),
        (6, 1200.0, 30, 4, 0, 5),
        (6, 1100.0, 30, 12, 1, 3),
        (6, 1300.0, 30, 1, 0, 1),

        # Cust 7 (Pulse Biotech): Punctual enterprise
        (7, 7500.0, 45, 0, 0, 9),
        (7, 8200.0, 45, -1, 0, 6),
        (7, 7800.0, 45, 1, 0, 3),

        # Cust 8 (Vance Capital): High value, prompt
        (8, 12000.0, 30, 0, 0, 8),
        (8, 14500.0, 30, -2, 0, 5),
        (8, 13000.0, 30, 1, 0, 2),
    ]

    for cust_id, amount, term_days, delay_days, was_late, months_ago in history_records:
        approx_due_date = today - datetime.timedelta(days=months_ago * 30)
        approx_paid_date = approx_due_date + datetime.timedelta(days=delay_days)
        cursor.execute("""
            INSERT INTO payment_history (customer_id, amount, term_days, due_date, paid_date, delay_days, was_late)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cust_id, amount, term_days, str(approx_due_date), str(approx_paid_date), delay_days, was_late))

    # 3. Create active invoices (Pending, Overdue, and Paid)
    active_invoices = [
        # inv_num, cust_id, issue_offset_days, due_offset_days, amount, status, notes
        ("INV-2026-001", 1, -25, 5, 2100.0, "Pending", "Quarterly UX design retainer"),
        ("INV-2026-002", 2, -45, -15, 4800.0, "Overdue", "Warehouse management integration"),
        ("INV-2026-003", 2, -20, 10, 3200.0, "Pending", "Fleet tracking API module"),
        ("INV-2026-004", 3, -40, -10, 5500.0, "Overdue", "POS barcode scanner rollout"),
        ("INV-2026-005", 4, -20, 10, 2600.0, "Pending", "Cloud infrastructure maintenance"),
        ("INV-2026-006", 5, -50, -20, 2900.0, "Overdue", "Custom ERP connector build"),
        ("INV-2026-007", 6, -10, 20, 1400.0, "Pending", "Brand identity assets & guidelines"),
        ("INV-2026-008", 7, -60, -15, 8400.0, "Overdue", "Clinical data automation pipeline"),
        ("INV-2026-009", 8, -15, 15, 15000.0, "Pending", "Annual advisory retainer"),
        ("INV-2026-010", 1, -60, -30, 1750.0, "Paid", "Mobile responsive refactor (Paid on time)"),
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

    conn.commit()
    conn.close()

# CRUD / Query Helpers
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

def add_customer(name: str, company: str, email: str, phone: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customers (name, company, email, phone) VALUES (?, ?, ?, ?)",
        (name.strip(), company.strip(), email.strip(), phone.strip())
    )
    conn.commit()
    cust_id = cursor.lastrowid
    conn.close()
    return cust_id

def get_all_invoices() -> List[Dict[str, Any]]:
    conn = get_connection()
    query = """
    SELECT 
        i.*,
        c.name as customer_name,
        c.company as customer_company,
        c.email as customer_email,
        c.phone as customer_phone
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
        c.phone as customer_phone
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

    # Get invoice details
    inv = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    if inv:
        d_due = datetime.datetime.strptime(inv["due_date"], "%Y-%m-%d").date()
        d_paid = datetime.datetime.strptime(paid_date, "%Y-%m-%d").date()
        delay_days = (d_paid - d_due).days
        was_late = 1 if delay_days > 5 else 0  # 5-day grace period

        # Update invoice
        cursor.execute("UPDATE invoices SET status = 'Paid', paid_date = ? WHERE id = ?", (paid_date, invoice_id))
        
        # Record into payment history for ML model training!
        cursor.execute("""
            INSERT INTO payment_history (customer_id, invoice_id, amount, term_days, due_date, paid_date, delay_days, was_late)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (inv["customer_id"], invoice_id, inv["amount"], inv["term_days"], inv["due_date"], paid_date, delay_days, was_late))

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

def get_payment_history_records() -> List[Dict[str, Any]]:
    conn = get_connection()
    query = """
    SELECT 
        ph.*,
        c.name as customer_name,
        c.company as customer_company
    FROM payment_history ph
    JOIN customers c ON ph.customer_id = c.id
    ORDER BY ph.id ASC
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_customer_stats(customer_id: int) -> Dict[str, Any]:
    """Returns payment history stats for a specific customer."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT delay_days, was_late, amount
        FROM payment_history
        WHERE customer_id = ?
    """, (customer_id,)).fetchall()
    conn.close()

    if not rows:
        return {
            "total_invoices": 0,
            "late_count": 0,
            "on_time_count": 0,
            "avg_delay": 0.0,
            "late_rate": 0.0,
            "has_history": False
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
        "has_history": True
    }
