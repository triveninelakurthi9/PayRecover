# 🛡️ PayRecover — AI Revenue Recovery Agent
> **Razorpay AI Buildathon — Track 03 (AI Revenue Recovery Agent)**

PayRecover is an autonomous, explainable AI agent that diagnoses failed payments, abandoned checkouts, and recurring billing failures, chooses bounded recovery interventions using a deterministic rules engine, executes payment links & retries via **Razorpay TEST MODE APIs**, and tracks full audit metrics on a real-time dashboard.

---

## 📸 Dashboard Overview & Features

- **Batch Performance Analytics**: Total Cases Processed, Amount at Risk (₹), Amount Recovered (₹), Recovery Rate %, Escalated Queue Count, and Average Time-to-Recovery.
- **Root-Cause Taxonomy Engine**: Classifies error codes (`EXPIRED_CARD`, `INSUFFICIENT_FUNDS`, `RISK_CHECK_FAILED`, `GATEWAY_TIMEOUT`, `CHECKOUT_ABANDONED`) via direct lookup with LLM fallback for free-text messages.
- **Deterministic Intervention Rules**: Strict stopping rules (max 3 attempts, 4h cooldown period, gated manual review for high-risk blocks).
- **Hinglish Notification Generator**: Drafts short, contextual SMS, Email, and WhatsApp messages formatted for Indian checkout contexts.
- **Explainable Audit Ledger**: Modal timeline inspecting step-by-step reasoning (`Why Chosen`, `Rule Fired`, `Raw Payloads`) for every transaction.
- **Graceful Failure Handler**: Live demo button showing how API timeouts/LLM drops are safely handled without server crashes.

---

## 🏗️ Architecture Diagram

```
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
                       | - Full Case State (`cases`)       |
                       | - Explainability (`audit_logs`)   |
                       +-----------------+-----------------+
                                         |
                                         v
                       +-----------------+-----------------+
                       |   Vite React Single-Page Dashboard|
                       +-----------------------------------+
```

---

## 🚀 Quickstart & How to Run

### Prerequisites
- Python 3.9+
- Node.js 18+ and `npm`

### 1. Setup & Launch Backend (FastAPI)

```bash
cd backend

# Create virtual environment (optional)
python -m venv venv
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload --port 8000
```
Backend API will run at `http://127.0.0.1:8000`.

### 2. Setup & Launch Frontend (Vite + React)

Open a new terminal window:

```bash
cd frontend

# Install frontend dependencies
npm install

# Start Vite dev server
npm run dev
```
Dashboard will open at `http://localhost:3000`.

---

## 🧪 Running the Demo End-to-End

1. **View Initial Seed Data**: Open `http://localhost:3000`. You will see 60+ synthetic cases pre-populated across Payment Degradation, Checkout Abandonment, and Subscription Failure.
2. **Execute Full Batch Agent**: Click the **"Run Batch Agent (50+ Cases)"** button at the top of the dashboard.
   - The agent will process all cases through the diagnosis -> decision -> execution pipeline.
   - Watch the **Amount Recovered**, **Recovery Rate %**, and **Escalated Queue** numbers update live!
3. **Inspect Audit Trail**: Click **"Audit Log"** next to any case (e.g. `PAY-0004` or `PAY-0014`). Inspect the exact rule matched, Razorpay test payment link URL, and LLM Hinglish draft notification.
4. **Trigger Graceful Failure Demo**: Click **"Demo Graceful Failure"**.
   - The agent will simulate an external API Gateway Timeout (HTTP 504) on target case `PAY-0042`.
   - The system handles the error gracefully without crashing, logs the fallback event to the audit trail, and displays the **Agent Fallback Successful** alert banner.

---

## ⚙️ Environment Variables (Optional)

Configure `backend/.env` if you want to connect real Razorpay Test keys or Gemini / OpenAI LLM keys:

```env
# Optional Razorpay Test Mode Credentials (Simulator active if blank)
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_test_key_secret

# Optional LLM API Configuration (Mock LLM classifier active if blank)
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
LLM_PROVIDER=mock  # Options: mock, gemini, openai
```

---

## 📁 Repository Structure

```
payrecover/
├── README.md                  # Project overview & demo guide
├── ARCHITECTURE.md            # In-depth architectural pipeline documentation
├── seed_data/
│   └── synthetic_cases.json   # Seed dataset of 60+ cases
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI router & endpoint logic
│   │   ├── db.py              # SQLite connection & schema initialization
│   │   ├── models.py          # Pydantic data schemas
│   │   ├── seed_generator.py  # Synthetic case generator
│   │   ├── diagnosis_engine.py# Root-cause taxonomy classifier
│   │   ├── intervention_rules.py # Deterministic rules & stopping boundaries
│   │   ├── execution_layer.py # Razorpay integration & action executor
│   │   ├── razorpay_client.py # Razorpay Test Mode API client & simulator
│   │   ├── llm_service.py     # Gemini / OpenAI / Mock LLM wrapper
│   │   └── audit_logger.py    # Structured audit trail logger
│   ├── tests/
│   │   └── test_rules.py      # Automated pytest unit test suite
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── App.jsx            # Main dashboard component
        ├── index.css          # Dark glassmorphic design system
        └── components/
            ├── StatsOverview.jsx
            ├── ControlPanel.jsx
            ├── CasesTable.jsx
            ├── AuditModal.jsx
            └── FailureDemoBanner.jsx
```

---

## 🛡️ License & Acknowledgments
Built for **Razorpay AI Buildathon (Track 03 - AI Revenue Recovery Agent)**.
