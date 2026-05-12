from sqlalchemy import Column, Integer, String

from database import Base


class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    cooking_time = Column(Integer, nullable=False)  # минуты
    ingredients = Column(String, nullable=False)  # перечисление через запятую
    procedure = Column(String, nullable=False)  # текстовое описание
    views = Column(Integer, default=0)
