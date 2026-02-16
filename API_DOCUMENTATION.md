# SAR AI Platform — Complete API Reference

**Base URL:** `http://localhost:8001`  
**Version:** 1.0.0  
**Authentication:** JWT Bearer Token

---

## 📋 Table of Contents
1. [Authentication](#authentication)
2. [Case Management](#case-management)
3. [SAR Generation](#sar-generation)
4. [Audit Trail](#audit-trail)
5. [Risk Analysis](#risk-analysis)
6. [RAG & Templates](#rag--templates)
7. [Models](#models)
8. [Error Codes](#error-codes)

---

## 🔐 Authentication

### Login
Generate JWT token for API access.

**Request:**
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "adminpass"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "user_id": "admin",
    "role": "admin"
  }
}
```

**Error Response (401):**
```json
{
  "detail": "Invalid credentials"
}
```

**Demo Credentials:**
```
Username: admin
Password: adminpass
Role: admin (full access)

Username: analyst
Password: password
Role: analyst (case management access)
```

**Using Token:**
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 📂 Case Management

### Create Case
Submit a new suspicious activity case for SAR generation.

**Request:**
```http
POST /cases/create
Content-Type: application/json
Authorization: Bearer {token}

{
  "case_id": "CASE-custom-001",  // optional, auto-generated if omitted
  "customer_name": "John Doe",
  "customer_id": "C12345",
  "alerts": [
    {
      "alert_id": "ALT-001",
      "alert_type": "HIGH_AMOUNT_TRANSFER",
      "amount": 75000,
      "date": "2026-02-14",
      "description": "Large transfer detected"
    }
  ],
  "transactions": [
    {
      "tx_id": 1,
      "amount": 50000,
      "currency": "USD",
      "date": "2026-02-14",
      "time": "10:30:00",
      "type": "transfer",
      "destination": "UAE",
      "destination_bank": "Emirates Bank",
      "description": "Wire transfer"
    },
    {
      "tx_id": 2,
      "amount": 25000,
      "currency": "USD",
      "date": "2026-02-14",
      "time": "14:45:00",
      "type": "transfer",
      "destination": "Hong Kong",
      "destination_bank": "HSBC Hong Kong",
      "description": "International transfer"
    }
  ]
}
```

**Success Response (200):**
```json
{
  "status": "created",
  "case_id": "CASE-a1b2c3d4"
}
```

**Validation Rules:**
- `customer_name` (required): String, 1-200 chars
- `customer_id` (required): String, 1-50 chars
- `alerts` (optional): Array of alert objects
- `transactions` (required): Array of transaction objects, minimum 1

**Error Response (400):**
```json
{
  "detail": "Invalid case payload - missing required fields"
}
```

---

### Get Case Details
Retrieve case information with all associated transactions and alerts.

**Request:**
```http
GET /cases/{case_id}
Authorization: Bearer {token}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| case_id | string | Yes | Case identifier (e.g., CASE-a1b2c3d4) |

**Success Response (200):**
```json
{
  "case_id": "CASE-a1b2c3d4",
  "customer_name": "John Doe",
  "customer_id": "C12345",
  "created_at": "2026-02-16T10:30:00Z",
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
      "currency": "USD",
      "date": "2026-02-14",
      "type": "transfer",
      "destination": "UAE"
    }
  ]
}
```

**Error Response (404):**
```json
{
  "detail": "case not found"
}
```

---

## 📝 SAR Generation

### Generate SAR Narrative
AI-powered generation of Suspicious Activity Report narrative.

**Request:**
```http
POST /sars/generate?case_id=CASE-a1b2c3d4
Authorization: Bearer {token}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| case_id | string | Yes | Case ID for SAR generation |

**Processing Steps:**
1. Retrieve case and transactions
2. Detect suspicious patterns (high velocity, bulk transfers, etc.)
3. Query RAG templates for similar cases
4. Generate narrative using LLM
5. Create explainability report
6. Log audit entry
7. Save SAR to database

**Success Response (200):**
```json
{
  "case_id": "CASE-a1b2c3d4",
  "sar_id": "SAR-x9y8z7u6",
  "sar_draft": "On February 14, 2026, customer John Doe (ID: C12345) initiated a series of international transfers totaling $75,000 to high-risk jurisdictions. The transactions exhibit several indicators of suspicious activity:\n\nWHO: John Doe, retail customer with account opened in 2024\nWHAT: Two international wire transfers, $50,000 and $25,000\nWHEN: February 14, 2026, within 4 hours\nWHERE: UAE and Hong Kong banking institutions\nWHY: Customer profile examination reveals no prior international transaction history\nHOW: Online banking, initiated by account holder\n\nRisk Assessment: Multiple suspicious patterns detected...",
  "audit": {
    "generated_at": "2026-02-16T10:45:30Z",
    "model": "stub_model",
    "prompt_version": "v1",
    "data_points": {
      "tx_count": 2,
      "retrieved_templates": ["template_bulk_transfer", "template_international"]
    }
  },
  "explain": {
    "risk_score": 0.78,
    "risk_level": "HIGH",
    "patterns": [
      {
        "name": "bulk_transfer_alert",
        "confidence": 0.92,
        "evidence": "Single transaction $50,000 (threshold: $50,000)"
      },
      {
        "name": "high_velocity",
        "confidence": 0.65,
        "evidence": "2 transactions in 4 hours"
      },
      {
        "name": "destination_jurisdiction_risk",
        "confidence": 0.88,
        "evidence": "Transfers to UAE and Hong Kong"
      },
      {
        "name": "customer_profile_mismatch",
        "confidence": 0.75,
        "evidence": "No prior international transfers, retail customer"
      }
    ],
    "recommendation": "ESCALATE: Manual review required. Verify business purpose and source of funds."
  }
}
```

**Error Response (404):**
```json
{
  "detail": "case not found"
}
```

**Error Response (500):**
```json
{
  "detail": "Internal error: Model unavailable"
}
```

---

### Export SAR as PDF
Download generated SAR as professionally formatted PDF document.

**Request:**
```http
GET /sars/export/{sar_id}
Authorization: Bearer {token}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sar_id | string | Yes | SAR identifier (e.g., SAR-x9y8z7u6) |

**Success Response (200):**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename=SAR-x9y8z7u6.pdf

[Binary PDF data]
```

**PDF Contents:**
- Header: SAR title, case ID, date
- Case metadata: Customer name, ID, creation date
- Narrative: Full SAR text (who/what/when/where/why/how)
- Transaction summary table
- Risk analysis section
- Page numbers and timestamps

**Error Response (404):**
```json
{
  "detail": "sar not found"
}
```

---

### List SAR Versions
Get all version history for a case's SAR.

**Request:**
```http
GET /sars/versions/{case_id}
Authorization: Bearer {token}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| case_id | string | Yes | Case identifier |

**Success Response (200):**
```json
{
  "case_id": "CASE-a1b2c3d4",
  "versions": [
    {
      "version_id": 1,
      "sar_id": "SAR-x9y8z7u6",
      "draft": "On February 14, 2026...",
      "created_at": "2026-02-16T10:45:30Z",
      "modified_by": "system"
    },
    {
      "version_id": 2,
      "sar_id": "SAR-x9y8z7u6",
      "draft": "On February 14, 2026... [edited version]",
      "created_at": "2026-02-16T11:30:15Z",
      "modified_by": "analyst1"
    }
  ]
}
```

---

### Compare SAR Versions
View differences between SAR versions for a case.

**Request:**
```http
GET /sars/versions/compare/{case_id}
Authorization: Bearer {token}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| case_id | string | Yes | Case identifier |

**Success Response (200):**
```json
{
  "case_id": "CASE-a1b2c3d4",
  "diffs": [
    {
      "version_id": 2,
      "diff": "--- version 1\n+++ version 2\n@@ -1,5 +1,6 @@\n On February 14, 2026, customer John Doe...\n-risk score: 0.75\n+risk score: 0.78\n vulnerability identified..."
    }
  ]
}
```

**Format:** Unified diff format (like `git diff`)

---

### Get SAR Status
Check current status of a generated SAR.

**Request:**
```http
GET /sars/status/{sar_id}
Authorization: Bearer {token}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sar_id | string | Yes | SAR identifier |

**Success Response (200):**
```json
{
  "sar_id": "SAR-x9y8z7u6",
  "status": "draft",
  "last_modified": "2026-02-16T11:30:15Z",
  "version": 2,
  "exportable": true
}
```

---

## 📊 Audit Trail

### Get Case Audit Trail
Retrieve complete audit history for a case.

**Request:**
```http
GET /audit/case/{case_id}
Authorization: Bearer {token}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| case_id | string | Yes | Case identifier |

**Query Parameters (Optional):**
| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | string | Filter by user (e.g., analyst1) |
| action | string | Filter by action (create_case, generate_sar, export_pdf) |
| start_date | ISO8601 | Filter from date (e.g., 2026-02-16T00:00:00Z) |
| end_date | ISO8601 | Filter to date |

**Success Response (200):**
```json
{
  "case_id": "CASE-a1b2c3d4",
  "audit_entries": [
    {
      "audit_id": "AUD-20260216104500",
      "timestamp": "2026-02-16T10:45:00Z",
      "user_id": "system",
      "action": "create_case",
      "details": {
        "case_id": "CASE-a1b2c3d4",
        "customer_name": "John Doe"
      },
      "ip_address": "127.0.0.1"
    },
    {
      "audit_id": "AUD-20260216104530",
      "timestamp": "2026-02-16T10:45:30Z",
      "user_id": "system",
      "action": "generate_sar",
      "details": {
        "sar_id": "SAR-x9y8z7u6",
        "model_used": "stub_model",
        "risk_score": 0.78
      },
      "ip_address": "127.0.0.1"
    },
    {
      "audit_id": "AUD-20260216114015",
      "timestamp": "2026-02-16T11:40:15Z",
      "user_id": "analyst1",
      "action": "export_pdf",
      "details": {
        "sar_id": "SAR-x9y8z7u6",
        "file_size": 245632
      },
      "ip_address": "192.168.1.100"
    }
  ],
  "total_entries": 3
}
```

**Tracked Actions:**
| Action | Description |
|--------|-------------|
| create_case | New case submitted |
| generate_sar | SAR narrative auto-generated |
| modify_sar | Manual narrative edits |
| export_pdf | PDF exported |
| view_case | Case viewed |
| escalate_case | Case escalated for review |
| close_case | Case closed |
| add_comment | Analyst comment added |

---

## ⚠️ Risk Analysis

### Analyze Transactions for Risk
Detect suspicious patterns in transaction list.

**Request:**
```http
POST /risk/analyze
Content-Type: application/json
Authorization: Bearer {token}

{
  "transactions": [
    {
      "tx_id": 1,
      "amount": 50000,
      "date": "2026-02-14",
      "destination": "UAE"
    },
    {
      "tx_id": 2,
      "amount": 25000,
      "date": "2026-02-14",
      "destination": "Hong Kong"
    }
  ],
  "customer_profile": {
    "customer_type": "retail",
    "account_age_days": 180,
    "typical_transaction_amount": 5000
  }
}
```

**Success Response (200):**
```json
{
  "risk_score": 0.78,
  "risk_level": "HIGH",
  "patterns": [
    {
      "name": "bulk_transfer_alert",
      "confidence": 0.92,
      "evidence": "Transaction of $50,000 detected",
      "recommendation": "Verify business purpose"
    },
    {
      "name": "high_velocity",
      "confidence": 0.65,
      "evidence": "2 transactions in 4 hours",
      "recommendation": "Monitor for escalation"
    },
    {
      "name": "destination_jurisdiction_risk",
      "confidence": 0.88,
      "evidence": "Destination to high-risk countries",
      "recommendation": "Additional KYC review"
    }
  ],
  "flagged_transactions": [1, 2],
  "overall_recommendation": "ESCALATE: Requires manual compliance review"
}
```

**Risk Patterns Detected:**
| Pattern | Threshold | Score Impact |
|---------|-----------|--------------|
| bulk_transfer_alert | Amount > $50,000 | +0.30 |
| high_velocity | >5 transactions/24h | +0.25 |
| destination_jurisdiction_risk | High-risk countries | +0.40 |
| customer_profile_mismatch | Atypical amount | +0.15 |
| round_amount_pattern | Round numbers ($5K, $10K) | +0.10 |

---

## 🔍 RAG & Templates

### Reindex Templates
Rebuild FAISS vector index from template library.

**Request:**
```http
POST /rag/reindex
Authorization: Bearer {token}
```

**Processing:**
1. Load all SAR templates from `sample_data/`
2. Generate embeddings using sentence-transformers
3. Build FAISS index for semantic search
4. Save index to `backend/vector_store/faiss_index/`

**Success Response (200):**
```json
{
  "status": "reindexed",
  "templates_count": 52,
  "indexed_dimensions": 384,
  "index_type": "IVFFlat",
  "indexed_at": "2026-02-16T12:00:00Z"
}
```

---

### Save RAG Index
Persist FAISS index to disk.

**Request:**
```http
POST /rag/save
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "status": "saved",
  "path": "backend/vector_store/faiss_index",
  "size_mb": 12.5
}
```

---

### Load RAG Index
Load pre-built FAISS index from disk.

**Request:**
```http
GET /rag/load
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "status": "loaded",
  "path": "backend/vector_store/faiss_index",
  "templates_count": 52
}
```

---

### Query RAG for Similar Templates
Find similar SAR examples from template library.

**Request:**
```http
GET /rag/query?q={query}&top_k=3
Authorization: Bearer {token}
```

**Query Parameters:**
| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| q | string | required | 500 | Search query (case description or key details) |
| top_k | integer | 3 | 10 | Number of similar templates to return |

**Example Query:**
```
GET /rag/query?q=bulk+transfer+to+middle+east+by+retail+customer&top_k=3
```

**Success Response (200):**
```json
{
  "query": "bulk transfer to middle east by retail customer",
  "results": [
    {
      "rank": 1,
      "similarity_score": 0.89,
      "source": "template_high_value_international.txt",
      "summary": "Customer transferred $100,000 to UAE bank account...",
      "text": "On [DATE], retail customer [NAME] initiated international transfer of [AMOUNT] to [DESTINATION]. Transaction triggered multiple compliance reviews due to..."
    },
    {
      "rank": 2,
      "similarity_score": 0.76,
      "source": "template_rapid_sequence.txt",
      "summary": "Rapid sequence of transfers to high-risk jurisdictions...",
      "text": "Customer executed [COUNT] transfers within [PERIOD] timeframe to [DESTINATIONS]..."
    },
    {
      "rank": 3,
      "similarity_score": 0.69,
      "source": "template_country_risk.txt",
      "summary": "Transfer to sanctioned jurisdiction assessment...",
      "text": "Transaction destination analysis reveals [DETAILS]..."
    }
  ]
}
```

---

## 🤖 Models

### Download LLM Model
Download quantized GGML language model.

**Request:**
```http
GET /models/download?model=mistral-7b&format=q4_K_M
Authorization: Bearer {token}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Model name (mistral-7b, neural-chat-7b) |
| format | string | Yes | Quantization format (q4_K_M, q5_K_M, q8) |

**Authorization:** Requires admin role

**Success Response (200):**
```json
{
  "model": "mistral-7b",
  "format": "q4_K_M",
  "size_mb": 4100,
  "download_url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b.Q4_K_M.gguf",
  "local_cache_path": "$HOME/.ggml_models/mistral-7b.Q4_K_M.gguf",
  "sha256": "abc123def456...",
  "suitable_for_sar": true
}
```

---

### Check Model Status
Verify current LLM model availability.

**Request:**
```http
GET /models/status
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "current_mode": "stub",
  "available_modes": ["stub", "local", "huggingface"],
  "models": {
    "stub": {
      "status": "ready",
      "description": "Mock responses (no API required)"
    },
    "local": {
      "status": "not_configured",
      "description": "Requires LLM_MODEL_PATH environment variable"
    },
    "huggingface": {
      "status": "not_configured",
      "description": "Requires HUGGINGFACE_API_KEY"
    }
  },
  "performance": {
    "avg_response_time_ms": 250,
    "requests_processed": 145
  }
}
```

---

## ❌ Error Codes

### HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid payload or validation error |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Insufficient permissions (RBAC) |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 500 | Internal Server Error | Backend processing error |
| 503 | Service Unavailable | LLM/database unavailable |

### Error Response Format

```json
{
  "detail": "Human-readable error description"
}
```

### Common Errors

**Invalid Case Payload:**
```json
{
  "detail": "Invalid case payload - missing required fields: customer_name"
}
```

**Case Not Found:**
```json
{
  "detail": "case not found"
}
```

**SAR Not Found:**
```json
{
  "detail": "sar not found"
}
```

**Unauthorized:**
```json
{
  "detail": "Invalid credentials"
}
```

**Insufficient Permissions:**
```json
{
  "detail": "Insufficient permissions: requires 'admin' role"
}
```

**Server Error:**
```json
{
  "detail": "Internal error: Database connection failed"
}
```

---

## 📊 Rate Limiting

Currently **not implemented** (no rate limits).

Future implementation:
- 100 requests/minute per IP
- 50 SAR generations/day per user
- 10 concurrent requests per session

---

## 🔄 Workflow Examples

### Complete SAR Workflow
```
1. POST /auth/login
   → Get access_token

2. POST /cases/create
   → case_id = CASE-a1b2c3d4

3. POST /sars/generate?case_id=CASE-a1b2c3d4
   → sar_id = SAR-x9y8z7u6
   → sar_draft = "On Feb 16..."
   → explain = {risk_score: 0.78}

4. GET /sars/export/SAR-x9y8z7u6
   → Download PDF file

5. GET /audit/case/CASE-a1b2c3d4
   → View all actions on this case
```

### Risk Analysis Workflow
```
1. GET /risk/analyze
   → Analyze transactions
   → Get risk_score + patterns

2. GET /rag/query?q=similar+pattern
   → Find similar cases from templates

3. POST /sars/generate?case_id=...
   → Auto-generate narrative using risk analysis + templates
```

---

## 🧪 Testing with cURL

### Create Case
```bash
curl -X POST http://localhost:8001/cases/create \
  -H "Content-Type: application/json" \
  -d @sample_case.json
```

### Generate SAR
```bash
curl -X POST http://localhost:8001/sars/generate?case_id=CASE-a1b2c3d4 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Audit Trail
```bash
curl -X GET "http://localhost:8001/audit/case/CASE-a1b2c3d4" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

This API enables complete SAR generation workflows with advanced compliance auditing.
