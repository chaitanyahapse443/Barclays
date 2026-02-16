from fastapi import APIRouter

router = APIRouter()


@router.get("/logs/{case_id}")
def get_audit_logs(case_id: str):
    return {"case_id": case_id, "logs": []}
