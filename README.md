# 💼 Invoice & Payment-Reminder Assistant (Multi-Page AI App)

An intelligent, multi-page web application designed for small businesses and freelancers to **track invoices**, **forecast late payment risks using Machine Learning**, and **draft tone-calibrated WhatsApp & Email reminders** with 1-click delivery links.

---

## 🌟 Key Features

1. **📊 Executive Receivables Dashboard**:
   - High-level KPIs: Total Invoiced, Outstanding Balance, Overdue Balance, Collection Efficiency Rate, and At-Risk Capital.
   - **Aging Buckets**: Automatically segments unpaid capital into *Current*, *1-15 Days*, *16-30 Days*, and *30+ Days (Critical)* intervals with interactive Plotly visual charts.
   - **Client Exposure Breakdown**: Identifies top debtors and critical accounts requiring immediate follow-up.

2. **📄 Complete Invoice Lifecycle Management**:
   - Track invoice number, customer company, issue date, due date, terms (Net 15/30/45/60), and amount.
   - Instant search and filters by status (`Pending`, `Overdue`, `Paid`) and ML risk tier.
   - **"Record Payment" Settlement Flow**: Automatically calculates payment delay in days and records it in the historical training set so the AI continuously learns.
   - **CSV Export**: 1-click download of all invoices for accounting or spreadsheet reconciliation.

3. **🤖 Machine Learning Late-Payer Predictor**:
   - Trained on historical customer settlement habits using a Scikit-Learn **Random Forest Classifier**.
   - Forecasts risk on the day an invoice is created:
     - 🟢 **Low Risk (0 - 34%)**: Reliable client, standard billing.
     - 🟡 **Medium Risk (35 - 64%)**: Moderate delay chance, friendly check-in recommended.
     - 🔴 **High Risk (65 - 100%)**: Chronic delay expected, proactive outreach required.
   - **Explainable AI**: Highlights exact drivers behind every prediction (e.g., *"Historical delay averages +28 days"*, *"Invoice amount ($5,500) exceeds typical approvals"*).
   - **Interactive What-If Simulator**: Adjust delay, past overdue rate, and invoice amounts with real-time gauge feedback.
   - **1-Click Model Retraining**: Fits on new payment records with reported accuracy and feature importance rankings.

4. **💬 Smart WhatsApp & Email Reminder Drafter**:
   - **4 Calibrated Tones**:
     - *Gentle / Friendly* (warm, relationship-preserving check-in)
     - *Professional / Standard* (clear, objective business notice)
     - *Firm / Assertive* (direct overdue notification with service continuity notice)
     - *Urgent / Final Notice* (formal warning outlining late fees/escalation)
   - **1-Click WhatsApp Launch**: Generates direct `https://wa.me/...` deep-links that open WhatsApp Web or Desktop with the message pre-filled.
   - **1-Click Email Launch**: Generates `mailto:...` links opening Outlook, Apple Mail, or Thunderbird with subject and body populated.

5. **👥 Customer Directory & Reliability Scorecards**:
   - Complete client roster with contact info (email, WhatsApp phone with country code).
   - Star reliability ratings based on historical settlement records (e.g. `⭐⭐⭐⭐⭐ Perfect Payer` vs `⚠️ Chronic Late Payer`).
   - Deep-dive payment history audit log for every client.

6. **🎓 Interactive Novice Step-by-Step Guide**:
   - Dedicated in-app guide explaining the architecture, the database schema, how the ML model works under the hood, and how to extend it.

---

## 🗂️ Project Structure

```
Invoice_app/
│
├── app.py                             # Main landing page & navigation hub
│
├── pages/                             # Multi-page application modules
│   ├── 1_📊_Dashboard.py              # Executive financial & aging dashboard
│   ├── 2_📄_Invoices.py               # Invoices table, new invoice form & payment logger
│   ├── 3_🤖_Late_Payment_Predictor.py # ML risk radar, what-if simulator & retraining
│   ├── 4_💬_Smart_Reminders.py        # Tone-calibrated WhatsApp & Email drafter
│   ├── 5_👥_Customers.py              # Customer directory & reliability cards
│   └── 6_🎓_Novice_Step_by_Step_Guide.py # Beginner tutorial & architecture breakdown
│
├── database.py                        # SQLite database engine, tables & seed data
├── ml_model.py                        # Scikit-learn Random Forest model & explainability
├── reminder_engine.py                 # Tone message generators & deep-linking URLs
├── invoicing.db                       # Local SQLite database (pre-seeded with 8 clients)
├── late_payer_model.joblib            # Serialized trained machine learning model
├── requirements.txt                   # Python dependencies
├── run.bat                            # Windows 1-click double-click launcher
└── run.ps1                            # PowerShell launcher
```

---

## 🚀 How to Run the App (Step-by-Step)

### Option A: The Easiest 1-Click Method (Windows)
Simply double-click **`run.bat`** in this folder! It will activate your Python virtual environment and launch the browser automatically.

### Option B: Terminal / Command Prompt
Open your terminal in this directory and execute:

```powershell
# 1. Run via the virtual environment directly
.venv\Scripts\streamlit run app.py
```

Your browser will automatically open:
```
Local URL: http://localhost:8501
```

---

## 🧠 How the Machine Learning Model Works

1. **Input Features**:
   - `avg_delay`: Customer's past average days late.
   - `late_rate`: Ratio of past invoices paid late.
   - `total_past_invs`: Number of prior completed transactions.
   - `amount`: Dollar value of the current invoice.
   - `term_days`: Payment terms allowed (e.g. 15, 30, 45, 60 days).

2. **Classification & Output**:
   The `RandomForestClassifier` calculates the exact probability of delinquency. High probabilities trigger proactive early alerts, preventing cash-flow bottlenecks before they happen.

3. **Continuous Retraining**:
   Whenever an invoice is marked as Paid, its actual payment delay is saved into `payment_history`. Clicking **"Retrain Model Now"** updates the algorithm with the latest data!
