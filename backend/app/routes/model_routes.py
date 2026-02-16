from fastapi import APIRouter, HTTPException, Body, Depends
from ..utils.model_utils import download_file
import hashlib
from pathlib import Path
from ..services.rbac_service import get_current_user, has_role

router = APIRouter()


@router.post('/download')
def download_model(payload: dict = Body(...), user: dict = Depends(get_current_user)):
    url = payload.get('url')
    dest = payload.get('dest', 'vector_store/models/model.bin')
    sha256 = payload.get('sha256')
    # require admin
    if not has_role(user, 'admin'):
        raise HTTPException(status_code=403, detail='admin role required')
    repo_root = Path(__file__).resolve().parents[2]
    allowed_base = repo_root / 'vector_store' / 'models'
    dest_p = Path(dest)
    # ensure dest is within allowed_base
    target = (repo_root / dest_p).resolve()
    if allowed_base.resolve() not in target.parents and allowed_base.resolve() != target.parent:
        raise HTTPException(status_code=400, detail='destination must be under vector_store/models')
    try:
        path = download_file(url, str(target))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if sha256:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        if h.hexdigest() != sha256:
            raise HTTPException(status_code=400, detail='checksum mismatch')
    return {"path": path}
