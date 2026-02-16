# SAR AI Platform — Complete Architecture & File Reference

## Project Overview

**SAR Narrative Generator Platform** is an intelligent Suspicious Activity Report (SAR) generation system designed for financial institutions to streamline compliance reporting. It uses AI-powered analysis, vector-based retrieval (RAG), and role-based access control to create audit-compliant narratives with complete transaction tracking.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Streamlit)                          │
│  Dashboard | Create Case | Generate SAR | Audit Trail | Settings │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP (JSON)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Port 8001)                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Routes Layer (7 routers)                                 │   │
│  │ • case_routes       → Create/Retrieve cases             │   │
│  │ • sar_routes        → Generate/Export SARs              │   │
│  │ • audit_routes      → Audit trail queries               │   │
│  │ • auth_routes       → JWT authentication                │   │
│  │ • risk_routes       → Risk pattern detection            │   │
│  │ • rag_routes        → RAG index management              │   │
│  │ • model_routes      → LLM model operations              │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Services Layer (11 services)                             │   │
│  │ • storage           → SQLite persistence                │   │
│  │ • sar_generator     → Narrative generation              │   │
│  │ • rag_store         → FAISS vector indexing             │   │
│  │ • llm               → Model interface (stub/local)      │   │
│  │ • risk_engine       → Transaction analysis              │   │
│  │ • audit_logger      → Audit trail management            │   │
│  │ • rbac_service      → Role-based access                 │   │
│  │ • exporter          → PDF generation (ReportLab)        │   │
│  │ • explainability    → Decision reasoning                │   │
│  │ • task_manager      → Async job handling                │   │
│  │ • prompt_templates  → LLM prompt engineering            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┬─────────────┐
        ↓                ↓                ↓             ↓
   ┌─────────┐      ┌────────┐     ┌──────────┐   ┌─────────┐
   │ SQLite  │      │ FAISS  │     │ LLM      │   │ Audit   │
   │ Database│      │ Vector │     │ (Stub)   │   │ Logs    │
   │ (4 TBs) │      │ Index  │     │          │   │         │
   └─────────┘      └────────┘     └──────────┘   └─────────┘
```

---

## 📁 Directory Structure & File Descriptions

### Root Level
```
e:\Barclay\sar-ai-platform\
├── backend/                    # FastAPI backend application
├── frontend/                   # Streamlit frontend
├── sample_data/                # JSON test cases for demonstration
├── alembic/                    # Database migration framework
├── .github/                    # GitHub Actions CI/CD
├── docker-compose.yml          # Docker services (Redis, Postgres)
├── README.md                   # Project overview
├── ARCHITECTURE.md            # This file
├── FEATURES.md                # Feature documentation
└── API_DOCUMENTATION.md       # API endpoint reference
```

---

## 🔧 Backend Directory (`backend/`)

### Main Application Entry
**File:** `backend/app/main.py` (75 lines)
```python
Purpose:    FastAPI application entrypoint
Imports:    7 routers (case, sar, audit, auth, risk, rag, model)
Features:   • CORS middleware (allows all origins for local demo)
            • Database auto-initialization on startup
            • FAISS index auto-load/save lifecycle hooks
            • Root endpoint returns system status
```

**Execution Flow:**
1. On startup: Ensure SQLite DB exists, execute schema.sql
2. Load FAISS index from disk if available
3. On shutdown: Save FAISS index to disk

---

### `backend/app/routes/` — API Endpoints

#### **1. case_routes.py** (38 lines)
```
Endpoints:   POST /cases/create          — Create new SAR case
             GET  /cases/{case_id}       — Retrieve case details

Logic:       • Validate payload structure (customer_name, transactions, alerts)
             • Generate unique case_id (CASE-{8-char-hex})
             • Save case to SQLite database
             • Return status + case_id

