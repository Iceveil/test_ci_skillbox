from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Recept(Base):
    """Таблица рецептов"""
    __tablename__ = 'recepts'
    id = Column(Integer, primary_key=True, index=True)
    recept_name = Column(String, index=True)
    count = Column(Integer, index=True)
    time_to_done = Column(Integer, index=True)
    children = relationship('ReceptDetails', back_populates='parent')


class ReceptDetails(Base):
    """Таблица с подробным описанием рецептов"""
    __tablename__ = 'recept_details'
    id = Column(Integer, primary_key=True, index=True)
    recept_name = Column(String, index=True)
    time_to_done = Column(Integer, index=True)
    ing_list = Column(String, index=True)
    description = Column(String, index=True)
    parent_id = Column(Integer, ForeignKey('recepts.id'))
    parent = relationship('Recept', back_populates='children')