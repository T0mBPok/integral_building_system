from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.database import Base, str_uniq, int_pk

class Module(Base):
    id: Mapped[int_pk]
    name: Mapped[str_uniq]
    value: Mapped[int]
    level_id: Mapped[int] = mapped_column(ForeignKey('levels.id', ondelete="CASCADE"))
    
    level: Mapped['Level'] = relationship('Level', back_populates='modules')