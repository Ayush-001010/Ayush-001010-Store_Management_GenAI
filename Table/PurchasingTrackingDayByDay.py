from sqlalchemy import Column, Integer , Float , String, Boolean, Date, DateTime, Text
from sqlalchemy.orm import relationship
from Table.Base import Base

class PurchasingTrackingDayWiseTable(Base):
    __tablename__ = "purchasingTrackingDayWiseTables"
    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(String, nullable=False)  # Ensures a valid month is provided
    year = Column(Integer, nullable=False)  # Ensure the year is an integer
    day = Column(Integer, nullable=False)
    revenue = Column(Float, nullable=False, default=0.0)  # Revenue as a floating-point value
    loss = Column(Float, nullable=False, default=0.0)  # Loss as a floating-point value
    createdAt = Column(DateTime, nullable=False)
    updatedAt = Column(DateTime, nullable=False)
    storeId = Column(Integer, nullable=False)  # Foreign key to the store table