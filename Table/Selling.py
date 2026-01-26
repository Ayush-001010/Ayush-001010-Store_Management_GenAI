from sqlalchemy import Column, Integer , Float , String, Boolean, Date, DateTime, Text
from sqlalchemy.orm import relationship
from Table.Base import Base

class Selling(Base):
    __tablename__ = "sellingTables"
    id = Column(Integer, primary_key=True, autoincrement=True)
    quantitySold = Column(Integer, nullable=False)
    unitSellingPrice = Column(Float, nullable=False)
    dateOfSale = Column(Date, nullable=False)
    createdAt = Column(DateTime, nullable=False)
    updatedAt = Column(DateTime, nullable=False)
    storeId = Column(Integer, nullable=False)
    inventoryId = Column(Integer, nullable=False)