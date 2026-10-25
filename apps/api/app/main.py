from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db.session import engine, Base, SessionLocal
from .services.routing_service import routing_engine
from .routers import (
    health_router,
    sos_router,
    incidents_router,
    resources_router,
    roads_router,
    routes_router,
    risk_router,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize DB tables
    Base.metadata.create_all(bind=engine)
    
    # 2. Synchronize road network graph into routing engine
    with SessionLocal() as db:
        routing_engine.load_graph_from_db(db)
        
    yield
    # Shutdown steps if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Emergency SOS Ingestion, Verification, and Graph-based Disaster Routing System",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 Routers
prefix = settings.API_V1_PREFIX
app.include_router(health_router, prefix=prefix)
app.include_router(sos_router, prefix=prefix)
app.include_router(incidents_router, prefix=prefix)
app.include_router(resources_router, prefix=prefix)
app.include_router(roads_router, prefix=prefix)
app.include_router(routes_router, prefix=prefix)
app.include_router(risk_router, prefix=prefix)

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs",
        "health_url": f"{prefix}/health"
    }

