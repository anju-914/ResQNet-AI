from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from .config import settings

security_bearer = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="x-coordinator-key", auto_error=False)

def verify_coordinator_auth(
    credentials: HTTPAuthorizationCredentials | None = Security(security_bearer),
    api_key: str | None = Security(api_key_header)
) -> bool:
    """
    Verifies that the caller is authenticated as a coordinator.
    Supports Bearer token (JWT placeholder/mock) or direct API key header.
    In local dev / demo mode, allows default credentials.
    """
    if api_key and api_key == settings.COORDINATOR_API_KEY:
        return True
    
    if credentials and credentials.credentials in (settings.COORDINATOR_BEARER_TOKEN, settings.COORDINATOR_API_KEY):
        return True

    # If neither matched, reject
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing coordinator credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

