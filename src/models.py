from sqlalchemy import Column, Integer, String, BOOLEAN, VARCHAR
from database import Base


class DBUsers(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR, index=True)
    passwd = Column(String)

