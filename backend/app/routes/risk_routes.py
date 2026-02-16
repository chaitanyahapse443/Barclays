from fastapi import APIRouter

router = APIRouter()


@router.post("/assess")
def assess_risk(payload: dict):
    # stub risk scoring
    return {"risk_score": 85, "patterns": ["structuring", "rapid_movement"]}
