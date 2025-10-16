from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.database import Base, str_uniq, int_pk
from src.level.model import Level

class Module(Base):
    id: Mapped[int_pk]
    level_id: Mapped[int] = mapped_column(ForeignKey('levels.id', ondelete='CASCADE'), nullable=False)
    type: Mapped[str]
    name: Mapped[str_uniq]
    description: Mapped[str]
    indicator_id: Mapped[int] = mapped_column(ForeignKey('indicators.id'), nullable=True)
    
    indicator: Mapped['Indicator'] = relationship("Indicator")
    level: Mapped["Level"] = relationship("Level")