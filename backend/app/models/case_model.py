from pydantic import BaseModel
from typing import List, Dict

class Case(BaseModel):
    case_id: str
    customer_id: str
    customer_name: str
    alerts: List[Dict]
