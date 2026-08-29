import random
import logging
from datetime import datetime
from app.db import get_db_connection
from app.diagnosis_engine import diagnosis_engine
from app.intervention_rules import rules_engine
from app.razorpay_client import razorpay_client
from app.llm_service import llm_service
from app.audit_logger import audit_logger

logger = logging.getLogger("payrecover.execution")

class ExecutionLayer:
    def process_case(self, case_id: str, inject_failure: bool = False) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"success": False, "message": f"Case {case_id} not found."}

        case = dict(row)
        conn.close()

        # Step 1: Root Cause Diagnosis
        diagnosis = diagnosis_engine.diagnose(
            case["failure_code"], 
            case["failure_description"], 
            case["category"]
        )
        root_cause = diagnosis["root_cause"]
        confidence = diagnosis["confidence"]

        # Step 2: Intervention Decision Logic
        decision = rules_engine.decide_intervention(
            root_cause=root_cause,
            prior_attempts=case["prior_attempts"],
            status=case["status"],
            last_action_at=case["last_action_at"]
        )

        rule_fired = decision["rule_fired"]
        action = decision["action"]
        allowed = decision["allowed"]

        # Handle rules rejection (terminal state, cooldown, max attempts)
        if not allowed:
            if action == "escalate_limit_reached":
                self._update_case_status(case_id, "failed", root_cause, rule_fired, "max_attempts_exceeded")
                audit_logger.log_event(
                    case_id=case_id,
                    root_cause=root_cause,
                    action_taken="escalate_limit_reached",
                    rule_fired=rule_fired,
                    outcome="failed",
                    amount_at_stake=case["amount"],
                    explanation=decision["reason"]
                )
            else:
                audit_logger.log_event(
                    case_id=case_id,
                    root_cause=root_cause,
                    action_taken=action,
                    rule_fired=rule_fired,
                    outcome="skipped",
                    amount_at_stake=case["amount"],
                    explanation=decision["reason"]
                )
            return {"success": True, "case_id": case_id, "action": action, "outcome": "skipped", "reason": decision["reason"]}

        # Step 3: Injected Graceful Failure Demo Case
        if inject_failure:
            error_explanation = (
                f"GRACEFUL FAILURE DEMO INJECTED: Razorpay API Connection Timeout (HTTP 504 Gateway Timeout) "
                f"or LLM Endpoint Unreachable while processing {case_id}. Fallback handler activated."
            )
            logger.warning(error_explanation)
            self._update_case_status(case_id, "pending", root_cause, "RULE_GRACEFUL_FAILURE_FALLBACK", "api_timeout_fallback")
            audit_logger.log_event(
                case_id=case_id,
                root_cause=root_cause,
                action_taken="api_retry_fallback",
                rule_fired="RULE_GRACEFUL_FAILURE_FALLBACK",
                outcome="graceful_failure_handled",
                amount_at_stake=case["amount"],
                explanation=error_explanation,
                raw_details={"error_code": 504, "status": "gateway_timeout", "recovered_by_agent": False}
            )
            return {
                "success": True,
                "case_id": case_id,
                "action": "graceful_failure_handled",
                "outcome": "handled",
                "explanation": error_explanation
            }

        # Step 4: Execute Bounded Action
        new_attempts = case["prior_attempts"] + 1
        now_iso = datetime.now().isoformat()
        outcome = "in_progress"
        new_status = case["status"]
        plink_id = case["razorpay_payment_link_id"]
        plink_url = case["razorpay_payment_link_url"]
        drafted_msg = case["drafted_message"]

        if action == "escalate_manual_review":
            new_status = "escalated"
            outcome = "escalated"
            explanation = f"Gated Rule Fired ({rule_fired}). Case flagged for human security/risk queue. Zero automated payment commands issued."
            audit_logger.log_event(
                case_id=case_id,
                root_cause=root_cause,
                action_taken=action,
                rule_fired=rule_fired,
                outcome=outcome,
                amount_at_stake=case["amount"],
                explanation=explanation
            )

        elif action == "auto_retry":
            retry_res = razorpay_client.attempt_order_retry(case["razorpay_order_id"], case_id, case["amount"])
            # Auto retries convert ~80% of the time on test mode
            if retry_res.get("success") and random.random() < 0.85:
                new_status = "recovered"
                outcome = "recovered"
                explanation = f"Razorpay API Auto-Retry succeeded on order {case['razorpay_order_id']}. Payment authorized."
            else:
                new_status = "retrying"
                outcome = "retry_attempted"
                explanation = f"Razorpay API Auto-Retry attempted on order {case['razorpay_order_id']}. Awaiting bank confirmation."
            
            audit_logger.log_event(
                case_id=case_id,
                root_cause=root_cause,
                action_taken=action,
                rule_fired=rule_fired,
                outcome=outcome,
                amount_at_stake=case["amount"],
                explanation=explanation,
                raw_details=retry_res
            )

        elif action in ["send_payment_link", "send_reminder_link"]:
            link_res = razorpay_client.create_payment_link(
                case_id=case_id,
                amount=case["amount"],
                customer_name=case["customer_name"],
                customer_email=case["customer_email"],
                customer_phone=case["customer_phone"],
                description=f"Recovery for {root_cause}"
            )
            plink_id = link_res.get("payment_link_id")
            plink_url = link_res.get("payment_link_url")

            drafted_msg = llm_service.draft_recovery_message(
                customer_name=case["customer_name"],
                amount=case["amount"],
                currency=case["currency"],
                root_cause=root_cause,
                channel=case["channel_pref"],
                payment_link_url=plink_url
            )

            # High recovery simulation conversion for payment links (65%-75%)
            if random.random() < 0.70:
                new_status = "recovered"
                outcome = "recovered"
                explanation = f"Generated Razorpay Payment Link ({plink_id}). Customer converted and paid via {case['channel_pref']} channel."
            else:
                new_status = "link_sent"
                outcome = "link_sent"
                explanation = f"Generated Razorpay Payment Link ({plink_id}) & drafted {case['channel_pref']} message. Waiting for customer action."

            # Log mock notification to console & audit
            print(f"[MOCK NOTIFICATION SENDER - {case['channel_pref'].upper()}] To: {case['customer_email']} / {case['customer_phone']}\n{drafted_msg}\n")

            audit_logger.log_event(
                case_id=case_id,
                root_cause=root_cause,
                action_taken=action,
                rule_fired=rule_fired,
                outcome=outcome,
                amount_at_stake=case["amount"],
                explanation=explanation,
                raw_details={"payment_link_url": plink_url, "channel": case["channel_pref"], "drafted_message": drafted_msg}
            )

        # Update case record in DB
        self._update_full_case_record(
            case_id=case_id,
            status=new_status,
            root_cause=root_cause,
            confidence=confidence,
            rule_fired=rule_fired,
            last_action=action,
            last_action_at=now_iso,
            prior_attempts=new_attempts,
            plink_id=plink_id,
            plink_url=plink_url,
            drafted_msg=drafted_msg
        )

        return {
            "success": True,
            "case_id": case_id,
            "root_cause": root_cause,
            "action": action,
            "outcome": outcome,
            "status": new_status,
            "payment_link_url": plink_url,
            "drafted_message": drafted_msg
        }

    def process_all_batch(self, inject_failure_id: str = None) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM cases ORDER BY id ASC;")
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            c_id = r["id"]
            should_inject = (c_id == inject_failure_id)
            res = self.process_case(c_id, inject_failure=should_inject)
            results.append(res)

        return {"processed_count": len(results), "results": results}

    def _update_case_status(self, case_id, status, root_cause, rule_fired, last_action):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cases 
            SET status = ?, root_cause = ?, rule_fired = ?, last_action = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
        """, (status, root_cause, rule_fired, last_action, case_id))
        conn.commit()
        conn.close()

    def _update_full_case_record(self, case_id, status, root_cause, confidence, rule_fired, last_action, last_action_at, prior_attempts, plink_id, plink_url, drafted_msg):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cases 
            SET status = ?, root_cause = ?, confidence = ?, rule_fired = ?, last_action = ?,
                last_action_at = ?, prior_attempts = ?, razorpay_payment_link_id = ?,
                razorpay_payment_link_url = ?, drafted_message = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
        """, (status, root_cause, confidence, rule_fired, last_action, last_action_at, prior_attempts, plink_id, plink_url, drafted_msg, case_id))
        conn.commit()
        conn.close()

# Global instance
execution_layer = ExecutionLayer()
