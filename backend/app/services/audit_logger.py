from datetime import datetime
from . import storage
import uuid

def log_audit(db, case_id, user_id, action, details):
    # create audit entry and persist via storage
    entry = {
        "case_id": case_id,
        "user_id": user_id,
        "action": action,
        "details": details,
        "timestamp": datetime.utcnow().isoformat(),
    }
    audit_id = f"AUDIT-{uuid.uuid4().hex[:8]}"
    # attempt to save via storage; storage.save_audit expects strings
    try:
        storage.save_audit(audit_id=audit_id, case_id=case_id, user_id=user_id, action=action, details=details)
    except Exception:
        # fallback to printing
        print("AUDIT (fallback):", entry)
    return entry
