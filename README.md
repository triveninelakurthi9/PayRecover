# 🛡️ PayRecover — AI Revenue Recovery Agent

**Razorpay AI Buildathon — Track 03 (AI Revenue Recovery Agent)**

PayRecover is an autonomous, explainable AI agent that diagnoses failed payments, abandoned checkouts, and recurring billing failures, chooses bounded recovery interventions using a deterministic rules engine, executes payment links & retries via Razorpay TEST MODE APIs, and tracks full audit metrics on a real-time dashboard.

## 🔗 Live Demo

- **Live Dashboard:** https://frontend-three-roan-je5msy1mbk.vercel.app/
- **Backend API Docs:** https://payrecover-backend.onrender.com/docs

> ⚠️ **Note:** The backend runs on Render's free tier, which spins down after inactivity. The first request after a period of inactivity may take **30–50 seconds** to wake up — this is expected, not a bug. Just wait and refresh.


## 📸 Dashboard Overview & Features

- **Batch Performance Analytics:** Total Cases Processed, Amount at Risk (₹), Amount Recovered (₹), Recovery Rate %, Escalated Queue Count, and Average Time-to-Recovery.
- **Root-Cause Taxonomy Engine:** Classifies error codes (EXPIRED_CARD, INSUFFICIENT_FUNDS, RISK_CHECK_FAILED, GATEWAY_TIMEOUT, CHECKOUT_ABANDONED) via direct lookup with LLM fallback for free-text messages.
- **Deterministic Intervention Rules:** Strict stopping rules (max 3 attempts, 4h cooldown period, gated manual review for high-risk blocks).
- **Hinglish Notification Generator:** Drafts short, contextual SMS, Email, and WhatsApp messages formatted for Indian checkout contexts.
- **Explainable Audit Ledger:** Modal timeline inspecting step-by-step reasoning (Why Chosen, Rule Fired, Raw Payloads) for every transaction.
- **Graceful Failure Handler:** Live demo button showing how API timeouts/LLM drops are safely handled without server crashes.

## 🏗️ Architecture Diagram

                   +-----------------------------------+
                   |    Synthetic Seed Generator       |
                   |  (60+ Realistic Test Cases DB)    |
                   +-----------------+-----------------+
                                     |
                                     v
                   +-----------------+-----------------+
                   |    Root-Cause Diagnosis Engine    |
                   | (Direct Code Map + LLM Fallback)  |
                   +-----------------+-----------------+
                                     |
                                     v
                   +-----------------+-----------------+
                   | Deterministic Rules Engine        |
                   | - Max 3 Attempts                  |
                   | - 4h Cooldown Window              |
                   | - Risk Block Human Escalation     |
                   +-----------------+-----------------+
                                     |
                                     v
                   +-----------------+-----------------+
                   |       Execution Layer             |
                   | - Razorpay Test Orders/Links API  |
                   | - Hinglish Notification Stubs     |
                   | - Graceful Timeout Fallback       |
                   +-----------------+-----------------+
                                     |
                                     v
                   +-----------------+-----------------+
                   |    SQLite Ledger & Audit Logs     |
                   | - Full Case State (cases)         |
                   | - Explainability (audit_logs)     |
                   +-----------------+-----------------+
                                     |
                                     v
                   +-----------------+-----------------+
                   |   Vite React Single-Page Dashboard|
                   +-----------------------------------+

## 🚀 Quickstart & How to Run (Local Dev)

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm

### 1. Setup & Launch Backend (FastAPI)

    cd backend
    python -m venv venv
    venv\Scripts\activate        # Windows
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000

Backend API will run at http://127.0.0.1:8000.

### 2. Setup & Launch Frontend (Vite + React)

    cd frontend
    npm install
    npm run dev

Dashboard will open at http://localhost:3000.

## 🧪 Running the Demo End-to-End

1. **View Initial Seed Data:** Open the dashboard. You'll see 60+ synthetic cases pre-populated across Payment Degradation, Checkout Abandonment, and Subscription Failure.
2. **Execute Full Batch Agent:** Click "Run Batch Agent (50+ Cases)". The agent processes all cases through the diagnosis → decision → execution pipeline. Watch Amount Recovered, Recovery Rate %, and Escalated Queue update live.
3. **Inspect Audit Trail:** Click "Audit Log" next to any case. Inspect the exact rule matched, Razorpay test payment link URL, and LLM Hinglish draft notification.
4. **Trigger Graceful Failure Demo:** Click "Demo Graceful Failure". The agent simulates an API Gateway Timeout on a target case, handles the error gracefully without crashing, logs the fallback event, and displays a success banner.

## ⚙️ Environment Variables

**Backend** (backend/.env):

    RAZORPAY_KEY_ID=rzp_test_your_key_id
    RAZORPAY_KEY_SECRET=your_test_key_secret
    GEMINI_API_KEY=your_gemini_api_key
    OPENAI_API_KEY=your_openai_api_key
    LLM_PROVIDER=mock

**Frontend** (frontend/.env for local dev, frontend/.env.production for deploys):

    VITE_API_BASE_URL=http://127.0.0.1:8000
    # production: VITE_API_BASE_URL=https://payrecover-backend.onrender.com

## 📁 Repository Structure

    payrecover/
    ├── README.md
    ├── ARCHITECTURE.md
    ├── seed_data/
    │   └── synthetic_cases.json
    ├── backend/
    │   ├── app/
    │   │   ├── main.py
    │   │   ├── db.py
    │   │   ├── models.py
    │   │   ├── seed_generator.py
    │   │   ├── diagnosis_engine.py
    │   │   ├── intervention_rules.py
    │   │   ├── execution_layer.py
    │   │   ├── razorpay_client.py
    │   │   ├── llm_service.py
    │   │   └── audit_logger.py
    │   ├── tests/
    │   │   └── test_rules.py
    │   ├── requirements.txt
    │   └── .env.example
    └── frontend/
        ├── index.html
        ├── vite.config.js
        ├── package.json
        └── src/
            ├── App.jsx
            ├── index.css
            ├── config.js
            └── components/
                ├── StatsOverview.jsx
                ├── ControlPanel.jsx
                ├── CasesTable.jsx
                ├── AuditModal.jsx
                └── FailureDemoBanner.jsx

## 🧪 Test Coverage

7/7 automated tests passing (pytest tests/test_rules.py -v):
- Synthetic seed generation
- Deterministic diagnosis classification
- Risk-block gated escalation (zero automated money movement)
- Stopping rule: max attempts
- Stopping rule: terminal state freeze
- Stopping rule: 4-hour cooldown enforcement
- Graceful failure injection handling

## 🛡️ License & Acknowledgments

Built for the Razorpay AI Buildathon (Track 03 — AI Revenue Recovery).
