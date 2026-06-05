from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.database import get_db
from app import models
from app.security import get_password_hash, verify_password, create_access_token
from app.config import settings
from app.schemas import UserCreate, UserResponse, TokenResponse


router = APIRouter(prefix="/auth", tags=["Auth"])

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

@router.post("/signup", response_model=UserResponse, status_code=201)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed_password = get_password_hash(user_data.password)

    new_user = models.User(
        email=user_data.email,
        hashed_password=hashed_password,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token_data = {
        "sub": str(new_user.id),
        "type": "verify",
        "exp": int((datetime.utcnow() + timedelta(hours=24)).timestamp())
    }
    verify_token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    verify_url = f"{settings.SERVER_HOST}/auth/verify?token={verify_token}"

    print("Verification link:", verify_url)

    message = MessageSchema(
        subject="Verify your email",
        recipients=[new_user.email],
        body=f"Click to verify your account: {verify_url}",
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    access_token = create_access_token({"sub": user.id})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    print("RECEIVED TOKEN:", token)

    from jose import JWTError, ExpiredSignatureError

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "verify":
            raise HTTPException(status_code=400, detail="Invalid token type")

        user_id = payload.get("sub")

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid token subject")

    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    db.commit()

    return {"message": "Email verified successfully"}


@router.delete("/delete/{user_id}", status_code=200)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": f"User with id {user_id} deleted successfully"}