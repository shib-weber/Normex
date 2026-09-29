from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.auth_middleware import AuthMiddleware
from app.services.seed_service import seed_demo, seed_procurement_workflow
from app.core.config import settings
from app.db.database import init_db
from app.routes.analysis_routes import router as analysis_router
from app.api import analysis, standards, documents, tender, reports, graph, compliance, basket, evaluation, health, auth, demo, procurement, organizations

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    from app.db.database import SessionLocal
    db=SessionLocal()
    try:
        seed_demo(db)
        seed_procurement_workflow(db)
    finally: db.close()
    yield

app = FastAPI(
    title="NORMEX API",
    version="0.2.0",
    description="Indian Standards & Procurement Intelligence Platform",
    lifespan=lifespan,
)

origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(demo.router, prefix="/api/v1")
app.include_router(procurement.router, prefix="/api/v1")
app.include_router(organizations.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(standards.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(tender.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(graph.router, prefix="/api/v1")
app.include_router(compliance.router, prefix="/api/v1")
app.include_router(basket.router, prefix="/api/v1")
app.include_router(evaluation.router, prefix="/api/v1")
app.include_router(analysis_router)
