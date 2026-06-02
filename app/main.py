from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import Base, engine, get_db
from app import models, schemas, crud

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contacts API", version="1.0.0")

@app.post("/contacts", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db, contact)

@app.get("/contacts", response_model=List[schemas.ContactResponse])
def list_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_contacts(db, skip=skip, limit=limit)

@app.get("/contacts/search", response_model=List[schemas.ContactResponse])
def search(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.search_contacts(db, first_name, last_name, email)

@app.get("/contacts/birthdays", response_model=List[schemas.ContactResponse])
def birthdays(db: Session = Depends(get_db)):
    return crud.upcoming_birthdays(db)

@app.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = crud.get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def update_contact_endpoint(contact_id: int, contact_in: schemas.ContactUpdate, db: Session = Depends(get_db)):
    contact = crud.update_contact(db, contact_id, contact_in)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_contact(db, contact_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Contact not found")
    return
