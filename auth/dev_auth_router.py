from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from common.database import get_db
from common.config import settings
from auth.auth_schema import DevTokenRequest, DevTokenResponse
from auth.dev_auth_service import generate_dev_token

router = APIRouter(prefix="/api/auth", tags=["DEV"])

@router.post("/dev-token", response_model=DevTokenResponse)
def dev_token(
    req: DevTokenRequest,
    db: Session = Depends(get_db)
):
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Not allowed")

    return generate_dev_token(db, req.email)
