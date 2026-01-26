from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text
from sqlalchemy.orm import relationship
from Table.Base import Base  # Shared Base class


class Store(Base):
    __tablename__ = "storeTables"  # Exact table name matches MySQL

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # Name of the store
    description = Column(Text, nullable=True)  # Optional description
    city = Column(String(255), nullable=False)  # City of the store
    state = Column(String(255), nullable=False)  # State of the store
    street = Column(String(255), nullable=True)  # Optional street address
    address = Column(Text, nullable=True)  # Optional address
    postalCode = Column(String(10), nullable=True)  # ZIP or postal code
    category = Column(String(255), nullable=False)  # Store category
    is24hrOpen = Column(Boolean, default=False)  # Whether open 24/7
    openingTime = Column(Date, nullable=True)  # Store opening time
    closingTime = Column(Date, nullable=True)  # Store closing time
    firstSaleDate = Column(Date, nullable=True)  # Date of first sale
    createdAt = Column(DateTime, nullable=False)  # Creation date
    updatedAt = Column(DateTime, nullable=False)  # Last updated timestamp
    organizationId = Column(Integer, nullable=False)  # Associated organization ID

    # Relationship with PurchasingTrackingTable
    purchasing_tracking = relationship("PurchasingTrackingTable", back_populates="store")