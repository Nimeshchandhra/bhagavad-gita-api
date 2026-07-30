from typing import Generator
import os
from fastapi import Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session

from bhagavad_gita_api.db.session import SessionLocal
from bhagavad_gita_api.models.user import User

# Keep the header name the same so your scraper doesn't need to change
API_KEY_NAME = "X-API-KEY"
api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    api_key_header: str = Security(api_key_header_auth)
) -> User:
    """
    Bypasses the database check. 
    Compares the incoming header against the TESTER_API_KEY env var.
    """
    # Get the key from environment or default to your perfection key
    valid_key = os.getenv("TESTER_API_KEY", "my_perfection_key")
    
    if api_key_header != valid_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    
    # Return a dummy User object to satisfy FastAPI dependencies 
    # without needing a real database record.
    return User(
        full_name="Research Admin",
        email="admin@research.local",
        is_active=True
    )

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    # Since we hardcoded is_active=True above, this will always pass.
    return current_user