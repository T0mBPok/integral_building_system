from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.database import Base, str_uniq, int_pk
from src.module.model import Module


class Function(Base):
    id: Mapped[int_pk]
    module_id: Mapped[int] = mapped_column(ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str_uniq]
    expression: Mapped[int]
    
    module: Mapped["Module"] = relationship("Module")
    indicators: Mapped[list["FunctionIndicator"]] = relationship(
        back_populates="function",
        order_by="FunctionIndicator.position",
        cascade="all, delete-orphan"
    )