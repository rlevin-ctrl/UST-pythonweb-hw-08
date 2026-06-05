from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import Base, engine, get_db
from app import models, schemas, crud
from app.security import get_current_user
from app.auth import router as auth_router
from app.avatar import router as avatar_router

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contacts API", version="2.0.0")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return PlainTextResponse("Too many requests", status_code=429)


app.include_router(auth_router)
app.include_router(avatar_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/users/me", response_model=schemas.UserResponse)
@limiter.limit("5/minute")
def get_me(
    request: Request,  # ← додано для SlowAPI
    current_user: models.User = Depends(get_current_user)
):
    return current_user


@app.post("/contacts", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_contact(db, contact, user_id=current_user.id)


@app.get("/contacts", response_model=List[schemas.ContactResponse])
def list_contacts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_contacts(db, user_id=current_user.id, skip=skip, limit=limit)


@app.get("/contacts/search", response_model=List[schemas.ContactResponse])
def search(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.search_contacts(
        db,
        user_id=current_user.id,
        first_name=first_name,
        last_name=last_name,
        email=email
    )


@app.get("/contacts/birthdays", response_model=List[schemas.ContactResponse])
def birthdays(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.upcoming_birthdays(db, user_id=current_user.id)


@app.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    contact = crud.get_contact(db, contact_id, user_id=current_user.id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@app.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def update_contact_endpoint(
    contact_id: int,
    contact_in: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    contact = crud.update_contact(db, contact_id, contact_in, user_id=current_user.id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    ok = crud.delete_contact(db, contact_id, user_id=current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Contact not found")
    return