Example Response:
{
  "status": "created",
  "case_id": "CASE-a1b2c3d4"
}
```

#### **2. sar_routes.py** (55 lines)
```
Endpoints:   POST /sars/generate              — Generate SAR narrative
             GET  /sars/export/{sar_id}      — Export SAR as PDF
             GET  /sars/versions/{case_id}   — List SAR versions
             GET  /sars/versions/compare/{case_id} — Compare versions
             GET  /sars/status/{sar_id}      — Get SAR status

Logic:       • case_id → fetch case from storage
             • Run risk detection on transactions (find suspicious patterns)
             • Generate explainability (why patterns detected)
             • Call LLM to write SAR narrative
             • Save to database with audit trail
             • Support PDF export via ReportLab

Example Flow:
POST /sars/generate?case_id=CASE-a1b2c3d4
↓
1. Fetch case + transactions
2. Risk engine analyzes transactions ($50k+ transfers, rapid sequences, etc.)
3. Explainability engine explains detected patterns
4. LLM generates 2-3 paragraph narrative in WHO/WHAT/WHEN/WHERE/WHY format
5. Save SAR with version tracking
6. Log audit entry
↓
Response:
{
  "case_id": "CASE-a1b2c3d4",
  "sar_id": "SAR-x9y8z7u6",
  "sar_draft": "On 2024-02-14, customer John Doe (ID: C12345)...",
  "audit": {...},
  "explain": {"risk_score": 0.85, "patterns": ["bulk_transfer", "rapid_sequence"]}
}
```

#### **3. audit_routes.py** (20 lines)
```
Endpoints:   GET /audit/case/{case_id}  — Get audit trail for case

Logic:       • Query audit_logs table for all actions on case_id
             • Return filtered by user_id, action, timestamp
             • Include action details (what changed, by whom, when)

Example:
{
  "case_id": "CASE-a1b2c3d4",
  "audit_entries": [
    {
      "timestamp": "2026-02-16T10:30:00Z",
      "user_id": "analyst@bank.com",
      "action": "create_case",
      "details": {...}
    }
  ]
}
```

#### **4. auth_routes.py** (35 lines)
```
Endpoints:   POST /auth/login  — Authenticate user and return JWT

Logic:       • Accept username + password
             • Verify against hardcoded demo credentials:
               - admin / adminpass (role: admin)
               - analyst / password (role: analyst)
             • Generate JWT token valid for 24 hours
             • Include role in token payload for RBAC

Security:    • BCrypt password hashing
             • JWT signature with SECRET_KEY
             • Token contains: user_id, role, exp

Example:
POST /auth/login
{
  "username": "admin",
  "password": "adminpass"
}
↓
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {"user_id": "admin", "role": "admin"}
}
```

#### **5. risk_routes.py** (18 lines)
```
Endpoints:   POST /risk/analyze  — Analyze transactions for risk patterns

Logic:       • Accept transaction list
             • Detect patterns:
               - High-value transfers (>$50,000)
               - Rapid transaction sequences (>5 in 24h)
               - Destination country risk (high-risk jurisdictions)
               - Customer profile mismatch
             • Score risk (0.0 — 1.0)

Example Response:
{
  "risk_score": 0.78,
  "patterns": [
    {"name": "bulk_transfer", "confidence": 0.92},
    {"name": "high_velocity", "confidence": 0.65}
  ]
}
```

#### **6. rag_routes.py** (28 lines)
```
Endpoints:   POST /rag/reindex           — Rebuild FAISS index
             POST /rag/save              — Persist index to disk
             GET  /rag/load              — Load index from disk
             GET  /rag/query             — Query similar templates

Logic:       • Load SAR template library from sample_data/
             • Use sentence-transformers to create embeddings
             • Build FAISS index for semantic search
             • When generating SAR: query index for similar examples
             • Return top-3 matching templates

