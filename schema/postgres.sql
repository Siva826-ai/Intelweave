-- IntelWeave™ Core Schema (PostgreSQL)
-- Notes:
-- 1) Court-safety: immutable evidence/export hashes; audit logs for every critical action.
-- 2) Confidence-first: every relationship/insight has confidence_score.
-- 3) Integrity: ingestion validation_score and file sha256_hash.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- USERS & ROLES
CREATE TABLE IF NOT EXISTS users (
  user_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email             TEXT NOT NULL UNIQUE,
  full_name         TEXT,
  clearance_level   SMALLINT NOT NULL DEFAULT 1,
  is_active         BOOLEAN NOT NULL DEFAULT TRUE,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roles (
  role_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role_name         TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS user_roles (
  user_id           UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  role_id           UUID NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);

-- CASES
CREATE TABLE IF NOT EXISTS cases (
  case_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title             TEXT NOT NULL,
  status            TEXT NOT NULL CHECK (status IN ('draft','active','on_hold','closed')),
  jurisdiction      TEXT,
  integrity_score   NUMERIC(5,2) NOT NULL DEFAULT 0.00 CHECK (integrity_score >= 0 AND integrity_score <= 100),
  created_by        UUID REFERENCES users(user_id) ON DELETE SET NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS case_assignments (
  case_id           UUID NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
  user_id           UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  assigned_role     TEXT NOT NULL DEFAULT 'analyst',
  PRIMARY KEY (case_id, user_id)
);

-- INGESTION
CREATE TABLE IF NOT EXISTS ingest_jobs (
  job_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id           UUID NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
  source_type       TEXT NOT NULL, -- e.g., 'cdr','tower_dump','ip_logs','finance'
  validation_score  NUMERIC(5,2) NOT NULL DEFAULT 0.00 CHECK (validation_score >= 0 AND validation_score <= 100),
  status            TEXT NOT NULL CHECK (status IN ('queued','running','completed','failed')),
  started_at        TIMESTAMPTZ,
  completed_at      TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ingest_files (
  file_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id            UUID NOT NULL REFERENCES ingest_jobs(job_id) ON DELETE CASCADE,
  filename          TEXT NOT NULL,
  file_type         TEXT NOT NULL, -- csv/xlsx/pdf/json
  sha256_hash       TEXT NOT NULL,
  row_count         BIGINT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ingest_jobs_case ON ingest_jobs(case_id);
CREATE INDEX IF NOT EXISTS idx_ingest_files_job ON ingest_files(job_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_ingest_files_hash ON ingest_files(sha256_hash);

-- ENTITIES
CREATE TABLE IF NOT EXISTS entities (
  entity_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_type       TEXT NOT NULL CHECK (entity_type IN ('person','phone','org','ip','device','vehicle','unknown')),
  label             TEXT NOT NULL,
  risk_score        NUMERIC(5,2) NOT NULL DEFAULT 0.00 CHECK (risk_score >= 0 AND risk_score <= 100),
  confidence_score  NUMERIC(5,2) NOT NULL DEFAULT 0.00 CHECK (confidence_score >= 0 AND confidence_score <= 100),
  first_seen        TIMESTAMPTZ,
  last_seen         TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS case_entities (
  case_id           UUID NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
  entity_id         UUID NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
  role_in_case      TEXT, -- subject/suspect/witness/unknown
  PRIMARY KEY (case_id, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_case_entities_case ON case_entities(case_id);
CREATE INDEX IF NOT EXISTS idx_case_entities_entity ON case_entities(entity_id);

-- RELATIONSHIPS (within a case context)
CREATE TABLE IF NOT EXISTS relationships (
  rel_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id           UUID NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
  source_entity_id  UUID NOT NULL REFERENCES entities(entity_id) ON DELETE RESTRICT,
  target_entity_id  UUID NOT NULL REFERENCES entities(entity_id) ON DELETE RESTRICT,
  basis             TEXT NOT NULL, -- 'tower','time','ip','finance','device','manual'
  strength_score    NUMERIC(5,2) NOT NULL DEFAULT 0.00 CHECK (strength_score >= 0 AND strength_score <= 100),
  confidence_score  NUMERIC(5,2) NOT NULL DEFAULT 0.00 CHECK (confidence_score >= 0 AND confidence_score <= 100),
  first_seen        TIMESTAMPTZ,
  last_seen         TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_relationships_case ON relationships(case_id);
CREATE INDEX IF NOT EXISTS idx_relationships_src ON relationships(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_tgt ON relationships(target_entity_id);

-- INSIGHTS (interpretive intelligence, not prediction)
CREATE TABLE IF NOT EXISTS insights (
  insight_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id           UUID NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
  severity          TEXT NOT NULL CHECK (severity IN ('low','medium','high','critical')),
  summary           TEXT NOT NULL,
  explanation       TEXT,
  confidence_score  NUMERIC(5,2) NOT NULL DEFAULT 0.00 CHECK (confidence_score >= 0 AND confidence_score <= 100),
  created_by        UUID REFERENCES users(user_id) ON DELETE SET NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_insights_case ON insights(case_id);
CREATE INDEX IF NOT EXISTS idx_insights_severity ON insights(severity);

-- EVIDENCE ITEMS (hash-anchored, court-safe)
CREATE TABLE IF NOT EXISTS evidence_items (
  evidence_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id           UUID NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
  insight_id        UUID REFERENCES insights(insight_id) ON DELETE SET NULL,
  entity_id         UUID REFERENCES entities(entity_id) ON DELETE SET NULL,
  rel_id            UUID REFERENCES relationships(rel_id) ON DELETE SET NULL,
  source_file_id    UUID REFERENCES ingest_files(file_id) ON DELETE SET NULL,
  evidence_type     TEXT NOT NULL, -- 'cdr_record','tower_event','ip_event','analysis_note','snapshot'
  description       TEXT,
  evidence_hash     TEXT NOT NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_evidence_hash ON evidence_items(evidence_hash);
CREATE INDEX IF NOT EXISTS idx_evidence_case ON evidence_items(case_id);

-- EXPORTS (evidence packages)
CREATE TABLE IF NOT EXISTS exports (
  export_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id           UUID NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
  export_type       TEXT NOT NULL, -- 'pdf','csv','network_snapshot','timeline'
  requested_by      UUID REFERENCES users(user_id) ON DELETE SET NULL,
  export_hash       TEXT NOT NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_exports_hash ON exports(export_hash);
CREATE INDEX IF NOT EXISTS idx_exports_case ON exports(case_id);

-- AUDIT LOGS (immutable record of actions)
CREATE TABLE IF NOT EXISTS audit_logs (
  log_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  case_id           UUID REFERENCES cases(case_id) ON DELETE SET NULL,
  action            TEXT NOT NULL,
  target_type       TEXT,
  target_id         TEXT,
  ip_address        TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_case ON audit_logs(case_id);
CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_logs(created_at);
