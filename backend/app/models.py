from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CaseModel(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    category: str  # payment_degradation, checkout_abandonment, subscription_failure
    amount: float
    currency: str = "INR"
    timestamp: str
    failure_code: Optional[str] = None
    failure_description: Optional[str] = None
    payment_method: Optional[str] = None
    prior_attempts: int = 0
    channel_pref: str = "email"
    status: str = "pending"  # pending, retrying, link_sent, escalated, recovered, failed
    root_cause: Optional[str] = None
    confidence: Optional[float] = 1.0
    rule_fired: Optional[str] = None
    last_action: Optional[str] = None
    last_action_at: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    razorpay_payment_link_id: Optional[str] = None
    razorpay_payment_link_url: Optional[str] = None
    drafted_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class AuditLogModel(BaseModel):
    id: Optional[int] = None
    case_id: str
    timestamp: str
    root_cause: str
    action_taken: str
    rule_fired: str
    outcome: str
    amount_at_stake: float
    explanation: str
    raw_details: Optional[str] = None

class BatchSummaryModel(BaseModel):
    total_cases: int
    total_amount_at_risk: float
    amount_recovered: float
    recovery_rate_pct: float
    cases_escalated: int
    cases_pending: int
    cases_recovered: int
    cases_failed: int
    avg_time_to_recovery_hours: float
