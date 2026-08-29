from datetime import datetime, timedelta
from typing import Dict, Any, Optional

MAX_ATTEMPTS = 3
COOLDOWN_HOURS = 4

class InterventionRulesEngine:
    def decide_intervention(
        self, 
        root_cause: str, 
        prior_attempts: int, 
        status: str, 
        last_action_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determines the intervention action based on root cause, history, and stopping rules.
        """
        # Rule 1: Terminal state check
        if status in ["recovered", "escalated"]:
            return {
                "action": "none",
                "rule_fired": "RULE_TERMINAL_STATE",
                "allowed": False,
                "reason": f"Case is in terminal state '{status}'. Automated actions are frozen."
            }

        # Rule 2: Max attempts check
        if prior_attempts >= MAX_ATTEMPTS:
            return {
                "action": "escalate_limit_reached",
                "rule_fired": "RULE_MAX_ATTEMPTS_EXCEEDED",
                "allowed": False,
                "reason": f"Max recovery attempts limit ({MAX_ATTEMPTS}) reached for this case. Escalating."
            }

        # Rule 3: Cooldown period check
        if last_action_at:
            try:
                last_time = datetime.fromisoformat(last_action_at)
                elapsed_hours = (datetime.now() - last_time).total_seconds() / 3600.0
                if elapsed_hours < COOLDOWN_HOURS:
                    remaining_min = int((COOLDOWN_HOURS - elapsed_hours) * 60)
                    return {
                        "action": "cooldown_wait",
                        "rule_fired": "RULE_COOLDOWN_ACTIVE",
                        "allowed": False,
                        "reason": f"Cooldown active ({remaining_min}m remaining of {COOLDOWN_HOURS}h requirement)."
                    }
            except ValueError:
                pass  # Parse error fallback, proceed

        # Rule 4: Risk Block Gated Requirement (High Risk - MUST NOT auto-action money)
        if root_cause == "risk_block":
            return {
                "action": "escalate_manual_review",
                "rule_fired": "RULE_RISK_BLOCK_GATED_ESCALATION",
                "allowed": True,
                "reason": "Root cause 'risk_block' detected. Irreversible risk action requires human review queue."
            }

        # Rule 5: Network Timeout / Bank Decline -> Direct Auto-Retry
        if root_cause in ["network_timeout", "bank_decline"]:
            return {
                "action": "auto_retry",
                "rule_fired": "RULE_TRANSIENT_FAILURE_AUTO_RETRY",
                "allowed": True,
                "reason": f"Root cause '{root_cause}' identified as transient gateway error. Executing API auto-retry."
            }

        # Rule 6: Insufficient Funds / Card Expired -> Create Payment Link + Alternate Method Suggestion
        if root_cause in ["insufficient_funds", "card_expired", "wrong_details"]:
            return {
                "action": "send_payment_link",
                "rule_fired": "RULE_PAYMENT_INSTRUMENT_UPDATE_LINK",
                "allowed": True,
                "reason": f"Root cause '{root_cause}' requires updated instrument or alternate mode. Generating Razorpay Payment Link."
            }

        # Rule 7: User Abandoned Checkout -> Nudge / Reminder with Payment Link
        if root_cause == "user_abandoned":
            return {
                "action": "send_reminder_link",
                "rule_fired": "RULE_CHECKOUT_ABANDONMENT_REMINDER",
                "allowed": True,
                "reason": "Customer abandoned checkout. Drafting contextual Hinglish recovery reminder with Payment Link."
            }

        # Fallback default rule
        return {
            "action": "send_payment_link",
            "rule_fired": "RULE_DEFAULT_RECOVERY_LINK",
            "allowed": True,
            "reason": f"Standard recovery intervention for root cause '{root_cause}'."
        }

# Global instance
rules_engine = InterventionRulesEngine()
