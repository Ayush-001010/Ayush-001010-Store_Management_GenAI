from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from Table.Base import Base


class PurchasingTrackingTable(Base):
    __tablename__ = "purchasingTrackingTables"  # Match table name exactly (lowercase p)

    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(String(50), nullable=False)  # Month is stored as text (max length 50)
    year = Column(Integer, nullable=False)  # Year (integer)
    revenue = Column(Float, nullable=False, default=0.0)  # Revenue as a float
    loss = Column(Float, nullable=False, default=0.0)  # Loss as a float
    storeId = Column(Integer, ForeignKey("storeTables.id"), nullable=False)  # Foreign key to storeTables
    createdAt = Column(DateTime, nullable=False)
    updatedAt = Column(DateTime, nullable=False)

    # Relationship to Store
    store = relationship("Store", back_populates="purchasing_tracking")