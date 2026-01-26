from sqlalchemy import Column, Integer , Float , String, Boolean, Date, DateTime, Text
from sqlalchemy.orm import relationship
from Table.Base import Base

class Orginization(Base):
    __tablename__ = "OrginizationTable"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    estabishDate = Column(Date, nullable=True)
    country = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    postalCode = Column(String(20), nullable=True)
    isActive = Column(Boolean, default=True, nullable=False)
    createdAt = Column(DateTime, nullable=False)
    updatedAt = Column(DateTime, nullable=False)