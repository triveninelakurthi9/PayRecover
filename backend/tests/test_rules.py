import pytest
from app.db import init_db, get_db_connection
from app.seed_generator import generate_synthetic_cases, load_seed_into_db
from app.diagnosis_engine import diagnosis_engine
from app.intervention_rules import rules_engine, MAX_ATTEMPTS
from app.execution_layer import execution_layer

@pytest.fixture(autouse=True)
def setup_test_db():
    load_seed_into_db()

def test_seed_generation():
    cases = generate_synthetic_cases(count=60)
    assert len(cases) == 60
    assert any(c["category"] == "payment_degradation" for c in cases)
    assert any(c["category"] == "checkout_abandonment" for c in cases)
    assert any(c["category"] == "subscription_failure" for c in cases)

def test_diagnosis_engine_deterministic():
    # Direct code lookups
    res1 = diagnosis_engine.diagnose("BAD_REQUEST_ERROR:EXPIRED_CARD", "Card expired", "payment_degradation")
    assert res1["root_cause"] == "card_expired"
    assert res1["confidence"] == 1.0

    res2 = diagnosis_engine.diagnose("GATEWAY_ERROR:INSUFFICIENT_FUNDS", "Low balance", "payment_degradation")
    assert res2["root_cause"] == "insufficient_funds"

    res3 = diagnosis_engine.diagnose("BAD_REQUEST_ERROR:RISK_CHECK_FAILED", "Flagged transaction", "payment_degradation")
    assert res3["root_cause"] == "risk_block"

def test_risk_block_gated_requirement():
    # Risk block must escalate to manual queue and NOT take automated money action
    decision = rules_engine.decide_intervention("risk_block", prior_attempts=0, status="pending")
    assert decision["action"] == "escalate_manual_review"
    assert decision["rule_fired"] == "RULE_RISK_BLOCK_GATED_ESCALATION"

def test_stopping_rules_max_attempts():
    # Over max attempts -> stop & escalate
    decision = rules_engine.decide_intervention("insufficient_funds", prior_attempts=3, status="pending")
    assert decision["action"] == "escalate_limit_reached"
    assert decision["allowed"] is False

def test_stopping_rules_terminal_state():
    # Recovered state -> freeze actions
    decision = rules_engine.decide_intervention("insufficient_funds", prior_attempts=1, status="recovered")
    assert decision["action"] == "none"
    assert decision["allowed"] is False

def test_stopping_rules_cooldown_active():
    # Attempt within 4h window (e.g. 30 min ago) -> cooldown active
    from datetime import datetime, timedelta
    recent_time = (datetime.now() - timedelta(minutes=30)).isoformat()
    decision = rules_engine.decide_intervention(
        root_cause="insufficient_funds", 
        prior_attempts=1, 
        status="pending", 
        last_action_at=recent_time
    )
    assert decision["action"] == "cooldown_wait"
    assert decision["rule_fired"] == "RULE_COOLDOWN_ACTIVE"
    assert decision["allowed"] is False


def test_graceful_failure_injection():
    res = execution_layer.process_case("PAY-0001", inject_failure=True)
    assert res["success"] is True
    assert res["action"] == "graceful_failure_handled"

    # Check audit log entry
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs WHERE case_id = 'PAY-0001' AND outcome = 'graceful_failure_handled';")
    log = cursor.fetchone()
    conn.close()
    assert log is not None
    assert "GRACEFUL FAILURE DEMO" in log["explanation"]
