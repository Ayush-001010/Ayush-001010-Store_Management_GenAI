from sqlalchemy import Column, Integer , Float , String, Boolean, Date, DateTime, Text
from sqlalchemy.orm import relationship
from Table.Base import Base

class UsersTable(Base):
    __tablename__ = "UsersTables"
    id = Column(Integer, primary_key=True, autoincrement=True)
    userName = Column(String, nullable=False, unique=True)
    userPassword = Column(String, nullable=False)
    userEmail = Column(String, nullable=False, unique=True)
    userRole = Column(String, default="user")
    userProfileImage = Column(String)
    isActive = Column(Boolean, default=True)
    createdAt = Column(DateTime, nullable=False)
    lastLogInTime = Column(DateTime)
    userAbout = Column(Text)
    userGender = Column(String)
    organizationId = Column(Integer)
    location = Column(String)