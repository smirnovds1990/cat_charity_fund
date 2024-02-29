from datetime import datetime

from sqlalchemy import Column, Boolean, DateTime, Integer

from app.core.db import Base


class CoreClass(Base):
    """Абстрактный класс для общих полей."""
    __abstract__ = True

    full_amount = Column(Integer, default=0)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.utcnow)
    close_date = Column(DateTime, nullable=True)
