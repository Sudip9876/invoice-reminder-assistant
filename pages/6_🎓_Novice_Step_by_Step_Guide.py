"""
pages/6_🎓_Novice_Step_by_Step_Guide.py - Step-by-Step Novice Learning Guide
A complete beginner guide explaining every layer of the application: database, ML, reminders, and UI.
"""

import streamlit as st

st.set_page_config(page_title="Novice Step-by-Step Guide", page_icon="🎓", layout="wide")

st.title("🎓 Novice Guide: Building & Understanding the App Step-by-Step")
st.caption("A beginner-friendly masterclass explaining how every piece of this software fits together.")

st.markdown("""
Welcome! Even if you have never built a Machine Learning system or a multi-page web dashboard before, 
this guide breaks down **every single concept into simple, digestible steps**.
""")

# Step Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏗️ 1. Project Architecture",
    "🗄️ 2. Database & Data Model",
    "🤖 3. The ML Model Explained",
    "💬 4. WhatsApp & Email Engine",
    "🚀 5. How to Run & Extend"
])

# STEP 1: ARCHITECTURE
with tab1:
    st.subheader("🏗️ Step 1: How the Multi-Page Application Works")
    st.markdown("""
    In modern web development, instead of putting thousands of lines of code into one gigantic file, 
    we organize our software into **specialized modules**.

    Here is the exact structure of your project:
    ```
    Invoice_app/
    │
    ├── app.py                      # Main homepage & central navigation hub
    │
    ├── pages/                      # Multi-page directory (Streamlit auto-discovers these!)
    │   ├── 1_📊_Dashboard.py        # Executive receivables KPIs, aging buckets & risk charts
    │   ├── 2_📄_Invoices.py         # Invoicing table, create invoices & mark payments
    │   ├── 3_🤖_Late_Payment_Predictor.py  # ML risk radar, explanations & simulator
    │   ├── 4_💬_Smart_Reminders.py   # Tone-adjusted WhatsApp (wa.me) & Email drafter
    │   ├── 5_👥_Customers.py        # Customer directory & reliability scorecards
    │   └── 6_🎓_Novice_Guide.py     # This step-by-step interactive learning guide
    │
    ├── database.py                 # SQLite database storage & query helpers
    ├── ml_model.py                 # Scikit-Learn Random Forest late-payer classifier
    ├── reminder_engine.py          # Message templates, tone rules & URL deep-links
    ├── invoicing.db                # The local SQLite database file
    └── late_payer_model.joblib     # Serialized trained machine learning model
    ```

    #### Why Streamlit?
    - **Zero Web Bloat**: You don't need to configure React, Webpack, Node proxies, or complex CSS.
    - **Python Native**: Your data analysis, Machine Learning model, and user interface speak the exact same language (Python).
    - **Multi-Page by Convention**: Adding a new page is as easy as creating a file in `pages/`!
    """)

# STEP 2: DATABASE & DATA MODEL
with tab2:
    st.subheader("🗄️ Step 2: The Database & Relational Data Model")
    st.markdown("""
    All data is stored inside a lightweight, serverless SQLite database (`invoicing.db`). 
    SQLite requires **no configuration, no separate database server**, and stores everything in a single portable file.

    Our database uses **3 interconnected tables**:
    """)

    st.markdown("""
    | Table | What it Stores | Why it Matters |
    | :--- | :--- | :--- |
    | `customers` | Client name, company, email, phone number | The central contact directory for reminders |
    | `invoices` | Invoice number, issue date, due date, amount, status (`Pending`, `Overdue`, `Paid`) | The active ledger of money owed to your business |
    | `payment_history` | Historical payments, actual delay in days, and a boolean flag (`was_late: 0 or 1`) | **The training dataset for our Machine Learning algorithm!** |
    """)

    st.markdown("""
    #### The Closed-Loop Feedback Cycle:
    1. You issue an invoice (`invoices` table).
    2. When the customer settles, you click **"Mark as Paid"** on the Invoices page.
    3. The system calculates: `delay_days = payment_date - due_date`.
    4. If `delay_days > 5`, it sets `was_late = 1`.
    5. This record is permanently appended to `payment_history`.
    6. When you click **"Retrain Model"**, the AI learns from this new transaction!
    """)

