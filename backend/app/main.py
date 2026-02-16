from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import case_routes, sar_routes, audit_routes, auth_routes, risk_routes
from .services.rag_store import get_rag_store
import os
import sqlite3
from pathlib import Path

app = FastAPI(title="SAR AI Platform - API")

app.include_router(case_routes.router, prefix="/cases")
app.include_router(sar_routes.router, prefix="/sars")
app.include_router(audit_routes.router, prefix="/audit")
app.include_router(auth_routes.router, prefix="/auth")
app.include_router(risk_routes.router, prefix="/risk")
from .routes import rag_routes
app.include_router(rag_routes.router, prefix="/rag")
from .routes import model_routes
app.include_router(model_routes.router, prefix="/models")

# Allow CORS for local demo frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def ensure_db():
    # create sqlite DB file and run schema.sql if not present
    db_path = os.path.join(os.path.dirname(__file__), '..', 'sar_ai.db')
    db_path = os.path.normpath(db_path)
    # ensure directory exists
    db_dir = os.path.dirname(db_path)
    os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        sql = open(os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')).read()
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()
    # Attempt to auto-load FAISS RAG index if present
    try:
        repo_root = Path(__file__).resolve().parents[1]
        idx_dir = repo_root / 'vector_store' / 'faiss_index'
        if idx_dir.exists():
            store = get_rag_store()
            try:
                store.load_index(str(idx_dir))
            except Exception:
                # ignore loading errors at startup
                pass
    except Exception:
        pass


@app.on_event("shutdown")
def save_index_on_shutdown():
    try:
        repo_root = Path(__file__).resolve().parents[1]
        idx_dir = repo_root / 'vector_store' / 'faiss_index'
        store = get_rag_store()
        if store and getattr(store, '_index', None) is not None:
            store.save_index(str(idx_dir))
    except Exception:
        # swallow errors on shutdown
        pass


@app.get("/")
def root():
    return {"message": "SAR AI Platform API"}
