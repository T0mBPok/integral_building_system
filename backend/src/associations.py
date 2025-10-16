from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import ForeignKey
from src.database import Base, int_pk
from src.function.model import Function
from src.indicator.model import Indicator


class FunctionIndicator(Base):
    __tablename__ = "function_indicators"
    
    function_id: Mapped[int_pk] = relationship(ForeignKey('functions.id', ondelete="CASCADE"))
    indicator_id: Mapped[int_pk] = relationship(ForeignKey('indicators.id', ondelete="CASCADE"))
    position: Mapped[int]
    
    function: Mapped['Function'] = relationship(back_populates='indicators')
    indicator: Mapped["Indicator"] = relationship()