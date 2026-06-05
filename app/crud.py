from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional
from app import models, schemas

def create_contact(db: Session, contact_in: schemas.ContactCreate, user_id: int):
    contact = models.Contact(
        **contact_in.dict(),
        user_id=user_id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Contact)
        .filter(models.Contact.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_contact(db: Session, contact_id: int, user_id: int):
    return (
        db.query(models.Contact)
        .filter(
            models.Contact.id == contact_id,
            models.Contact.user_id == user_id
        )
        .first()
    )

def update_contact(db: Session, contact_id: int, contact_in: schemas.ContactUpdate, user_id: int):
    contact = get_contact(db, contact_id, user_id)
    if not contact:
        return None

    update_data = contact_in.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)
    return contact

def delete_contact(db: Session, contact_id: int, user_id: int):
    contact = get_contact(db, contact_id, user_id)
    if not contact:
        return False

    db.delete(contact)
    db.commit()
    return True

def search_contacts(db: Session, user_id: int, first_name=None, last_name=None, email=None):
    query = db.query(models.Contact).filter(models.Contact.user_id == user_id)

    if first_name:
        query = query.filter(models.Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(models.Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(models.Contact.email.ilike(f"%{email}%"))

    return query.all()

def upcoming_birthdays(db: Session, user_id: int):
    today = date.today()
    end = today + timedelta(days=7)

    contacts = (
        db.query(models.Contact)
        .filter(models.Contact.user_id == user_id)
        .all()
    )

    return [
        c for c in contacts
        if today <= c.birthday.replace(year=today.year) <= end
    ]
