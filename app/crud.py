from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional
from app import models, schemas

def create_contact(db: Session, contact_in: schemas.ContactCreate):
    contact = models.Contact(**contact_in.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).offset(skip).limit(limit).all()

def get_contact(db: Session, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()

def update_contact(db: Session, contact_id: int, contact_in: schemas.ContactUpdate):
    contact = get_contact(db, contact_id)
    if not contact:
        return None

    update_data = contact_in.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(db: Session, contact_id: int):
    contact = get_contact(db, contact_id)
    if not contact:
        return False
    db.delete(contact)
    db.commit()
    return True

def search_contacts(db: Session, first_name=None, last_name=None, email=None):
    query = db.query(models.Contact)
    if first_name:
        query = query.filter(models.Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(models.Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(models.Contact.email.ilike(f"%{email}%"))
    return query.all()

def upcoming_birthdays(db: Session):
    today = date.today()
    end = today + timedelta(days=7)
    contacts = db.query(models.Contact).all()
    return [
        c for c in contacts
        if today <= c.birthday.replace(year=today.year) <= end
    ]
