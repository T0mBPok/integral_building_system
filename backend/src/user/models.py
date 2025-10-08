from src.database import int_pk, Base
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    id: Mapped[int_pk]
    username: Mapped[str]
    hashed_password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)