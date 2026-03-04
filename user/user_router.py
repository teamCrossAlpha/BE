from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from common.database import get_db
from common.dependencies import get_current_user_id
from user.user_entity import User
from user.user_schema import UserResponse

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    return user