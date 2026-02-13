# IntelWeave Project Flow Documentation

## Overview
IntelWeave is a **court-safe, confidence-first intelligence analysis platform** built with FastAPI. It's designed for legal/investigative use cases where AI outputs must be interpretable, auditable, and evidence-based.

## Architecture Layers

### 1. **Entry Point** (`app/main.py`)
- FastAPI application initialization
- Registers all route modules with prefixes:
  - `/cases` - Case management
  - `/ingest` - Data ingestion
  - `/entities` - Entity search and retrieval
  - `/insights` - AI-generated insights
  - `/cases/{id}/relationships` - Entity relationships
  - `/cases/{id}/evidence` - Evidence items
  - `/export/pdf` - Court-safe Evidence Pack generation
- Health check endpoint at `/health`

### 2. **Security Layer** (`app/core/security.py`)
- **JWT-based authentication** (requires `PyJWT` package - currently missing)
- Bearer token validation via `HTTPBearer`
- **Clearance levels**: Minimum clearance required per endpoint (default: level 1)
- **Role-based access**: Optional role checking via `require_roles()`
- User context extracted from JWT: `user_id`, `email`, `clearance_level`, `roles`

**Flow:**
```
Request → HTTPBearer extracts token → decode_token() → CurrentUser object → Clearance/Role check
```

### 3. **Database Layer**

#### Models (`app/db/models.py`)
Core entities:
- **User**: Authentication and authorization
- **Case**: Main investigation container
- **Entity**: People, organizations, locations, etc.
- **Relationship**: Links between entities (with strength/confidence scores)
- **Insight**: AI-generated findings linked to cases
- **EvidenceItem**: Individual evidence pieces (with SHA256 hashes)
- **IngestJob/IngestFile**: File upload tracking
- **Export**: Export history
- **AuditLog**: IP-tracked, append-only audit trail

#### Session Management (`app/db/session.py`)
- SQLAlchemy session factory
- Dependency injection via `get_db()` for FastAPI routes
- PostgreSQL connection (configurable via `DATABASE_URL`)

#### Schemas (`app/db/schemas.py`)
- Pydantic models for request/response validation
- `*Create` schemas for input
- `*Out` schemas for output
- `DataResponse[T]` generic wrapper for API responses

### 4. **API Routes Layer** (`app/api/`)

#### Request Flow Pattern:
```
HTTP Request → Route Handler → Security Guard (clearance check) → Service Layer → Database → Response
```

#### Route Modules:

**`routes_cases.py`**
- `GET /cases/summary` - Dashboard statistics
- `GET /cases/{case_id}` - Get case details
- `GET /cases/{case_id}/stats` - Case statistics (stub)

**`routes_ingest.py`**
- `POST /ingest/upload` - Upload files for processing
  - Creates `IngestJob` record
  - Calculates SHA256 hash for each file
  - Creates `IngestFile` records
  - Returns job_id and file_ids

**`routes_entities.py`**
- `GET /entities/search?q=...` - Search entities by label
- `GET /entities/{entity_id}` - Get entity details

**`routes_insights.py`**
- `GET /insights/case/{case_id}` - List insights for a case
- `POST /insights/hypothesis` - Create hypothesis (stub for AI pipeline)

**`routes_relationships.py`**
- `POST /cases/{case_id}/relationships` - Create relationship between entities
- `GET /cases/{case_id}/relationships` - List relationships for a case

**`routes_evidence.py`**
- `POST /cases/{case_id}/evidence` - Create evidence item
  - Enforces "Court Mode" (read-only when enabled)

**`routes_exports.py`**
- `POST /export/pdf` - Generate full court-safe PDF (requires clearance >= 2)

### 5. **Service Layer** (`app/services/`)

Business logic separated from routes:

- **`ingest_service.py`**: Creates ingest jobs and file records
- **`relationship_service.py`**: Manages entity relationships
- **`evidence_service.py`**: Creates evidence items with hashing
- **`insight_service.py`**: AI insight generation
- **`export_service.py`**: Export generation
- **`audit_service.py`**: Append-only audit logging

**Pattern:**
- Services receive `db: Session` and business data
- Perform database operations
- Call `audit_service.log_action()` for compliance
- Return model instances or schemas

### 6. **AI/ML Layer** (`app/ai/`)

