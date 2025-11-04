from sqlalchemy.orm import Mapped
from src.database import Base, str_uniq, int_pk

class Indicator(Base):
    id: Mapped[int_pk]
    name: Mapped[str_uniq]
    value: Mapped[int]