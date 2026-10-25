from fastapi import APIRouter
from ..core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "layer": "API",
        "engine": "Dijkstra + PyG GNN"
    }

