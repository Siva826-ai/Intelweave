from fastapi import FastAPI
from app.api.routes_cases import router as cases_router
from app.api.routes_ingest import router as ingest_router
from app.api.routes_entities import router as entities_router
from app.api.routes_insights import router as insights_router
from app.api.routes_exports import router as exports_router

app = FastAPI(title="IntelWeave API", version="1.0")

app.include_router(cases_router, prefix="/cases", tags=["cases"])
app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
app.include_router(entities_router, prefix="/entities", tags=["entities"])
app.include_router(insights_router, prefix="/insights", tags=["insights"])
app.include_router(exports_router, prefix="/export", tags=["export"])

@app.get("/health")
def health():
    return {"status": "ok"}