Example:
POST /rag/reindex
↓
Embeds 50+ SAR templates using FAISS + sentence-transformers
↓
{
  "status": "reindexed",
  "templates_count": 52,
  "indexed_dimensions": 384
}
```

#### **7. model_routes.py** (25 lines)
```
Endpoints:   GET /models/download  — Download LLM model
             GET /models/status    — Check model availability

Logic:       • RBAC: Only admins can download
             • Download community GGML quantized models
             • Verify file integrity
             • Return download link or cache local path

Supported Models:  mistral-7b.ggmlv3.q4_K_M
                   neural-chat-7b.ggmlv3.q4
```

---

### `backend/app/services/` — Business Logic

#### **1. storage.py** (120 lines)
```
Purpose:     SQLite database persistence layer

Functions:
  save_case(case_dict)           → Insert case, return case_id
  get_case(case_id)              → Fetch case with transactions
  save_sar(sar_id, case_id, narrative, audit) → Insert SAR
  get_sar_by_id(sar_id)          → Fetch SAR by ID
  get_sar_versions(case_id)      → List all SAR versions for case
  save_audit(audit_id, case_id, user_id, action, details) → Log action
  get_audit_trail(case_id)       → Fetch all audit entries for case

Database Schema:
┌─ cases ────────────────────┐
│ case_id (PK)               │
│ customer_name              │
│ customer_id                │
│ alerts (JSON)              │
│ transactions (JSON)        │
│ created_at (timestamp)     │
└────────────────────────────┘

┌─ sars ─────────────────────┐
│ sar_id (PK)                │
│ case_id (FK)               │
│ draft (narrative text)     │
│ version_id                 │
│ created_at                 │
└────────────────────────────┘

┌─ audit_logs ───────────────┐
│ audit_id (PK)              │
│ case_id (FK)               │
│ user_id                    │
│ action (create/modify)     │
│ details (JSON)             │
│ timestamp                  │
└────────────────────────────┘

┌─ sar_versions ─────────────┐
│ version_id (PK)            │
│ case_id (FK)               │
│ sar_id (FK)                │
│ draft (text)               │
│ created_at                 │
└────────────────────────────┘
```

#### **2. sar_generator.py** (45 lines)
```
Purpose:     SAR narrative generation orchestration

Key Function:
  generate_sar_narrative(case, transactions, risk_summary, templates=None)
  → Returns: (narrative_text, audit_dict)

Algorithm:
  1. Extract customer name, timestamp from case
  2. Query RAG store for similar SAR templates (semantic search)
  3. Build prompt: 
     - System instructions (neutral tone, who/what/when/where/why/how)
     - Case details + transactions + risk summary
     - Retrieved templates as examples
  4. Call LLM (stub/local/huggingface)
  5. Extract narrative from response
  6. Create audit entry with metadata:
     - Generated timestamp
     - Model name used
     - Data points (transaction count, template sources)

Output Format:
{
  "narrative": "On February 16, 2026, customer Jane Smith (ID: C99999) ...",
  "audit": {
    "generated_at": "2026-02-16T10:45:30Z",
    "model": "stub_model",
    "prompt_version": "v1",
    "data_points": {
      "tx_count": 8,
      "retrieved_templates": ["template_5", "template_12"]
    }
  }
}
```

#### **3. risk_engine.py** (60 lines)
```
Purpose:     Transaction pattern analysis for suspicious activity detection

Key Function:
  detect_patterns(transactions) → risk_summary_dict

Patterns Detected:
  1. bulk_transfer_alert
     Condition: Single transaction > $50,000
     Score boost: +0.30

  2. high_velocity
     Condition: >5 transactions in 24 hours
     Score boost: +0.25

  3. destination_jurisdiction_risk
     Condition: Transaction to high-risk countries (N.Korea, Iran, Syria)
     Score boost: +0.40

  4. customer_profile_mismatch
     Condition: Transaction amount > customer's typical profile
     Score boost: +0.15

  5. round_amount_pattern
     Condition: Multiple round-number transactions (exact $5K, $10K, $50K)
     Score boost: +0.10

