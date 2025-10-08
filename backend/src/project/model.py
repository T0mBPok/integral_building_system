from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.database import Base, str_uniq, int_pk
from src.user.model import User

class Project(Base):
    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str_uniq]
    description: Mapped[str]
    
    user: Mapped["User"] = relationship("User")