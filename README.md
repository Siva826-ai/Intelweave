# IntelWeave™ (HB-TRF) — Python Backend + AI Starter Kit

Court-safe, confidence-first intelligence analysis platform skeleton.

## Quick Start (Docker)
1. Copy env:
   ```bash
   cp .env.example .env
   ```
2. Run:
   ```bash
   docker compose up --build
   ```
3. Open:
   - API: http://localhost:8001
   - Swagger: http://localhost:8001/docs
   - Database: localhost:8088 (PostgreSQL)

## Principles
- **No prediction / no accusation**. AI outputs are *interpretive intelligence* with confidence + evidence basis.
- **Court Mode** is read-only and hides AI suggestions.
- **Integrity**: ingest validation scores, sha256 hashes, IP-tracked and append-only audit logs.

## Key Endpoints
- `/cases/summary`
- `/cases/{case_id}`
- `/ingest/upload`
- `/entities/search?q=`
- `/cases/{case_id}/insights`
- `/export/pdf` (Generate full Evidence Pack)

## Verification & Scripts
Inside the `api` container:
```bash
# Verify 'Court-Safe' Blueprint compliance
python scripts/verify_blueprint.py

# Seed demo data
python scripts/seed_demo_data.py
```

## Auth (v1.1)
- All endpoints require `Authorization: Bearer <JWT>`.
- JWT claims expected: `sub` (user_id), `email`, `clearance_level`, `roles`.
- Exports require clearance >= 2.

