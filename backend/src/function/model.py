from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import ForeignKey
from src.database import Base, str_uniq, int_pk


class Function(Base):
    id: Mapped[int_pk]
    name: Mapped[str_uniq]
    expression: Mapped[str]
    level_id: Mapped[int] = ForeignKey('levels.id', ondelete="CASCADE")
    
    level: Mapped['Level'] = relationship("Level")