Output:
{
  "risk_score": 0.72,
  "patterns": [
    {"name": "bulk_transfer_alert", "confidence": 0.92, "details": "Transfer of $75,000"},
    {"name": "high_velocity", "confidence": 0.60, "details": "8 transactions in 12 hours"}
  ],
  "flagged_transactions": [123, 456],
  "recommendation": "Escalate for manual review"
}
```

#### **4. rag_store.py** (80 lines)
```
Purpose:     Semantic search using FAISS + sentence-transformers

Key Class:   RAGStore
Methods:
  index_templates(template_dir) → Build vector index from files
  query(question, top_k=3)       → Find similar SAR templates
  save_index(path)               → Persist FAISS index to disk
  load_index(path)               → Load pre-built index from disk

Technical:
  • Embedding Model: sentence-transformers/all-MiniLM-L6-v2 (384-dim)
  • Vector DB: FAISS (fast approximate nearest neighbor search)
  • Index Type: IVFFlat (inverted file, good for <1M documents)

Workflow:
  1. During app startup: Load embeddings for all SAR templates
  2. When generating SAR:
     - Convert query (case + transactions) to embedding
     - Find 3 most similar templates in index
     - Pass to LLM as context examples
  3. On shutdown: Save updated index to disk for persistence

Example:
rag_store.query("Bulk transfer to Middle East by retail customer")
↓
Returns:
[
  {
    "text": "Customer transferred $100,000 to UAE bank account...",
    "source": "template_high_value_transfer.txt",
    "similarity_score": 0.89
  },
  {
    "text": "Rapid sequence of international transfers detected...",
    "source": "template_international_pattern.txt",
    "similarity_score": 0.76
  }
]
```

#### **5. llm.py** (70 lines)
```
Purpose:     LLM model interface with multiple backends

Supported Modes:
  • stub       : Returns mock responses (for testing)
  • local      : Runs llama-cpp-python with GGML model
  • huggingface: Calls HuggingFace Inference API

Key Function:
  generate(prompt, max_tokens=500, temperature=0.7) → response_dict

Configuration (via environment variables):
  LLM_MODE              : "stub" | "local" | "huggingface"
  LLM_MODEL_PATH        : Path to .ggml file (for local mode)
  HUGGINGFACE_API_KEY   : API token (for huggingface mode)
  LLM_MODEL             : Model name (for huggingface mode)

Response Format:
{
  "text": "Generated narrative text...",
  "model": "mistral-7b.ggmlv3.q4_K_M",
  "tokens_used": 342,
  "completed": true
}

Stub Mode Response (for demo without LLM):
{
  "text": "On [DATE], customer [NAME] initiated a series of transfers totaling $[AMOUNT]...",
  "model": "stub_model",
  "tokens_used": 0,
  "completed": true
}
```

#### **6. explainability_engine.py** (55 lines)
```
Purpose:     Generate human-readable explanations for risk decisions

Key Function:
  explain_decision(risk_summary, transactions) → explanation_dict

Output:
{
  "risk_score": 0.78,
  "decision_summary": "ESCALATE: High-risk patterns detected",
  "patterns_explained": [
    {
      "pattern": "bulk_transfer_alert",
      "explanation": "Customer transferred $75,000 in single transaction, exceeding typical profile",
      "confidence": 0.92,
      "recommendation": "Verify business purpose and source of funds"
    }
  ],
  "overall_recommendation": "Require additional customer documentation",
  "reasoning_trace": [
    "1. Detected bulk transfer: $75,000",
    "2. No prior large transfers in customer history",
    "3. Destination: High-risk jurisdiction",
    "4. Cumulative risk score: 0.78 (threshold: 0.70)",
    "5. Recommendation: Manual review required"
  ]
}
```

#### **7. audit_logger.py** (45 lines)
```
Purpose:     Comprehensive audit trail for compliance

