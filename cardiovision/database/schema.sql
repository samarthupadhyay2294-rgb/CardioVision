-- CardioVision PostgreSQL schema (reference; SQLAlchemy creates tables on startup)

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE,
    google_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS guest_sessions (
    id VARCHAR(36) PRIMARY KEY,
    session_token VARCHAR(64) UNIQUE NOT NULL,
    user_id VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS reports (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    guest_session_id VARCHAR(36) REFERENCES guest_sessions(id),
    file_name VARCHAR(512) NOT NULL,
    file_path VARCHAR(1024) NOT NULL,
    file_type VARCHAR(32) NOT NULL,
    status VARCHAR(32) DEFAULT 'uploaded',
    ocr_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS predictions (
    id VARCHAR(36) PRIMARY KEY,
    report_id VARCHAR(36) UNIQUE REFERENCES reports(id),
    risk_pct FLOAT NOT NULL,
    risk_category VARCHAR(64) NOT NULL,
    disease_risks JSONB NOT NULL,
    shap_factors JSONB NOT NULL,
    explanations JSONB NOT NULL,
    features JSONB NOT NULL,
    pdf_path VARCHAR(1024),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS extracted_parameters (
    id VARCHAR(36) PRIMARY KEY,
    report_id VARCHAR(36) UNIQUE REFERENCES reports(id),
    raw_data JSONB NOT NULL,
    ml_features JSONB NOT NULL,
    parameter_table JSONB NOT NULL,
    patient_summary JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS recommendations (
    id VARCHAR(36) PRIMARY KEY,
    prediction_id VARCHAR(36) UNIQUE REFERENCES predictions(id),
    content JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    action VARCHAR(128) NOT NULL,
    actor_id VARCHAR(36),
    meta JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS settings (
    key VARCHAR(128) PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notifications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
