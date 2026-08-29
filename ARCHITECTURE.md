# PayRecover System Architecture

PayRecover is an autonomous, explainable AI revenue recovery agent designed for Razorpay merchants (Track 03 - Razorpay AI Buildathon). It systematically recovers lost revenue from degraded payments, checkout abandonments, and subscription failures.

---

## High-Level Pipeline Flow

```
+-------------------------------------------------------------------------------+
|                               1. INPUT DATASET                                |
|          50+ Synthetic Cases (Degradation, Abandonment, Subscription)         |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                       2. ROOT-CAUSE DIAGNOSIS ENGINE                          |
|  - Deterministic Code Lookup (EXPIRED_CARD, INSUFFICIENT_FUNDS, RISK_BLOCK)   |
|  - LLM Classifier Fallback for ambiguous/free-text failure descriptions       |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                      3. INTERVENTION DECISION ENGINE                          |
|  - Deterministic Rules Tree (No LLM black-box money decisions)                |
|  - Stopping Rules Enforcement (Max 3 attempts, 4h cooldown, risk block gate)   |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                             4. EXECUTION LAYER                                |
|  - Razorpay TEST MODE API (Orders API, Payment Links API)                     |
|  - LLM Notification Drafting (Email / SMS / WhatsApp Hinglish tone)           |
|  - Graceful Exception Handler (HTTP 504 Timeout Fallback)                     |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                       5. AUDIT TRAIL & DISPLAY LEDGER                         |
|  - SQLite `cases` state table + `audit_logs` explainability ledger            |
|  - Vite React Real-time Dashboard with visual recovery analytics              |
+-------------------------------------------------------------------------------+
```

---

## 1. Diagnosis Taxonomy Engine (`diagnosis_engine.py`)

Every incoming case is mapped into one of 7 standardized failure taxonomy buckets:
1. `insufficient_funds`: Bank balance low or card limit exceeded.
2. `bank_decline`: Technical bank server error or mandate authorization decline.
3. `network_timeout`: Mid-transaction gateway network disconnect.
4. `risk_block`: High-risk fraud check failure or IP block.
5. `user_abandoned`: Checkout window closed prior to authentication.
6. `card_expired`: Saved payment card expiration.
7. `wrong_details`: Invalid OTP, incorrect CVV, or authentication error.

### Code vs. LLM Responsibilities
- **Direct Error Lookup**: If Razorpay returns a known test code (`BAD_REQUEST_ERROR:EXPIRED_CARD`, `GATEWAY_ERROR:INSUFFICIENT_FUNDS`, `RISK_CHECK_FAILED`), the engine assigns taxonomy with **100% confidence** deterministically.
- **LLM Classifier Fallback**: If failure data contains free-text or ambiguous customer logs, the LLM service (`llm_service.py`) analyzes the text, assigns the taxonomy category, and returns confidence + reasoning.

---

## 2. Deterministic Intervention Rules (`intervention_rules.py`)

Interventions are driven by explicit deterministic rules—**never by unguided LLM outputs**:

| Root Cause | Rule Fired | Interventions Triggered |
| :--- | :--- | :--- |
| `insufficient_funds` / `card_expired` | `RULE_PAYMENT_INSTRUMENT_UPDATE_LINK` | Create Razorpay Payment Link with alternate payment method suggestion |
| `network_timeout` / `bank_decline` | `RULE_TRANSIENT_FAILURE_AUTO_RETRY` | Trigger backend Razorpay API order retry |
| `user_abandoned` | `RULE_CHECKOUT_ABANDONMENT_REMINDER` | Draft Hinglish recovery reminder with Payment Link |
| `risk_block` | `RULE_RISK_BLOCK_GATED_ESCALATION` | **GATED RULE**: Escalate to human security queue (0 auto action) |

---

## 3. Stopping Rules (Hard Safety Boundaries)

Located in `backend/app/intervention_rules.py`:

1. **Maximum Attempts Rule (`prior_attempts >= 3`)**:
   - Every case is bounded by a maximum of 3 recovery interventions. Once exceeded, the agent stops automated interventions and flags the case as `failed` / escalated.
2. **Cooldown Requirement (`COOLDOWN_HOURS = 4`)**:
   - A minimum 4-hour wait window is enforced between consecutive attempts on the same case. Rapid retries are prevented.
3. **Terminal State Lockdown**:
   - Once a case achieves `recovered` or `escalated` status, automated rules freeze further execution on that case.
4. **Risk Block Gate**:
   - Cases categorized as `risk_block` are strictly forbidden from automated retry/payment link generation. They are routed directly to the human review queue.

---

## 4. Execution & Audit Explainability

Every single execution writes an immutable record to the SQLite `audit_logs` table:
```json
{
  "case_id": "PAY-0014",
  "timestamp": "2026-08-29T08:18:00",
  "root_cause": "insufficient_funds",
  "action_taken": "send_payment_link",
  "rule_fired": "RULE_PAYMENT_INSTRUMENT_UPDATE_LINK",
  "outcome": "recovered",
  "amount_at_stake": 4999.00,
  "explanation": "Generated Razorpay Payment Link (plink_9a87f1). Customer converted via WhatsApp channel.",
  "raw_details": "..."
}
```

---

## 5. Graceful Failure Handling

The agent contains explicit exception handling (`ExecutionLayer.process_case(..., inject_failure=True)`). If a downstream Razorpay API or LLM endpoint experiences a timeout or network drop:
- The exception is caught cleanly without crashing the web process.
- The case status transitions to a safe state (`pending` / `retrying`).
- A `RULE_GRACEFUL_FAILURE_FALLBACK` audit log entry is written.
- The UI displays an explicit alert banner showing how the error was safely mitigated.
