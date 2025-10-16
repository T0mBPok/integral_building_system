from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.database import Base, int_pk
from src.project.model import Project

class Level(Base):
    id: Mapped[int_pk]
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    number: Mapped[int]
    
    project: Mapped["Project"] = relationship("Project")
    modules: Mapped[list['Module']] = relationship(back_populates='level')