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
   - API: http://localhost:8000
   - Swagger: http://localhost:8000/docs

## Principles
- **No prediction / no accusation**. AI outputs are *interpretive intelligence* with confidence + evidence basis.
- **Court Mode** is read-only and hides AI suggestions.
- **Integrity**: ingest validation scores, sha256 hashes, append-only audit logs.

## Key Endpoints
- `/cases/summary`
- `/cases/{case_id}`
- `/ingest/upload`
- `/entities/search?q=`
- `/cases/{case_id}/insights`
- `/export/pdf` (stub for packaging)

## Training
Run (inside container or local venv):
```bash
python scripts/train_models.py
```

Artifacts saved to `artifacts/`.


## Auth (v1.1)
- All endpoints require `Authorization: Bearer <JWT>`.
- JWT claims expected: `sub` (user_id), `email`, `clearance_level`, `roles`.
- Exports require clearance >= 2.

Example payload:
```json
{
  "sub": "<uuid>",
  "email": "analyst@org",
  "clearance_level": 2,
  "roles": ["analyst"]
}
```
