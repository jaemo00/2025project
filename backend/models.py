from sqlalchemy import Column, Integer, String
from database import Base

class TextItem(Base):
    __tablename__ = "text_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    content = Column(String, index=True)