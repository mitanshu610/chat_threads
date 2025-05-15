from datetime import datetime
from pytz import timezone
from sqlalchemy import DateTime, Column
from sqlalchemy.orm import declarative_mixin, Mapped, declarative_base

from chat_threads.utils.constants import UTC_TIME_ZONE


def get_current_time(time_zone: str = UTC_TIME_ZONE):
    return datetime.now(timezone(time_zone))

@declarative_mixin
class TimestampMixin:
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=get_current_time)
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=get_current_time,
                                          onupdate=get_current_time)


Base = declarative_base()

