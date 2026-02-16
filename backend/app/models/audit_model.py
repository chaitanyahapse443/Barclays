from pydantic import BaseModel
from typing import Dict

class AuditLog(BaseModel):
    audit_id: str
    case_id: str
    user_id: str
    action: str
    details: Dict
    timestamp: str
