-- Basic schema for prototype (expand in real project)
CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    customer_id TEXT,
    payload TEXT
);

CREATE TABLE IF NOT EXISTS sars (
    sar_id TEXT PRIMARY KEY,
    case_id TEXT,
    draft TEXT,
    audit TEXT
);

CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id TEXT PRIMARY KEY,
    case_id TEXT,
    user_id TEXT,
    action TEXT,
    details TEXT,
    timestamp TEXT
);
