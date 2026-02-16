# SAR AI Platform — Hackathon Scaffold

This repository is a prototype scaffold for the SAR Narrative Generator with Audit Trail hackathon project.

Structure includes backend API (FastAPI), a Streamlit demo frontend, sample data, and a vector store directory for RAG assets.

See `backend/requirements.txt` for Python dependencies.

Local, free option (recommended)
 - Embeddings / RAG: `sentence-transformers` + `faiss-cpu` (local, free)
 - LLM: `llama-cpp-python` with a GGML quantized model (run locally, no API costs)

To use the local stack:
1. Install dependencies (from `backend`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Download a quantized GGML model (for example, a community Llama or Mistral GGML file) and set `LLM_MODEL_PATH` environment variable to its path.

3. Start the backend with local LLM mode:

```powershell
$env:LLM_MODE='local'
$env:LLM_MODEL_PATH='C:\path\to\model.ggml'
uvicorn app.main:app --reload --port 8000
```

4. If you prefer not to run a local LLM, set `LLM_MODE=huggingface` and provide `HUGGINGFACE_API_KEY` and `LLM_MODEL` (free tier available).

Full quickstart (Windows PowerShell)

```powershell
cd e:/Barclay/sar-ai-platform/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# optionally copy .env.example to .env and edit or set env vars directly
# start backend
uvicorn app.main:app --reload --port 8000

# in another terminal run frontend demo
cd e:/Barclay/sar-ai-platform
streamlit run frontend/streamlit_app.py
```

If you want to run purely offline with no API keys:
- Set `LLM_MODE=local` and `LLM_MODEL_PATH` to a GGML model file (download from model sources).
- Ensure `sentence-transformers` and `faiss-cpu` installed for RAG; otherwise the system falls back to simple keyword retrieval.

Notes:
- The database is SQLite for prototype convenience. For concurrency and audit integrity, switch to PostgreSQL (update `database/db.py`).
- RAG persistence will auto-load FAISS index at startup if `vector_store/faiss_index` exists.

Docker / Compose (recommended for full local stack)

This repository includes a `docker-compose.yml` with `redis` and `postgres`. To run the full stack locally:

```powershell
docker-compose up --build
```

This will start Redis (for RQ), Postgres (for DB), and an RQ worker (the worker will install Python deps inside the container).

To run the backend against Docker services locally from your host, set these env vars:

```powershell
$env:REDIS_URL='redis://localhost:6379/0'
$env:DATABASE_URL='postgresql://saruser:example@localhost:5432/sardb'
```

Then run the backend as normal (or run inside container).

Alembic migrations

Alembic scaffolding is included. To run migrations locally (after setting `DATABASE_URL`):

```powershell
python backend/tools/migrate.py
# or use alembic if installed: alembic upgrade head
```

Auth & RBAC

- Login is available at `POST /auth/login` (demo users `admin`/`adminpass`, `analyst`/`password`).
- Use the returned JWT in `Authorization: Bearer <token>` for protected endpoints (model download requires `admin`).


