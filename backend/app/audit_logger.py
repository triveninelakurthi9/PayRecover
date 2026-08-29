import json
from datetime import datetime
from app.db import get_db_connection

class AuditLogger:
    def log_event(
        self,
        case_id: str,
        root_cause: str,
        action_taken: str,
        rule_fired: str,
        outcome: str,
        amount_at_stake: float,
        explanation: str,
        raw_details: dict = None
    ):
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = datetime.now().isoformat()
        raw_str = json.dumps(raw_details or {})

        cursor.execute("""
            INSERT INTO audit_logs (
                case_id, timestamp, root_cause, action_taken, rule_fired,
                outcome, amount_at_stake, explanation, raw_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            case_id, now_str, root_cause, action_taken, rule_fired,
            outcome, amount_at_stake, explanation, raw_str
        ))

        conn.commit()
        conn.close()
        print(f"[AUDIT LOG] [{case_id}] {action_taken} -> {outcome} (Rule: {rule_fired})")

audit_logger = AuditLogger()
