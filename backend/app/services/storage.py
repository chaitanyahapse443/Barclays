import sqlite3
import json
import os
from datetime import datetime

DB_FILE = r"C:\barcklays_hackathon\Barclays\backend\sar_ai.db"

DB_FILE = os.path.normpath(DB_FILE)

def _conn():
    return sqlite3.connect(DB_FILE)

def save_case(payload: dict):
    conn = _conn()
    try:
        cur = conn.cursor()
        case_id = payload.get('case_id')
        cur.execute('INSERT OR REPLACE INTO cases(case_id, customer_id, payload) VALUES (?,?,?)',
                    (case_id, payload.get('customer_id'), json.dumps(payload)))
        conn.commit()
        return case_id
    finally:
        conn.close()

def get_case(case_id: str):
    conn = _conn()
    try:
        cur = conn.cursor()
        r = cur.execute('SELECT payload FROM cases WHERE case_id=?', (case_id,)).fetchone()
        if not r:
            return None
        return json.loads(r[0])
    finally:
        conn.close()

def save_sar(sar_id: str, case_id: str, draft: str, audit: dict):
    conn = _conn()
    try:
        cur = conn.cursor()
        # ensure sars table exists
        cur.execute('CREATE TABLE IF NOT EXISTS sars (sar_id TEXT PRIMARY KEY, case_id TEXT, draft TEXT, audit TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS sar_versions (version_id TEXT PRIMARY KEY, sar_id TEXT, case_id TEXT, draft TEXT, audit TEXT, created_at TEXT)')
        cur.execute('INSERT OR REPLACE INTO sars(sar_id, case_id, draft, audit) VALUES (?,?,?,?)',
                    (sar_id, case_id, draft, json.dumps(audit)))
        # insert a version entry
        version_id = f"VER-{int(datetime.utcnow().timestamp())}-{sar_id}"
        cur.execute('INSERT INTO sar_versions(version_id, sar_id, case_id, draft, audit, created_at) VALUES (?,?,?,?,?,?)',
                    (version_id, sar_id, case_id, draft, json.dumps(audit), datetime.utcnow().isoformat()))
        conn.commit()
        return sar_id
    finally:
        conn.close()

def save_audit(audit_id: str, case_id: str, user_id: str, action: str, details: dict):
    conn = _conn()
    try:
        cur = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        cur.execute('INSERT INTO audit_logs(audit_id, case_id, user_id, action, details, timestamp) VALUES (?,?,?,?,?,?)',
                    (audit_id, case_id, user_id, action, json.dumps(details), timestamp))
        conn.commit()
        return audit_id
    finally:
        conn.close()

def get_audit_logs(case_id: str):
    conn = _conn()
    try:
        cur = conn.cursor()
        rows = cur.execute('SELECT audit_id, user_id, action, details, timestamp FROM audit_logs WHERE case_id=? ORDER BY timestamp DESC', (case_id,)).fetchall()
        return [
            {'audit_id': r[0], 'user_id': r[1], 'action': r[2], 'details': json.loads(r[3]) if r[3] else {}, 'timestamp': r[4]}
            for r in rows
        ]
    finally:
        conn.close()

def get_sar_by_id(sar_id: str):
    conn = _conn()
    try:
        cur = conn.cursor()
        r = cur.execute('SELECT sar_id, case_id, draft, audit FROM sars WHERE sar_id=?', (sar_id,)).fetchone()
        if not r:
            return None
        return {'sar_id': r[0], 'case_id': r[1], 'draft': r[2], 'audit': json.loads(r[3]) if r[3] else {}}
    finally:
        conn.close()

def get_sar_versions(case_id: str):
    conn = _conn()
    try:
        cur = conn.cursor()
        rows = cur.execute('SELECT version_id, sar_id, draft, audit, created_at FROM sar_versions WHERE case_id=? ORDER BY created_at DESC', (case_id,)).fetchall()
        return [
            {'version_id': r[0], 'sar_id': r[1], 'draft': r[2], 'audit': json.loads(r[3]) if r[3] else {}, 'created_at': r[4]}
            for r in rows
        ]
    finally:
        conn.close()
