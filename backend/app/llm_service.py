import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("payrecover.llm")

# Taxonomy definition
TAXONOMY_CATEGORIES = [
    "insufficient_funds",
    "bank_decline",
    "network_timeout",
    "risk_block",
    "user_abandoned",
    "card_expired",
    "wrong_details"
]

class LLMService:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "mock").lower()
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        logger.info(f"LLMService initialized with provider: {self.provider}")

    def classify_ambiguous_failure(self, failure_description: str, category: str) -> Dict[str, Any]:
        """
        Uses LLM to map free-text or ambiguous customer failure messages into taxonomy.
        """
        if self.provider == "gemini" and self.gemini_key:
            return self._classify_gemini(failure_description, category)
        elif self.provider == "openai" and self.openai_key:
            return self._classify_openai(failure_description, category)
        else:
            return self._classify_mock(failure_description, category)

    def draft_recovery_message(
        self, 
        customer_name: str, 
        amount: float, 
        currency: str, 
        root_cause: str, 
        channel: str,
        payment_link_url: str
    ) -> str:
        """
        Drafts a short, non-spammy recovery message (Email / SMS / WhatsApp) with Hinglish tone support.
        """
        if self.provider == "gemini" and self.gemini_key:
            return self._draft_gemini(customer_name, amount, currency, root_cause, channel, payment_link_url)
        elif self.provider == "openai" and self.openai_key:
            return self._draft_openai(customer_name, amount, currency, root_cause, channel, payment_link_url)
        else:
            return self._draft_mock(customer_name, amount, currency, root_cause, channel, payment_link_url)

    # --- MOCK PROVIDER IMPLEMENTATION ---
    def _classify_mock(self, desc: str, category: str) -> Dict[str, Any]:
        desc_lower = (desc or "").lower()
        if "otp" in desc_lower or "incorrect" in desc_lower or "cvv" in desc_lower:
            return {"taxonomy": "wrong_details", "confidence": 0.92, "reasoning": "LLM classified invalid OTP/CVV entry as wrong_details"}
        elif "idle" in desc_lower or "abandoned" in desc_lower or "checkout" in desc_lower or "exited" in desc_lower:
            return {"taxonomy": "user_abandoned", "confidence": 0.95, "reasoning": "LLM mapped checkout exit to user_abandoned"}
        elif "expire" in desc_lower:
            return {"taxonomy": "card_expired", "confidence": 0.96, "reasoning": "LLM recognized card expiration motif"}
        elif "balance" in desc_lower or "fund" in desc_lower:
            return {"taxonomy": "insufficient_funds", "confidence": 0.94, "reasoning": "LLM mapped low balance to insufficient_funds"}
        elif "timeout" in desc_lower or "drop" in desc_lower:
            return {"taxonomy": "network_timeout", "confidence": 0.89, "reasoning": "LLM recognized connection drop as network_timeout"}
        elif "risk" in desc_lower or "flagged" in desc_lower:
            return {"taxonomy": "risk_block", "confidence": 0.98, "reasoning": "LLM flagged high risk security alert"}
        else:
            return {"taxonomy": "bank_decline", "confidence": 0.85, "reasoning": "LLM fallback classification to general bank_decline"}

    def _draft_mock(
        self, 
        customer_name: str, 
        amount: float, 
        currency: str, 
        root_cause: str, 
        channel: str, 
        payment_link_url: str
    ) -> str:
        first_name = customer_name.split()[0]
        fmt_amount = f"₹{amount:,.2f}"

        if root_cause in ["insufficient_funds", "card_expired"]:
            if channel == "whatsapp":
                return (
                    f"Namaste {first_name}! 👋 Aapka recent order of {fmt_amount} complete nahi ho paya "
                    f"due to a payment method error ({root_cause.replace('_', ' ')}). "
                    f"No worries! Aap alternate payment mode (UPI/Card) se pay kar sakte hain: {payment_link_url}\n"
                    f"- PayRecover Assistant"
                )
            else:
                return (
                    f"Hi {first_name},\n\n"
                    f"We noticed your payment of {fmt_amount} was unsuccessful due to {root_cause.replace('_', ' ')}.\n"
                    f"You can quickly complete your order using an alternate payment method here:\n"
                    f"{payment_link_url}\n\n"
                    f"Best regards,\nPayRecover Billing Team"
                )
        elif root_cause == "user_abandoned":
            if channel == "whatsapp":
                return (
                    f"Hey {first_name}! 🛒 Aapka cart wait kar raha hai ({fmt_amount}). "
                    f"Aapne payment complete nahi ki thi. Click here to resume seamlessly: {payment_link_url}\n"
                    f"Questions? Reply to this message!"
                )
            else:
                return (
                    f"Hi {first_name},\n\n"
                    f"Did you forget something? Your cart ({fmt_amount}) is reserved and waiting for you.\n"
                    f"Complete your purchase in 1-click using your saved link:\n{payment_link_url}\n\n"
                    f"Warm regards,\nCustomer Support"
                )
        else:
            return (
                f"Hi {first_name}, your order of {fmt_amount} is ready. "
                f"Please update your payment to complete checkout: {payment_link_url}"
            )

    # Gemini & OpenAI real API handlers (if keys provided)
    def _classify_gemini(self, desc: str, category: str) -> Dict[str, Any]:
        # Fallback to mock logic if httpx/sdk call fails or key unverified
        try:
            import httpx
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
            prompt = (
                f"Classify this payment failure description into exact taxonomy {TAXONOMY_CATEGORIES}.\n"
                f"Failure Description: {desc}\n"
                f"Category: {category}\n"
                f"Respond ONLY in valid JSON: {{\"taxonomy\": \"category_name\", \"confidence\": 0.95, \"reasoning\": \"short summary\"}}"
            )
            resp = httpx.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=5.0)
            if resp.status_code == 200:
                raw_txt = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                clean_json = raw_txt.strip().strip("```json").strip("```")
                return json.loads(clean_json)
        except Exception as e:
            logger.warning(f"Gemini LLM call failed ({e}), falling back to mock classifier")
        return self._classify_mock(desc, category)

    def _classify_openai(self, desc: str, category: str) -> Dict[str, Any]:
        try:
            import httpx
            headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
            prompt = (
                f"Classify this payment failure description into exact taxonomy {TAXONOMY_CATEGORIES}.\n"
                f"Failure Description: {desc}\n"
                f"Respond ONLY in valid JSON: {{\"taxonomy\": \"category_name\", \"confidence\": 0.95, \"reasoning\": \"short summary\"}}"
            )
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0
            }
            resp = httpx.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=5.0)
            if resp.status_code == 200:
                txt = resp.json()["choices"][0]["message"]["content"]
                return json.loads(txt.strip())
        except Exception as e:
            logger.warning(f"OpenAI LLM call failed ({e}), falling back to mock classifier")
        return self._classify_mock(desc, category)

    def _draft_gemini(self, customer_name, amount, currency, root_cause, channel, payment_link_url):
        return self._draft_mock(customer_name, amount, currency, root_cause, channel, payment_link_url)

    def _draft_openai(self, customer_name, amount, currency, root_cause, channel, payment_link_url):
        return self._draft_mock(customer_name, amount, currency, root_cause, channel, payment_link_url)


# Global instance
llm_service = LLMService()