- **`inference.py`**: Model scoring (loads joblib models, predicts confidence)
- **`models.py`**: Model definitions
- **`training.py`**: Model training scripts
- **`explain.py`**: Model explainability
- **`drift.py`**: Model drift detection

**Flow:**
- Models stored in `artifacts/` directory
- Inference loads models and scores relationships/entities
- Confidence scores stored in database

### 7. **Feature Engineering** (`app/features/`)

- **`graph_features.py`**: Network/graph-based features
- **`temporal_features.py`**: Time-based features

### 8. **Ingest Processing** (`app/ingest/`)

- **`parsers.py`**: File parsing (CSV, Excel → pandas DataFrame)
- **`validators.py`**: Data validation and integrity checks

## Data Flow Examples

### Example 1: File Upload Flow
```
1. POST /ingest/upload
   ↓
2. Security: require_clearance(1) checks JWT token
   ↓
3. Route creates IngestJobCreate schema
   ↓
4. ingest_service.create_ingest_job() creates IngestJob
   ↓
5. For each file:
   - Calculate SHA256 hash
   - ingest_service.add_file_to_job() creates IngestFile
   ↓
6. audit_service.log_action() records the action
   ↓
7. Return job_id and file_ids
```

### Example 2: Entity Relationship Creation
```
1. POST /cases/{case_id}/relationships
   ↓
2. Security check (clearance level)
   ↓
3. Validate RelationshipCreate schema
   ↓
4. relationship_service.create_relationship()
   - Creates Relationship model
   - Links to case and entities
   ↓
5. Audit log entry
   ↓
6. Return RelationshipOut with metadata
```

### Example 3: Insight Generation (AI)
```
1. POST /insights/hypothesis (or background job)
   ↓
2. Load case data, entities, relationships
   ↓
3. Extract features (graph_features, temporal_features)
   ↓
4. ai.inference.score_links() or similar
   ↓
5. Create Insight record with:
   - severity
   - summary
   - explanation
   - confidence_score
   ↓
6. Link to case
```

## Key Design Principles

1. **Court-Safe**: 
   - All evidence has SHA256 hashes
   - Append-only audit logs
   - "Court Mode" prevents modifications

2. **Confidence-First**:
   - All AI outputs include confidence scores
   - Scores stored as Numeric(5,2) in database
   - Confidence displayed in API responses

3. **Integrity**:
   - Validation scores for ingested data
   - Integrity scores for cases
   - Hash-based deduplication

4. **Auditability**:
   - Every action logged via `audit_service` with **IP tracking**
   - User tracking via JWT claims
   - Timestamps on all records

## Configuration

**`app/core/config.py`**:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret for JWT token validation

## Dependencies

Key packages (from `requirements.txt`):
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `psycopg2-binary` - PostgreSQL driver
- `PyJWT` - JWT handling (⚠️ **Currently missing - causes import error**)
- `pandas`, `numpy` - Data processing
- `networkx` - Graph analysis
- `scikit-learn` - ML models
- `joblib` - Model serialization

## Current Issue

**ModuleNotFoundError: No module named 'jwt'**

The code imports `jwt` but the package is listed as `PyJWT` in requirements.txt. The import should be:
```python
import jwt  # This works with PyJWT package
```

However, the package may not be installed. Solution: Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure Summary

```
IntelWeave/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── api/                 # Route handlers
│   ├── core/                # Config, security, logging
│   ├── db/                  # Models, schemas, session
│   ├── services/            # Business logic
│   ├── ai/                  # ML models and inference
│   ├── features/            # Feature engineering
│   ├── ingest/              # File parsing/validation
│   └── utils/               # Utilities
├── scripts/                 # Training, verification scripts
├── schema/                 # SQL schema files
├── requirements.txt        # Python dependencies
└── docker-compose.yml      # Docker setup
```

## Next Steps for Development

1. **Fix JWT import issue**: Ensure `PyJWT` is installed
2. **Complete stub endpoints**: Implement `/cases/{id}/stats`, `/insights/hypothesis`
3. **Wire up AI pipeline**: Connect inference to insight generation
4. **Add user authentication endpoint**: JWT token generation
5. **Implement export functionality**: PDF generation, etc.
6. **Add background job processing**: For ingest file processing
7. **Complete Court Mode**: Read-only enforcement across all endpoints

