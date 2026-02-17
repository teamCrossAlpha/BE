from sqlalchemy.orm import Session
from user.user_entity import User
from user.user_repository import save
from common.security import create_access_token, create_refresh_token
from refresh_token.refresh_repository import save_refresh_token

def generate_dev_token(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(
            email=email,
            provider="dev",
            provider_id=email
        )
        save(db, user)

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    save_refresh_token(db, user.id, refresh)

    return {
        "accessToken": access,
        "refreshToken": refresh,
        "userId": user.id
    }
