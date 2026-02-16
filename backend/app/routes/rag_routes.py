from fastapi import APIRouter, HTTPException, Body
from ..services.rag_store import get_rag_store
from ..services import task_manager

router = APIRouter()


@router.post('/reindex')
def reindex_rag():
    store = get_rag_store()
    try:
        res = store.reindex()
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/reindex_async')
def reindex_rag_async():
    store = get_rag_store()
    try:
        task_id = task_manager.start_task(store.reindex)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/save')
def save_rag_index(path: str = Body('vector_store/faiss_index')):
    store = get_rag_store()
    try:
        res = store.save_index(path)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/load')
def load_rag_index(path: str = Body('vector_store/faiss_index')):
    store = get_rag_store()
    try:
        res = store.load_index(path)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/status')
def rag_status():
    store = get_rag_store()
    return {"count": len(store.docs), "has_index": store._index is not None}


@router.get('/task/{task_id}')
def task_status(task_id: str):
    t = task_manager.get_task(task_id)
    if not t:
        raise HTTPException(status_code=404, detail='task not found')
    return t
