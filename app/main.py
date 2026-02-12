from fastapi import FastAPI
from app.api.routes_cases import router as cases_router
from app.api.routes_ingest import router as ingest_router
from app.api.routes_entities import router as entities_router
from app.api.routes_insights import router as insights_router
from app.api.routes_exports import router as exports_router
from app.api.routes_relationships import router as relationships_router
from app.api.routes_evidence import router as evidence_router
from app.api.routes_signals import router as signals_router
from app.api.routes_system import router as system_router


app = FastAPI(title="IntelWeave API", version="1.0")

app.include_router(cases_router, prefix="/cases", tags=["cases"])
app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
app.include_router(entities_router, prefix="/entities", tags=["entities"])
app.include_router(insights_router, prefix="/insights", tags=["insights"])
app.include_router(exports_router, prefix="/cases", tags=["export"])
app.include_router(relationships_router, prefix="/cases", tags=["relationships"])
app.include_router(evidence_router, prefix="/cases", tags=["evidence"])
app.include_router(signals_router, prefix="/signals", tags=["signals"])
app.include_router(system_router, prefix="/system", tags=["system"])


@app.get("/health")
def health():
    return {"status": "ok"}
