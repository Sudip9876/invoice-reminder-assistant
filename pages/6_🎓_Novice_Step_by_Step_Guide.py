"""
pages/6_🎓_Novice_Step_by_Step_Guide.py - Step-by-Step Novice Learning Guide (INR & CRM)
A complete beginner guide explaining every layer of the application: database, ML, CRM, reminders, and UI in INR.
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st

st.set_page_config(page_title="Novice Step-by-Step Guide (INR)", page_icon="🎓", layout="wide")

st.title("🎓 Novice Guide: Building & Understanding the App (INR & CRM)")
st.caption("A beginner-friendly masterclass explaining how every piece of this software fits together in an Indian business context.")

st.markdown("""
Welcome! Even if you have never built a Machine Learning system or a multi-page web dashboard before, 
this guide breaks down **every single concept into simple, digestible steps**.
""")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏗️ 1. Project Architecture",
    "🗄️ 2. Database & CRM Model",
    "🤖 3. The ML Model in INR",
    "💬 4. WhatsApp, UPI & Reminders",
    "🚀 5. How to Run & Extend"
])

with tab1:
    st.subheader("🏗️ Step 1: How the Multi-Page Application Works")
    st.markdown("""
    In modern web development, instead of putting thousands of lines of code into one gigantic file, 
    we organize our software into **specialized modules**.

    Here is the exact structure of your project:
    ```
    Dashboard_1-Invoice_App/
    │
    ├── app.py                      # Main landing hub & CRM action center
    │
    ├── pages/                      # Multi-page directory (Streamlit auto-discovers these!)
    │   ├── 1_📊_Dashboard.py        # Executive receivables KPIs, aging buckets & risk charts (₹)
    │   ├── 2_📄_Invoices.py         # Invoicing table, create invoices & mark payments
    │   ├── 3_🤖_Late_Payment_Predictor.py  # ML risk radar, explanations & simulator in INR
    │   ├── 4_💬_Smart_Reminders.py   # Tone-adjusted WhatsApp (wa.me), UPI & CRM Logger
    │   ├── 5_👥_Customers.py        # Customer CRM profiles, GSTIN, credit limits & timeline
    │   └── 6_🎓_Novice_Guide.py     # This step-by-step interactive learning guide
    │
    ├── database.py                 # SQLite database storage & CRM query helpers
    ├── ml_model.py                 # Scikit-Learn Random Forest late-payer classifier (INR)
    ├── reminder_engine.py          # Message templates, UPI formatting & URL deep-links
    ├── invoicing.db                # The local SQLite database file
    └── late_payer_model.joblib     # Serialized trained machine learning model
    ```

    #### Why Streamlit?
    - **Active Python Backend**: Runs real Python code on a live cloud server.
    - **100% Free**: Hostable on Streamlit Community Cloud without credit cards or subscriptions.
    - **Instant Multi-Page Navigation**: Adding a `.py` file to `pages/` automatically makes it a new page in the navigation bar!
    """)

with tab2:
    st.subheader("🗄️ Step 2: The Database & CRM Data Model")
    st.markdown("""
    All data is stored inside a lightweight, serverless SQLite database (`invoicing.db`). 
    Our system uses **4 interconnected relational tables**:
    """)

    st.markdown("""
    | Table | What it Stores | Why it Matters |
    | :--- | :--- | :--- |
    | `customers` | Name, company, email, WhatsApp phone, GSTIN, Credit Limit (₹), UPI ID, tags | Central CRM directory for client relationship management |
    | `invoices` | Invoice number, issue date, due date, amount in INR (₹), status (`Pending`, `Overdue`, `Paid`) | Active ledger of money owed to your business |
    | `payment_history` | Historical payment dates, delay in days, and flag (`was_late: 0 or 1`) | **Training dataset for the Machine Learning algorithm!** |
    | `crm_interactions`| Outreach channel (WhatsApp, Email, Call), notes, and **Promised Payment Dates** | Complete communication trail so follow-ups never slip through the cracks |
    """)

    st.markdown("""
    #### Starting with a Clean Slate or Testing with Demo Data:
    - **Wipe All Demo Data**: Click **'🧹 Clear All'** in the sidebar at any time to start completely fresh for your real clients.
    - **Load Sample Data**: Click **'🇮🇳 Load Demo'** to load realistic Indian SME records in INR for presentations or portfolio demonstrations.
    """)

with tab3:
    st.subheader("🤖 Step 3: Machine Learning Demystified for Beginners")
    st.markdown("""
    ### What is Machine Learning doing here?
    In traditional programming, you write rigid rules:
    ```python
    # ❌ Rigid Rule:
    if client_delayed_before:
        risk = "High"
    ```
    In reality, payment risk depends on **multiple interacting factors**:
    - Has this client settled 10 invoices on time and delayed only once?
    - Is this an unusually large order (e.g. ₹5,00,000) that requires board approval?
    - Are the payment terms Net-15 or Net-60?

    ### Random Forest Classification:
    Our Machine Learning model builds an ensemble of decision trees analyzing 5 key features:
    1. **`avg_delay`**: Historical average days the client takes to pay past the due date.
    2. **`late_rate`**: Percentage of past invoices that were overdue.
    3. **`total_past_invs`**: Relationship depth (number of completed invoices).
    4. **`amount`**: The invoice total in Indian Rupees (₹).
    5. **`term_days`**: The agreed credit window (Net 15 vs Net 45).

    The model outputs an exact probability (0% to 100%) and categorizes the invoice into:
    - 🟢 **0% to 34% (Low Risk)**: Standard billing workflow.
    - 🟡 **35% to 64% (Medium Risk)**: Send a gentle morning check-in on the due date.
    - 🔴 **65% to 100% (High Risk)**: Proactively follow up 3 days before due date via WhatsApp.
    """)

with tab4:
    st.subheader("💬 Step 4: WhatsApp, UPI & The 1-Click Reminder Engine")
    st.markdown("""
    In India, over 80% of business communication happens over WhatsApp, and payments are settled via UPI or direct NEFT/IMPS bank transfer. 
    Our reminder engine bridges both channels seamlessly:

    ### 1. How WhatsApp 1-Click Works (`wa.me`)
    ```
    https://wa.me/919876543210?text=Hi%20Aarav...%20UPI%20ID:%20bioron@upi
    ```
    Clicking **"🟢 Open in WhatsApp"** opens WhatsApp Web or the WhatsApp Desktop App with:
    - Clean formatting using WhatsApp bold text (`*Invoice #...*`, `*Amount:* ₹1,65,000`).
    - Your **Business UPI ID** and **Bank Account & IFSC code** pre-filled.
    - Zero awkwardness: polite, relationship-preserving wording.

    ### 2. CRM Activity Logging
    Every time you draft a reminder or speak with a customer, click **"Save Activity to Customer CRM Timeline"**:
    - Record payment commitments (e.g. *"Client promised to transfer ₹50,000 by Friday via RTGS"*).
    - Track communication history directly inside their client profile!
    """)

with tab5:
    st.subheader("🚀 Step 5: How to Deploy to GitHub & Streamlit Cloud (100% Free)")
    st.markdown("""
    ### How to Push to GitHub:
    ```powershell
    cd "c:\\Users\\SUDIP ROY\\OneDrive\\Documents\\Bioron Education\\ai-products\\Invoice_app\\Dashboard_1-Invoice_App"
    git add .
    git commit -m "Convert to INR currency, add CRM features, and clean database options"
    git push -u origin main
    ```

    ### How to Deploy on Streamlit Community Cloud:
    1. Visit [**share.streamlit.io**](https://share.streamlit.io/) and log in with your GitHub account.
    2. Click **"New App"** and select repository `Sudip9876/invoice-reminder-assistant`.
    3. Choose branch `main` and main file `app.py`.
    4. Click **"Deploy"**!
    5. Your app is live with an active Python backend, real database, and Scikit-Learn ML predictions!
    """)
