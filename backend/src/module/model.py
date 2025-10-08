from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.database import Base, str_uniq, int_pk
from src.project.model import Project

class Module(Base):
    id: int_pk
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str_uniq]
    description: Mapped[str]
    
    
    project: Mapped["Project"] = relationship("Project")