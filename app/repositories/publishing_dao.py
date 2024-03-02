from db.base_class import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class EditorialDAO(Base):
    __tablename__ = 'editoriales'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    editorial = Column(String(64), nullable=False)

    libros = relationship("LibroDAO", back_populates="editorial_ref")