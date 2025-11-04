from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.database import Base, int_pk
from src.project.model import Project
from src.module.model import Module
from src.function.model import Function

class Level(Base):
    id: Mapped[int_pk]
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    number: Mapped[int]
    function_id: Mapped[int|None]
    
    project: Mapped["Project"] = relationship("Project")
    modules: Mapped[list['Module']] = relationship("Module", back_populates='level')
    function: Mapped["Function"] = relationship('Function', back_populates='level')