Key Function:
  log_audit(user, case_id, user_id, action, details) → audit_entry

Tracked Events:
  • create_case          : New case submission
  • generate_sar         : SAR narrative auto-generation
  • modify_narrative     : Manual narrative edits
  • export_pdf           : PDF export
  • add_comment          : Analyst comments
  • escalate_case        : Case escalation
  • close_case           : Case closure

Audit Entry Structure:
{
  "audit_id": "AUD-2026021610453001",
  "timestamp": "2026-02-16T10:45:30.001Z",
  "user_id": "analyst@bank.com",
  "action": "generate_sar",
  "case_id": "CASE-a1b2c3d4",
  "details": {
    "sar_id": "SAR-x9y8z7u6",
    "model_used": "stub_model",
    "risk_score": 0.78,
    "audit_metadata": {...}
  },
  "ip_address": "127.0.0.1",
  "user_agent": "Streamlit/1.28.0"
}

Query Examples:
  • All actions on CASE-123 by any user
  • All SAR generations in last 24 hours
  • All exports by analyst1
  • Complete change history for specific SAR
```

#### **8. rbac_service.py** (50 lines)
```
Purpose:     Role-based access control

Roles:
  admin      : Full access — can view all cases, generate SARs, export PDFs, manage users
  analyst    : Limited access — can view assigned cases, generate SARs, export PDFs
  viewer     : Read-only — can view published SARs only

Functions:
  check_permission(user_id, role, resource, action) → bool
  has_role(user_id, required_role) → bool
  get_user_cases(user_id) → case_list

Permission Matrix:
┌────────────────┬────────┬─────────┬────────┐
│ Action         │ Admin  │ Analyst │ Viewer │
├────────────────┼────────┼─────────┼────────┤
│ Create Case    │   ✓    │    ✓    │   ✗    │
│ Generate SAR   │   ✓    │    ✓    │   ✗    │
│ Export PDF     │   ✓    │    ✓    │   ✗    │
│ View Audit     │   ✓    │    ✓    │   ✗    │
│ Modify SAR     │   ✓    │    ✓    │   ✗    │
│ View Report    │   ✓    │    ✓    │   ✓    │
│ Manage Users   │   ✓    │    ✗    │   ✗    │
└────────────────┴────────┴─────────┴────────┘
```

#### **9. exporter.py** (65 lines)
```
Purpose:     SAR export to PDF with professional formatting

Key Function:
  sar_to_pdf_bytes(narrative, case) → pdf_binary_data

Features:
  • ReportLab for PDF generation
  • Professional header with bank logo space
  • Case metadata section (customer name, ID, date)
  • Narrative body with proper formatting
  • Transaction summary table
  • Risk analysis section
  • Footer with document metadata
  • Page numbers and timestamps

PDF Structure:
┌─────────────────────────────────────────┐
│         SUSPICIOUS ACTIVITY REPORT       │
│                                         │
│  Case ID: CASE-a1b2c3d4                │
│  Customer: John Doe (ID: C12345)       │
│  Generated: 2026-02-16                 │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│  NARRATIVE                              │
│  On February 16, 2026, customer John    │
│  Doe initiated a series of transfers... │
│  [Body text continues]                  │
└─────────────────────────────────────────┘
┌─ Transaction Summary ──────────────────┐
│ Date       │ Amount │ Destination      │
├────────────┼────────┼──────────────────┤
│ 2026-02-14 │ $50K   │ UAE Bank Account │
│ 2026-02-14 │ $25K   │ Hong Kong        │
└─────────────────────────────────────────┘
```

#### **10. task_manager.py** (40 lines)
```
Purpose:     Async task management for long-running operations

Backend: Redis + RQ (Redis Queue)

