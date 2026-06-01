import secrets

from fastapi import APIRouter, Depends, HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.core.security import create_access_token, hash_password, verify_password
from backend.dependencies.auth import get_optional_user
from backend.schemas.auth import GoogleAuthRequest, LoginRequest, RegisterRequest, TokenResponse
from database.connection import get_db
from database.models import GuestSession, User

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, {"email": user.email})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_admin=user.is_admin,
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not user.hashed_password or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id, {"email": user.email})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_admin=user.is_admin,
    )


@router.post("/google", response_model=TokenResponse)
def google_auth(body: GoogleAuthRequest, db: Session = Depends(get_db)):
    if not settings.google_client_id:
        raise HTTPException(status_code=501, detail="Google OAuth not configured")
    try:
        idinfo = id_token.verify_oauth2_token(
            body.id_token, google_requests.Request(), settings.google_client_id
        )
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid Google token") from exc

    email = idinfo.get("email")
    google_sub = idinfo.get("sub")
    user = db.query(User).filter((User.email == email) | (User.google_id == google_sub)).first()
    if not user:
        user = User(
            email=email,
            full_name=idinfo.get("name"),
            google_id=google_sub,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.google_id:
        user.google_id = google_sub
        db.commit()

    token = create_access_token(user.id, {"email": user.email})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_admin=user.is_admin,
    )


@router.post("/guest-session")
def create_guest_session(db: Session = Depends(get_db)):
    token = secrets.token_urlsafe(32)
    session = GuestSession(session_token=token)
    db.add(session)
    db.commit()
    return {"guest_session": token}


@router.get("/me")
def me(user_guest=Depends(get_optional_user), db: Session = Depends(get_db)):
    user, guest = user_guest
    if user:
        return {
            "authenticated": True,
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
        }
    return {"authenticated": False, "guest_session": guest.session_token if guest else None}
