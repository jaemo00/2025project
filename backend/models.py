from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime
from database import Base

class Chr_Scenario(Base):
    __tablename__="chr_scanario"
    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(String, index=True, nullable=False)
    project_id = Column(Integer)
    user_topic_input=Column(String)
    time=Column(Integer)
    topic=Column(String,nullable=True)
    description = Column(String,nullable=True)
    character = Column(String)
    character_description= Column(String)
    character_prompt=Column(String)
    model=Column(String)
    background = Column(String,nullable=True)
    contents = Column(Text,nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

class Scenario(Base):
    __tablename__ = "scenarios"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    project_id = Column(Integer)
    user_topic_input=Column(String)
    time=Column(Integer)
    topic=Column(String,nullable=True)
    description = Column(String,nullable=True)
    background = Column(String,nullable=True)
    contents = Column(Text,nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    user_id = Column(String)
    image_prompt = Column(MutableList.as_mutable(JSON), default=list)
    model = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    video_prompt = Column(MutableList.as_mutable(JSON), default=list)
    video_path = Column(String)

from sqlalchemy.orm import Session
from typing import Optional

def get_scenario_value(
    db: Session, user_id: str, project_id: int, column: str
) -> Optional[str]:
    # getattr을 이용해 동적으로 컬럼 객체 가져오기
    col_attr = getattr(Scenario, column, None)
    if col_attr is None:
        raise ValueError(f"Scenario에는 '{column}' 컬럼이 없습니다.")

    result = (
        db.query(col_attr)
          .filter(
              Scenario.user_id == user_id,
              Scenario.project_id == project_id
          )
          .first()  #튜플 반환
    )
    return result[0] if result else None

def get_chr_scenario_value(
    db: Session, user_id: str, project_id: int, column: str
) -> Optional[str]:
    # getattr을 이용해 동적으로 컬럼 객체 가져오기
    col_attr = getattr(Chr_Scenario, column, None)
    if col_attr is None:
        raise ValueError(f"Scenario에는 '{column}' 컬럼이 없습니다.")

    result = (
        db.query(col_attr)
          .filter(
              Chr_Scenario.user_id == user_id,
              Chr_Scenario.project_id == project_id
          )
          .first()  #튜플 반환
    )
    return result[0] if result else None

def get_chr_image_value(
    db: Session, user_id: str, project_id: int, column: str
) -> Optional[str]:
    # getattr을 이용해 동적으로 컬럼 객체 가져오기
    col_attr = getattr(Chr_Image, column, None)
    if col_attr is None:
        raise ValueError(f"Scenario에는 '{column}' 컬럼이 없습니다.")

    result = (
        db.query(col_attr)
          .filter(
              Chr_Image.user_id == user_id,
              Chr_Image.project_id == project_id
          )
          .first()  #튜플 반환
    )
    return result[0] if result else None

