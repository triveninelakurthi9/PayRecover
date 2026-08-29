import logging
from typing import Dict, Any, Tuple
from app.llm_service import llm_service

logger = logging.getLogger("payrecover.diagnosis")

# Direct deterministic mapping dictionary for standard Razorpay error codes
DIRECT_CODE_MAP = {
    "EXPIRED_CARD": ("card_expired", 1.0, "Direct Razorpay Error Code: EXPIRED_CARD"),
    "INSUFFICIENT_FUNDS": ("insufficient_funds", 1.0, "Direct Razorpay Error Code: INSUFFICIENT_FUNDS"),
    "BANK_TECHNICAL_DECLINE": ("bank_decline", 1.0, "Direct Razorpay Error Code: BANK_TECHNICAL_DECLINE"),
    "RISK_CHECK_FAILED": ("risk_block", 1.0, "Direct Razorpay Error Code: RISK_CHECK_FAILED"),
    "INVALID_OTP": ("wrong_details", 1.0, "Direct Razorpay Error Code: INVALID_OTP"),
    "GATEWAY_TIMEOUT": ("network_timeout", 1.0, "Direct Razorpay Error Code: GATEWAY_TIMEOUT"),
    "PAYMENT_CANCELLED": ("user_abandoned", 1.0, "Direct Razorpay Error Code: PAYMENT_CANCELLED"),
    "CHECKOUT_ABANDONED": ("user_abandoned", 1.0, "Direct Checkout Event: CHECKOUT_ABANDONED"),
    "AUTOPAY_MANDATE_DECLINED": ("bank_decline", 1.0, "Direct Subscription Event: AUTOPAY_MANDATE_DECLINED"),
}

class DiagnosisEngine:
    def diagnose(self, failure_code: str, failure_description: str, category: str) -> Dict[str, Any]:
        """
        Diagnoses root cause:
        1. First checks exact Razorpay error subcodes.
        2. If ambiguous or missing, delegates to LLM service.
        """
        code = failure_code or ""
        subcode = code.split(":")[-1] if ":" in code else code

        # Step 1: Direct lookup
        if subcode in DIRECT_CODE_MAP:
            taxonomy, confidence, reasoning = DIRECT_CODE_MAP[subcode]
            return {
                "root_cause": taxonomy,
                "confidence": confidence,
                "reasoning": reasoning,
                "source": "deterministic_code_map"
            }

        # Check subcode substrings
        for key, val in DIRECT_CODE_MAP.items():
            if key in code or key in (failure_description or "").upper():
                return {
                    "root_cause": val[0],
                    "confidence": 0.95,
                    "reasoning": f"Subcode substring match '{key}' in failure code/description",
                    "source": "deterministic_pattern_map"
                }

        # Step 2: LLM fallback for ambiguous / free-text reasons
        logger.info(f"Ambiguous failure code '{failure_code}'. Routing to LLM classifier.")
        llm_res = llm_service.classify_ambiguous_failure(failure_description, category)
        return {
            "root_cause": llm_res.get("taxonomy", "bank_decline"),
            "confidence": llm_res.get("confidence", 0.85),
            "reasoning": f"LLM reasoning: {llm_res.get('reasoning')}",
            "source": "llm_classifier"
        }

# Global instance
diagnosis_engine = DiagnosisEngine()
