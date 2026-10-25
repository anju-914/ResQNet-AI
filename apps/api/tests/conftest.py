import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from apps.api.app.main import app
from apps.api.app.db.session import SessionLocal
from apps.api.app.services.routing_service import routing_engine

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        # Ensure routing graph is loaded
        with SessionLocal() as db:
            routing_engine.load_graph_from_db(db)
        yield test_client

