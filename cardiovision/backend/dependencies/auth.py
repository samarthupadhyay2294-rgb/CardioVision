from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from backend.core.security import decode_token
from database.connection import get_db
from database.models import GuestSession, User


def get_optional_user(
    authorization: str | None = Header(None),
    x_guest_session: str | None = Header(None),
    db: Session = Depends(get_db),
):
    user = None
    guest = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        payload = decode_token(token)
        if payload and payload.get("sub"):
            user = db.query(User).filter(User.id == payload["sub"]).first()
    if x_guest_session:
        guest = (
            db.query(GuestSession)
            .filter(GuestSession.session_token == x_guest_session)
            .first()
        )
    return user, guest


def require_user(user_guest=Depends(get_optional_user)):
    user, _ = user_guest
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_admin(user=Depends(require_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
