from sqlalchemy import Boolean, DateTime, String, Column, Integer, func
from app.database import Base

class User(Base):
    """SQLAlchemy model for the users table"""
    __tablename__="users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(72), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())