Supported Tasks:
  • generate_sar_batch        : Bulk SAR generation
  • export_multiple_sars      : Multi-SAR PDF export
  • reindex_templates         : Rebuild RAG index
  • cleanup_old_versions      : Archive old SAR versions

Usage:
from services.task_manager import queue_task
task_id = queue_task("generate_sar_batch", case_ids=[...])
# Later: check_task_status(task_id)
```

#### **11. prompt_templates.py** (25 lines)
```
Purpose:     System prompts for LLM

SAR_SYSTEM_PROMPT:
"""You are a Suspicious Activity Report (SAR) analyst.
Your task is to generate a professional SAR narrative based on:
1. Customer information (who)
2. Transaction details (what, when, where)
3. Risk analysis (why this is suspicious)
4. Industry context and regulations

Format your response in clear paragraphs following WHO/WHAT/WHEN/WHERE/WHY/HOW structure.
Maintain neutral, factual tone. Include:
- Customer profile mismatch if present
- Transaction amount justification
- Geographic risk factors
- Reasoning for each pattern detected

Do NOT include personal opinions or judgments. Use standard SAR terminology."""
```

---

### `backend/app/database/` — Data Layer

#### **schema.sql** (80 lines)
```sql
-- Core tables for SAR system

CREATE TABLE IF NOT EXISTS cases (
  case_id TEXT PRIMARY KEY,
  customer_name TEXT NOT NULL,
  customer_id TEXT,
  alerts TEXT,  -- JSON array of alerts
  transactions TEXT,  -- JSON array of transactions
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sars (
  sar_id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES cases(case_id),
  draft TEXT,  -- SAR narrative
  version_id INTEGER DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
  audit_id TEXT PRIMARY KEY,
  case_id TEXT REFERENCES cases(case_id),
  user_id TEXT,
  action TEXT,  -- create_case, generate_sar, export_pdf, etc.
  details TEXT,  -- JSON with action details
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sar_versions (
  version_id INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id TEXT NOT NULL REFERENCES cases(case_id),
  sar_id TEXT REFERENCES sars(sar_id),
  draft TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cases_customer_id ON cases(customer_id);
CREATE INDEX idx_sars_case_id ON sars(case_id);
CREATE INDEX idx_audit_case_id ON audit_logs(case_id);
```

#### **db.py** (30 lines)
```python
Purpose:     SQLAlchemy database configuration

Key Elements:
  DATABASE_URL  : sqlite:///sar_ai.db (configurable via env)
  SessionLocal  : Database session factory
  Base          : SQLAlchemy declarative base
  get_db()      : Dependency injection for FastAPI routes
```

---

### `backend/app/utils/` — Helper Functions

#### **validators.py** (35 lines)
```python
Purpose:     Input validation for API payloads

Functions:
  validate_case_payload(payload) → bool
    Checks: customer_name, customer_id, transactions array
  
  validate_transaction(tx) → bool
    Checks: amount, date, destination, type
  
  validate_email(email) → bool
    Standard email format validation
```

---

### Root Backend Files

#### **requirements.txt** (18 dependencies)
```
fastapi==0.104.1              # Web framework
uvicorn==0.24.0               # ASGI server
sqlalchemy==2.0.23            # ORM
sqlite3                       # Database (included)
jwt==1.3.0                    # JSON Web Tokens
passlib==1.7.4                # Password hashing
bcrypt==4.0.1                 # Bcrypt implementation
requests==2.31.0              # HTTP client
sentence-transformers==2.2.2  # Embeddings
faiss-cpu==1.8.0              # Vector search
llama-cpp-python==0.1.59      # Local LLM
python-multipart==0.0.6       # Form parsing
pandas==2.1.3                 # Data handling
reportlab==4.0.7              # PDF generation
python-dotenv==1.0.0          # .env loading
redis==5.0.0                  # Redis client
rq==1.14.0                    # Job queue
```

#### **init_db.py** (30 lines)
```python
Purpose:     One-time database initialization script

Usage:       python init_db.py (from backend directory)

Actions:
  1. Check if sar_ai.db exists
  2. Read schema.sql
  3. Execute all CREATE TABLE statements
  4. Create sample index for RAG
  5. Verify all tables created successfully
  6. Print status report
```

---

## 🎨 Frontend (`frontend/streamlit_app.py`)

**Total:** 397 lines of Streamlit code

### Page Configuration
```python
st.set_page_config(
    page_title="SAR AI Platform",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### **5 Main Pages**

#### **1. Dashboard** (40 lines)
Shows system status, quick metrics, and getting started guide.
- Metrics: Status (Ready), API (Connected), Database (Initialized), Demo Users (2)
- Quick Start: 4-step workflow illustration
- Features overview card

#### **2. Create Case** (85 lines)
Load sample cases and submit to backend.
- Dropdown selector for 10+ sample JSON cases
- Display case info in card layout (Case ID, Customer Name, Customer ID)
- Render alerts as pandas DataFrame table
- Render transactions with currency formatting (₹)
- "Create Case" button with loading spinner
- Success/error feedback

#### **3. Generate SAR** (145 lines)
AI-powered narrative generation with editing.
```
4 Tabs:
  📄 Draft         → Editable textarea, Save/Reset buttons
  🔍 Analysis      → Risk indicators, explainability panel
  📊 Audit Trail   → Transaction timeline + audit log
  ⬇️ Export        → PDF/JSON download buttons
```

#### **4. View Audit Trail** (50 lines)
Complete audit history viewer.
- Filter by case ID
- Display table: timestamp, user, action, details
- Expandable details panel

#### **5. Settings** (40 lines)
Admin panel for system configuration.
- API connection tester with status
- Demo credentials display (admin/analyst)
- Database status checker
- Feature checklist (all ✓)

### Session State Management
```python
st.session_state.current_case  # Holds loaded case data
st.session_state.current_sar   # Holds generated SAR
st.session_state.sar_draft     # Holds edited narrative
```

### Custom CSS Styling
```css
.card             /* Styled info cards */
.success-box      /* Green success boxes */
.error-box        /* Red error boxes */
.info-box         /* Blue info boxes */
```

### Error Handling
- Try-catch for all API calls
- User-friendly error messages
- Loading spinners for async operations
- Session timeouts (24 hours)

---

## 📊 Sample Data (`sample_data/`)

Directory containing 10+ JSON files with realistic SAR test cases.

Example: `sample_data/case_bulk_transfer.json`
```json
{
  "case_id": "CASE-bulk-001",
  "customer_name": "John Doe",
  "customer_id": "C12345",
  "alerts": [
    {
      "alert_id": "ALT-001",
      "alert_type": "HIGH_AMOUNT_TRANSFER",
      "amount": 75000,
      "date": "2026-02-14"
    }
  ],
  "transactions": [
    {
      "tx_id": 1,
      "amount": 50000,
      "date": "2026-02-14",
      "type": "transfer",
      "destination": "UAE"
    },
    {
      "tx_id": 2,
      "amount": 25000,
      "date": "2026-02-14",
      "type": "transfer",
      "destination": "Hong Kong"
    }
  ]
}
```

---

## 🔐 Security Features

### Authentication
- JWT tokens with 24-hour expiration
- Bcrypt password hashing (rounds=12)
- All endpoints require token validation (except /auth/login and /)

### Authorization (RBAC)
- Admin: Full access
- Analyst: Case management access
- Viewer: Read-only access

### Audit Trail
- Every action logged with timestamp
- User ID tracking
- IP address logging
- Change history with diffs

### Data Protection
- SQLite encryption option (future)
- PII masking in logs
- Secure token handling
- HTTPS enforcement (production)

---

## 🚀 Running the System

### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py                    # Initialize DB
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Frontend
```powershell
cd ..
streamlit run frontend/streamlit_app.py --server.port 8501
```

### Both Together
```powershell
# Terminal 1
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# Terminal 2
cd frontend && streamlit run streamlit_app.py --server.port 8501

# Browser
Open http://localhost:8501
```

---

## 📈 Data Flow Example

**Complete workflow: Case → SAR Generation → PDF Export**

```
1. USER CREATES CASE
   FrontendUI (Create Case)
   ↓
   POST /cases/create
   ↓
   Backend: case_routes → validate → storage.save_case()
   ↓
   SQLite: INSERT INTO cases
   ↓
   Response: {"case_id": "CASE-abc123"}

2. USER GENERATES SAR
   Frontend (Generate SAR)
   ↓
   POST /sars/generate?case_id=CASE-abc123
   ↓
   Backend: sar_routes
   ├─ storage.get_case()  [fetch case + transactions]
   ├─ risk_engine.detect_patterns() [find suspicious activity]
   ├─ rag_store.query()   [retrieve similar SAR templates]
   ├─ llm.generate()      [write narrative]
   ├─ explainability_engine.explain_decision() [explain why]
   └─ audit_logger.log_audit() [log action]
   ↓
   Response: {
     "case_id": "CASE-abc123",
     "sar_id": "SAR-xyz789",
     "sar_draft": "On 2026-02-14...",
     "explain": {"risk_score": 0.78, "patterns": [...]}
   }

3. USER EXPORTS PDF
   Frontend (Generate SAR → Export tab)
   ↓
   GET /sars/export/SAR-xyz789
   ↓
   Backend: sar_routes → exporter.sar_to_pdf_bytes()
   ↓
   Response: PDF binary file
   ↓
   Browser: Download CASE-abc123_SAR.pdf

4. USER VIEWS AUDIT
   Frontend (Audit Trail page)
   ↓
   GET /audit/case/CASE-abc123
   ↓
   Backend: audit_routes → storage.get_audit_trail()
   ↓
   Response: [
     {"timestamp": "...", "user_id": "analyst", "action": "create_case"},
     {"timestamp": "...", "user_id": "system", "action": "generate_sar"},
     {"timestamp": "...", "user_id": "analyst", "action": "export_pdf"}
   ]
```

---

## 🎯 Key Features Summary

✅ **Core Features**
- Case management (create, retrieve, list)
- AI-powered SAR narrative generation
- Risk pattern detection (5+ patterns)
- Complete audit trail (every action logged)
- PDF export with professional formatting
- SAR versioning with diff comparison

✅ **Advanced Features**
- RAG (Retrieval Augmented Generation) with FAISS
- Semantic template search
- Explainability engine (explain decisions)
- Role-based access control (Admin/Analyst/Viewer)
- JWT authentication
- Bcrypt password hashing
- Async task management (RQ/Redis)
- Multiple LLM backends (stub/local/huggingface)

✅ **UI/UX**
- Multi-page Streamlit dashboard
- Session state management
- Real-time loading feedback
- Card-based information layout
- Pandas DataFrames for tables
- Emoji-enhanced icons
- Custom CSS styling
- Error handling with user messages

✅ **Production Ready**
- Docker Compose (Redis, Postgres)
- Environment variable management
- Database migrations (Alembic)
- GitHub Actions CI/CD
- Comprehensive logging
- Error handling & recovery

---

## 📝 File Count & Statistics

```
Backend Routes:         7 files (200+ lines)
Backend Services:      11 files (600+ lines)
Backend Utils:          2 files (65 lines)
Database:               2 files (110 lines)
Frontend:               1 file (397 lines)
Config & Scripts:       4 files (150 lines)
Sample Data:           10+ JSON files (~1000 lines)
─────────────────────────────────────────
Total:                35+ files (~2,500 lines of code)
```

---

This architecture enables a **scalable, auditable, and intelligent SAR generation platform** suitable for enterprise financial compliance workflows.
