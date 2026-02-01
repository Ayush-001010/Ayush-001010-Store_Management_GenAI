from sqlalchemy import Column, Integer , Float , String, Boolean, Date, DateTime, Text
from sqlalchemy.orm import relationship
from Table.Base import Base

class Inventory(Base) :
    __tablename__ = "inventorytables"
    id = Column(Integer , primary_key=True, autoincrement=True)
    productName = Column(String(255) , nullable=False)
    category = Column(String(100) , nullable=True)
    type = Column(String(100) , nullable=True)
    subCategory = Column(String(100) , nullable=True)
    company = Column(String(255) , nullable=True)
    description = Column(Text ,  nullable=True)
    costPrice = Column(Float , nullable=False)
    sellingPrice = Column(Float , nullable=False)
    profitAmount = Column(Float , nullable=False)
    isInStock = Column(Integer , default=True , nullable=False)
    lowAlertLimit = Column(Integer , nullable=True)
    manufactureDate = Column(Date , nullable=True)
    expiryDate = Column(Date , nullable=True)
    placementDetails = Column(Text , nullable=True)
    isDiscounted = Column(Boolean , default=False , nullable=False)
    discountPercentage = Column(Float ,  nullable=True)
    createdAt = Column(Date,nullable=False )
    updatedAt = Column(Date , nullable=False)
    storeId = Column(Integer , nullable=False)  # Foreign key to the store table