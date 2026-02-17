from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from ..services import storage, risk_engine, sar_generator, explainability_engine, audit_logger, exporter
from ..services import rag_store
import uuid
import json

router = APIRouter()


@router.post("/generate")
def generate_sar(case_id: str = Query(...)):
    case = storage.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="case not found")
    transactions = case.get('transactions', [])
    risk_summary = risk_engine.detect_patterns(transactions)
    explain = explainability_engine.explain_decision(risk_summary, transactions)
    narrative, audit = sar_generator.generate_sar_narrative(case, transactions, risk_summary)
    sar_id = f"SAR-{uuid.uuid4().hex[:8]}"
    storage.save_sar(sar_id, case_id, narrative, audit)
    # persist audit log entry
    audit_entry = audit_logger.log_audit(None, case_id, user_id="system", action="generate_sar", details={"sar_id": sar_id, "audit": audit, "explain": explain})
    # also save audit to DB
    storage.save_audit(audit_id=audit_entry.get('timestamp', sar_id), case_id=case_id, user_id="system", action="generate_sar", details={"sar_id": sar_id, "audit": audit, "explain": explain})
    return {"case_id": case_id, "sar_id": sar_id, "sar_draft": narrative, "audit": audit, "explain": explain}


@router.get('/export/{sar_id}')
def export_sar(sar_id: str):
    sar = storage.get_sar_by_id(sar_id)
    if not sar:
        raise HTTPException(status_code=404, detail='sar not found')
    case = storage.get_case(sar.get('case_id'))
    pdf = exporter.sar_to_pdf_bytes(sar.get('draft') or '', case)
    return StreamingResponse(
        BytesIO(pdf),
    media_type="application/pdf",
    headers={
        "Content-Disposition": f'attachment; filename="{sar_id}.pdf"'
    }
)


@router.get('/versions/{case_id}')
def list_versions(case_id: str):
    versions = storage.get_sar_versions(case_id)
    return {"case_id": case_id, "versions": versions}


@router.get('/versions/compare/{case_id}')
def compare_versions(case_id: str):
    versions = storage.get_sar_versions(case_id)
    if len(versions) < 2:
        return {"case_id": case_id, "diffs": []}
    from difflib import unified_diff
    diffs = []
    base = versions[-1]['draft'] if versions else ''
    for v in versions:
        diff = '\n'.join(unified_diff(base.splitlines(), v['draft'].splitlines(), lineterm=''))
        diffs.append({'version_id': v['version_id'], 'diff': diff})
    return {"case_id": case_id, "diffs": diffs}


@router.get("/status/{sar_id}")
def sar_status(sar_id: str):
    # simple lookup
    return {"sar_id": sar_id, "status": "draft"}
