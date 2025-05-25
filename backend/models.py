from sqlalchemy import Column, Integer, String
from database import Base

class Scenario(Base):
    __tablename__ = "Scenario"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    content = Column(String, index=True)


class Image(Base):
    __tablename__ = "Image"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    prompt = Column(String)
    model = Column(String)
    width = Column(Integer)
    height = Column(Integer)