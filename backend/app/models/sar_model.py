from pydantic import BaseModel
from typing import Dict, List

class SAR(BaseModel):
    sar_id: str
    case_id: str
    draft: str
    audit: Dict
    versions: List[Dict] = []
