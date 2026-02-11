-- IntelWeave™ Core Schema (MySQL 8.0+)
-- Notes:
-- 1) Court-safety: immutable evidence/export hashes; audit logs for critical actions.
-- 2) Confidence-first: every relationship/insight has confidence_score.
-- 3) Integrity: ingestion validation_score and file sha256_hash.
-- 4) Uses CHAR(36) UUID strings for portability (application generates UUIDs).

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS users (
  user_id           CHAR(36) PRIMARY KEY,
  email             VARCHAR(320) NOT NULL UNIQUE,
  full_name         VARCHAR(255),
  clearance_level   SMALLINT NOT NULL DEFAULT 1,
  is_active         TINYINT(1) NOT NULL DEFAULT 1,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS roles (
  role_id           CHAR(36) PRIMARY KEY,
  role_name         VARCHAR(80) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user_roles (
  user_id           CHAR(36) NOT NULL,
  role_id           CHAR(36) NOT NULL,
  PRIMARY KEY (user_id, role_id),
  CONSTRAINT fk_user_roles_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  CONSTRAINT fk_user_roles_role FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cases (
  case_id           CHAR(36) PRIMARY KEY,
  title             VARCHAR(255) NOT NULL,
  status            ENUM('draft','active','on_hold','closed') NOT NULL,
  jurisdiction      VARCHAR(255),
  integrity_score   DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  created_by        CHAR(36),
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_cases_created_by FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS case_assignments (
  case_id           CHAR(36) NOT NULL,
  user_id           CHAR(36) NOT NULL,
  assigned_role     VARCHAR(60) NOT NULL DEFAULT 'analyst',
  PRIMARY KEY (case_id, user_id),
  CONSTRAINT fk_case_assign_case FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
  CONSTRAINT fk_case_assign_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ingest_jobs (
  job_id            CHAR(36) PRIMARY KEY,
  case_id           CHAR(36) NOT NULL,
  source_type       VARCHAR(40) NOT NULL,
  validation_score  DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  status            ENUM('queued','running','completed','failed') NOT NULL,
  started_at        TIMESTAMP NULL,
  completed_at      TIMESTAMP NULL,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_ingest_jobs_case FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ingest_files (
  file_id           CHAR(36) PRIMARY KEY,
  job_id            CHAR(36) NOT NULL,
  filename          VARCHAR(512) NOT NULL,
  file_type         VARCHAR(20) NOT NULL,
  sha256_hash       CHAR(64) NOT NULL,
  row_count         BIGINT,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_ingest_files_hash (sha256_hash),
  KEY idx_ingest_files_job (job_id),
  CONSTRAINT fk_ingest_files_job FOREIGN KEY (job_id) REFERENCES ingest_jobs(job_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS entities (
  entity_id         CHAR(36) PRIMARY KEY,
  entity_type       ENUM('person','phone','org','ip','device','vehicle','unknown') NOT NULL,
  label             VARCHAR(255) NOT NULL,
  risk_score        DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  confidence_score  DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  first_seen        TIMESTAMP NULL,
  last_seen         TIMESTAMP NULL,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS case_entities (
  case_id           CHAR(36) NOT NULL,
  entity_id         CHAR(36) NOT NULL,
  role_in_case      VARCHAR(60),
  PRIMARY KEY (case_id, entity_id),
  KEY idx_case_entities_entity (entity_id),
  CONSTRAINT fk_case_entities_case FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
  CONSTRAINT fk_case_entities_entity FOREIGN KEY (entity_id) REFERENCES entities(entity_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS relationships (
  rel_id            CHAR(36) PRIMARY KEY,
  case_id           CHAR(36) NOT NULL,
  source_entity_id  CHAR(36) NOT NULL,
  target_entity_id  CHAR(36) NOT NULL,
  basis             VARCHAR(40) NOT NULL,
  strength_score    DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  confidence_score  DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  first_seen        TIMESTAMP NULL,
  last_seen         TIMESTAMP NULL,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_rel_case (case_id),
  KEY idx_rel_src (source_entity_id),
  KEY idx_rel_tgt (target_entity_id),
  CONSTRAINT fk_rel_case FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
  CONSTRAINT fk_rel_src FOREIGN KEY (source_entity_id) REFERENCES entities(entity_id) ON DELETE RESTRICT,
  CONSTRAINT fk_rel_tgt FOREIGN KEY (target_entity_id) REFERENCES entities(entity_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS insights (
  insight_id        CHAR(36) PRIMARY KEY,
  case_id           CHAR(36) NOT NULL,
  severity          ENUM('low','medium','high','critical') NOT NULL,
  summary           TEXT NOT NULL,
  explanation       TEXT,
  confidence_score  DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  created_by        CHAR(36),
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_insights_case (case_id),
  KEY idx_insights_severity (severity),
  CONSTRAINT fk_insights_case FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
  CONSTRAINT fk_insights_created_by FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS evidence_items (
  evidence_id       CHAR(36) PRIMARY KEY,
  case_id           CHAR(36) NOT NULL,
  insight_id        CHAR(36) NULL,
  entity_id         CHAR(36) NULL,
  rel_id            CHAR(36) NULL,
  source_file_id    CHAR(36) NULL,
  evidence_type     VARCHAR(40) NOT NULL,
  description       TEXT,
  evidence_hash     CHAR(64) NOT NULL,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_evidence_hash (evidence_hash),
  KEY idx_evidence_case (case_id),
  CONSTRAINT fk_evidence_case FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
  CONSTRAINT fk_evidence_insight FOREIGN KEY (insight_id) REFERENCES insights(insight_id) ON DELETE SET NULL,
  CONSTRAINT fk_evidence_entity FOREIGN KEY (entity_id) REFERENCES entities(entity_id) ON DELETE SET NULL,
  CONSTRAINT fk_evidence_rel FOREIGN KEY (rel_id) REFERENCES relationships(rel_id) ON DELETE SET NULL,
  CONSTRAINT fk_evidence_file FOREIGN KEY (source_file_id) REFERENCES ingest_files(file_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS exports (
  export_id         CHAR(36) PRIMARY KEY,
  case_id           CHAR(36) NOT NULL,
  export_type       VARCHAR(40) NOT NULL,
  requested_by      CHAR(36) NULL,
  export_hash       CHAR(64) NOT NULL,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_exports_hash (export_hash),
  KEY idx_exports_case (case_id),
  CONSTRAINT fk_exports_case FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
  CONSTRAINT fk_exports_requested_by FOREIGN KEY (requested_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS audit_logs (
  log_id            CHAR(36) PRIMARY KEY,
  user_id           CHAR(36) NOT NULL,
  case_id           CHAR(36) NULL,
  action            VARCHAR(120) NOT NULL,
  target_type       VARCHAR(60),
  target_id         VARCHAR(120),
  ip_address        VARCHAR(64),
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_audit_user (user_id),
  KEY idx_audit_case (case_id),
  KEY idx_audit_time (created_at),
  CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  CONSTRAINT fk_audit_case FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE SET NULL
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;
