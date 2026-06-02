from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=False)
    birthday = Column(Date, nullable=False)
    extra = Column(String(255), nullable=True)
