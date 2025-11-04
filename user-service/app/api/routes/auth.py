from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.database import SessionLocal, Base, engine
from app.models.user import User, RefreshToken, AuditLog
from app.schemas.user import UserCreate, UserOut, Token
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
import os

Base.metadata.create_all(bind=engine)
router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

LOCK_THRESHOLD = int(os.getenv("LOCK_THRESHOLD", "5"))
LOCK_MINUTES = int(os.getenv("LOCK_MINUTES", "15"))

@router.post("/register", response_model=UserOut)
def register(u: UserCreate, request: Request, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == u.email).first():
        raise HTTPException(400, "Email already registered")
    new = User(
        username=u.username, email=u.email,
        hashed_password=hash_password(u.password),
        role=u.role, org_id=u.org_id
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    db.add(AuditLog(user_id=new.id, action="register", ip=request.client.host))
    db.commit()
    return new

@router.post("/login", response_model=Token)
def login(payload: dict, request: Request, db: Session = Depends(get_db)):
    # payload expected: {"email": "...", "password": "..."}
    email = payload.get("email")
    password = payload.get("password")
    user = db.query(User).filter(User.email == email).first()
    ip = request.client.host if request.client else None

    if not user:
        raise HTTPException(401, "Invalid credentials")

    # check lock
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(403, f"Account locked until {user.locked_until}")

    if not verify_password(password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= LOCK_THRESHOLD:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCK_MINUTES)
        db.add(user)
        db.commit()
        db.add(AuditLog(user_id=user.id if user else None, action="failed_login", ip=ip))
        db.commit()
        raise HTTPException(401, "Invalid credentials")

    # successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    db.add(user)
    db.commit()

    access = create_access_token({"sub": user.email, "role": user.role, "user_id": user.id})
    refresh = create_refresh_token()
    expires_at = datetime.utcnow() + timedelta(days=int(os.getenv("REFRESH_EXPIRE_DAYS", "30")))

    rt = RefreshToken(user_id=user.id, token=refresh, expires_at=expires_at)
    db.add(rt)
    db.add(AuditLog(user_id=user.id, action="login", ip=ip))
    db.commit()

    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
def refresh_token(payload: dict, db: Session = Depends(get_db)):
    # payload: {"refresh_token": "..."}
    token = payload.get("refresh_token")
    db_rt = db.query(RefreshToken).filter(RefreshToken.token == token, RefreshToken.revoked == False).first()
    if not db_rt or db_rt.expires_at < datetime.utcnow():
        raise HTTPException(401, "Invalid refresh token")

    user = db.query(User).filter(User.id == db_rt.user_id).first()
    if not user:
        raise HTTPException(401, "Invalid user")

    access = create_access_token({"sub": user.email, "role": user.role, "user_id": user.id})
    # rotate refresh token: revoke old, issue new
    db_rt.revoked = True
    new_refresh = create_refresh_token()
    expires_at = datetime.utcnow() + timedelta(days=int(os.getenv("REFRESH_EXPIRE_DAYS", "30")))
    new_rt = RefreshToken(user_id=user.id, token=new_refresh, expires_at=expires_at)
    db.add(db_rt); db.add(new_rt); db.commit()
    return {"access_token": access, "refresh_token": new_refresh, "token_type": "bearer"}

@router.post("/logout")
def logout(payload: dict, db: Session = Depends(get_db)):
    token = payload.get("refresh_token")
    rt = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if rt:
        rt.revoked = True
        db.add(rt)
        db.commit()
    return {"status": "logged_out"}
