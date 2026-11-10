# 💼 Invoice & Payment-Reminder Assistant (INR & CRM Edition)

An intelligent, multi-page web application designed for Indian businesses, agencies, and freelancers to **track invoices**, **manage CRM client relationships**, **forecast late-payment risks using Machine Learning**, and **draft tone-calibrated WhatsApp & Email reminders** featuring UPI and direct bank transfer details.

---

## 🌟 Key Features

1. **📊 Executive Receivables Dashboard (INR)**:
   - High-level KPIs in Indian Rupees (₹): Total Invoiced, Outstanding Balance, Overdue Balance, Collection Efficiency Rate, and At-Risk Capital.
   - **Aging Intervals**: Automatically segments unpaid capital into *Current*, *1-15 Days*, *16-30 Days*, and *30+ Days (Critical)* intervals with interactive Plotly visual charts.
   - **Client Credit Exposure Breakdown**: Identifies top debtors and critical accounts requiring immediate follow-up.

2. **👥 Comprehensive Customer CRM & Credit Management**:
   - Centralized client database with **GSTIN (GST Number)**, contact person, WhatsApp phone, and email.
   - **Credit Limit & Real-time Utilization Meter**: Set an approved credit limit in INR (e.g. ₹2,00,000) and track live credit utilization percentage with visual progress bars.
   - **CRM Communication Timeline**: Audit trails of all client outreach (WhatsApp reminders, email notices, phone calls, and meetings).
   - **Payment Promise Tracker**: Log and track exact dates promised by customers for NEFT/IMPS/UPI clearance.

3. **📄 Complete Tax Invoice Lifecycle (₹)**:
   - Issue GST tax invoices with terms (Net 15/30/45/60) and amounts in INR.
   - Instant search and filters by status (`Pending`, `Overdue`, `Paid`) and ML risk tier.
   - **"Record Payment" Settlement Flow**: Automatically calculates payment delay in days and records it in both the historical ML training set and the CRM activity ledger.
   - **CSV Export**: 1-click download of all invoices for accounting or GST reconciliation.

4. **🤖 Machine Learning Late-Payer Predictor (INR)**:
   - Trained on historical customer settlement habits using a Scikit-Learn **Random Forest Classifier**.
   - Forecasts delinquency risk on the day an invoice is created:
     - 🟢 **Low Risk (0 - 34%)**: Reliable client, standard billing.
     - 🟡 **Medium Risk (35 - 64%)**: Moderate delay chance, friendly check-in recommended.
     - 🔴 **High Risk (65 - 100%)**: Chronic delay expected, proactive outreach required.
   - **Explainable AI**: Highlights exact drivers behind every prediction (e.g., *"Historical delay averages +28 days"*, *"High ticket invoice (₹3,80,000) requires multi-tier finance approval"*).
   - **Interactive What-If Simulator**: Adjust delay, past overdue rate, and invoice amounts (₹10,000 to ₹15,00,000) with real-time gauge feedback.
   - **1-Click Model Retraining**: Fits on new payment records with reported accuracy and feature importance rankings.

5. **💬 Smart WhatsApp & Email Reminder Drafter with UPI & Banking Details**:
   - **4 Calibrated Tones**:
     - *Gentle / Friendly* (warm, relationship-preserving check-in)
     - *Professional / Standard* (clear, objective business notice)
     - *Firm / Assertive* (direct overdue notification with service continuity notice)
     - *Urgent / Final Notice* (formal warning outlining late interest charges or credit hold)
   - **UPI & Bank Transfer Integration**: Formats drafts with your **Business UPI ID** (e.g. `bioron@okhdfcbank`) and **Bank Account & IFSC code**.
   - **1-Click WhatsApp Launch**: Generates direct `https://wa.me/...` deep-links that open WhatsApp Web or Desktop with the message pre-filled.
   - **1-Click Email Launch**: Generates `mailto:...` links opening Outlook, Apple Mail, or Thunderbird with subject and body populated.
   - **Log to CRM**: 1-click button to log the outreach to the customer's CRM history.

6. **🧹 Flexible Data Management (Clean Slate vs Demo)**:
   - **Wipe All Demo Data**: Click **'🧹 Clear All'** in the sidebar at any time to start completely fresh for your real business.
   - **Load Indian Demo Data**: Click **'🇮🇳 Load Demo'** to load realistic Indian SME records in INR for presentations or portfolio demonstrations.

---

## 🗂️ Project Structure

```
Dashboard_1-Invoice_App/
│
├── app.py                             # Main landing page & CRM action hub
│
├── pages/                             # Multi-page application modules
│   ├── 1_📊_Dashboard.py              # Executive financial & aging dashboard (₹)
│   ├── 2_📄_Invoices.py               # Invoices table, new invoice form & payment logger
│   ├── 3_🤖_Late_Payment_Predictor.py # ML risk radar, what-if simulator & retraining (INR)
│   ├── 4_💬_Smart_Reminders.py        # Tone-calibrated WhatsApp (wa.me), UPI & CRM Logger
│   ├── 5_👥_Customers.py              # Customer CRM profiles, GSTIN, credit limits & timeline
│   └── 6_🎓_Novice_Step_by_Step_Guide.py # Beginner tutorial & architecture breakdown
│
├── database.py                        # SQLite database engine, CRM tables & seed data
├── ml_model.py                        # Scikit-learn Random Forest model & explainability
├── reminder_engine.py                 # Tone message generators, UPI & deep-linking URLs
├── invoicing.db                       # Local SQLite database
├── late_payer_model.joblib            # Serialized trained machine learning model
├── requirements.txt                   # Python dependencies
├── run.bat                            # Windows 1-click double-click launcher
└── run.ps1                            # PowerShell launcher
```

---

## 🚀 How to Run Locally

Open your terminal in `Dashboard_1-Invoice_App` and run:

```powershell
# Run Streamlit dashboard
.venv\Scripts\streamlit run app.py
```

Or simply double-click **`run.bat`** in Windows Explorer!
