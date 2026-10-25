from .health import router as health_router
from .sos import router as sos_router
from .incidents import router as incidents_router
from .resources import router as resources_router
from .roads import router as roads_router
from .routes import router as routes_router
from .risk import router as risk_router

__all__ = [
    "health_router",
    "sos_router",
    "incidents_router",
    "resources_router",
    "roads_router",
    "routes_router",
    "risk_router",
]

