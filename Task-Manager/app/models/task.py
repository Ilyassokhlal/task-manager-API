from sqlalchemy import Boolean, String, Column, Integer, DateTime, func 
from app.database import Base
from sqlalchemy import ForeignKey

class Task(Base):
    __tablename__="tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(String(20), default="medium")
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)