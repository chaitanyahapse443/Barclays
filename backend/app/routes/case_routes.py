from fastapi import APIRouter, HTTPException
from ..services import storage
from ..utils.validators import validate_case_payload
import uuid

router = APIRouter()


@router.post("/create")
def create_case(payload: dict):
    try:
        if not validate_case_payload(payload):
            raise HTTPException(status_code=400, detail="Invalid case payload")
        case_id = payload.get('case_id') or f"CASE-{uuid.uuid4().hex[:8]}"
        payload['case_id'] = case_id
        storage.save_case(payload)
        return {"status": "created", "case_id": case_id}
    except Exception as e:
        print(f"Error in create_case: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/{case_id}")
def get_case(case_id: str):
    c = storage.get_case(case_id)
    if not c:
        raise HTTPException(status_code=404, detail="case not found")
    return c