# STEP 3: THE ML MODEL EXPLAINED
with tab3:
    st.subheader("🤖 Step 3: Machine Learning Demystified for Beginners")
    st.markdown("""
    ### What is Machine Learning actually doing here?
    In traditional programming, you write fixed `if/else` rules:
    ```python
    # ❌ Rigid Traditional Rule:
    if customer_delay > 10:
        risk = "High"
    ```
    However, real business risk depends on **multiple interacting factors**! 
    For example:
    - What if a customer pays 5 days late, but this is a **huge $20,000 invoice** with **Net-60 terms**?
    - What if a customer was late once, but has paid on time for **10 consecutive invoices**?

    ### Enter Random Forest Classification:
    Our Machine Learning model (`RandomForestClassifier` from Scikit-Learn) builds a **forest of decision trees**. 
    Each tree examines combinations of 5 features:
    
    1. **`avg_delay`**: Historical average days the client takes to pay after the due date.
    2. **`late_rate`**: Percentage of past invoices that were overdue.
    3. **`total_past_invs`**: How many invoices we have completed with this client.
    4. **`amount`**: The dollar amount of the current invoice.
    5. **`term_days`**: The credit window (e.g. Net 15 vs Net 45).

    #### How Probability Becomes Actionable:
    """)

    st.markdown("""
    - 🟢 **0% to 34% (Low Risk)**: Standard billing. Do not pester the customer.
    - 🟡 **35% to 64% (Medium Risk)**: Send a gentle polite check-in on the due date morning.
    - 🔴 **65% to 100% (High Risk)**: Proactively reach out 3 days before the due date via WhatsApp.
    """)

# STEP 4: WHATSAPP & EMAIL ENGINE
with tab4:
    st.subheader("💬 Step 4: How the 1-Click Reminder Engine Works")
    st.markdown("""
    Small business owners hate following up on payments because it feels awkward or aggressive. 
    Our reminder engine solves this using **Tone Calibration** and **Direct Deep-Linking**.

    ### 1. How WhatsApp 1-Click Works (`wa.me`)
    WhatsApp provides a global URL scheme. When formatted correctly:
    ```
    https://wa.me/<country_code><phone_number>?text=<url_encoded_message>
    ```
    When you click our **"🟢 Open in WhatsApp"** button:
    1. The app sanitizes the phone number (removes spaces, dashes).
    2. It URL-encodes special characters (spaces become `%20`, newlines become `%0A`).
    3. It launches WhatsApp Web (on desktop) or the WhatsApp Mobile App with the message already filled in!
    4. You only have to hit **Send**.

    ### 2. How Email 1-Click Works (`mailto:`)
    Similarly, modern operating systems support the `mailto:` protocol:
    ```
    mailto:client@example.com?subject=Invoice%20Reminder&body=Dear%20Client...
    ```
    Clicking **"✉️ Open in Email Client"** instantly opens Outlook, Apple Mail, or Thunderbird with the subject line, customer email, and body text pre-populated.

    ### 3. The 4 Tone Presets:
    - **Gentle / Friendly**: Emphasizes partnership and warm relationships.
    - **Professional / Standard**: Factual, formal, summary of invoice and due date.
    - **Firm / Assertive**: Highlights service continuation and requested remittance date.
    - **Urgent / Final Notice**: For severe overdue invoices or chronic defaulters.
    """)

# STEP 5: HOW TO RUN & EXTEND
with tab5:
    st.subheader("🚀 Step 5: How to Run, Test, and Extend the Project")
    st.markdown("""
    ### How to Run this Application Anytime
    Open your terminal in this project folder and run:
    ```bash
    # 1. Activate the virtual environment
    .venv\\Scripts\\activate

    # 2. Run the Streamlit web app
    streamlit run app.py
    ```
    *(We also created a 1-click startup script: simply double-click `run.bat` in Windows Explorer!)*

    ### How to Extend this Project for Production
    Now that your core application is complete, here are 3 exciting ways to extend it:
    
    1. **Online Payment Gateway (Stripe / Razorpay)**:
       - Generate dynamic payment links and insert them directly into the reminder text.
       - Use a webhook to automatically mark invoices as Paid when payment succeeds!
    
    2. **Automated WhatsApp via Meta Cloud API / Twilio**:
       - Instead of clicking the link manually, you can set up a scheduled background cron job to send reminders automatically.
    
    3. **Cloud Deployment**:
       - You can deploy this repository to **Streamlit Community Cloud** or **Railway** for free so you can access your dashboard from your smartphone anywhere in the world!
    """)
