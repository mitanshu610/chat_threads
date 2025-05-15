from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON, Enum as SQLAEnum, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID, JSONB

import uuid

from chat_threads.utils.constants import Role, FynixProducts
from chat_threads.utils.orm_utils import Base, TimestampMixin


class Thread(Base, TimestampMixin):
    __tablename__ = 'thread'

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True)
    title = Column(String)
    user_id = Column(Integer, nullable=True)
    user_email = Column(String)
    is_deleted = Column(Boolean, default=False)
    alternate_id = Column(Integer)
    product = Column(SQLAEnum(FynixProducts), nullable=False)
    meta = Column(JSON, default={})
    last_message_id = Column(Integer, nullable=True)
    org_id = Column(String, nullable=True, index=True)

    messages = relationship("ThreadMessage", back_populates="thread")

    __table_args__ = (
        Index('ix_thread_user_email_product_is_deleted', 'user_email', 'product', 'is_deleted'),
    )


class ThreadMessage(TimestampMixin, Base):
    __tablename__ = 'thread_message'

    id = Column(Integer, primary_key=True)
    thread_uuid = Column(UUID(as_uuid=True), ForeignKey('thread.uuid'), index=True)
    parent_message_id = Column(Integer, ForeignKey('thread_message.id'), nullable=True)
    content = Column(String)
    role = Column(SQLAEnum(Role))
    display_text = Column(String)
    is_json = Column(Boolean, default=False)
    is_disliked = Column(Boolean, nullable=True)
    is_deleted = Column(Boolean, default=False)
    user_id = Column(Integer, nullable=True)
    # meta = Column(JSON, default={})
    question_config = Column(JSONB, default={})
    prompt_details = Column(JSONB, default={})

    # user = relationship("User", back_populates="thread_messages")
    thread = relationship("Thread", back_populates="messages")
    summary = relationship("ThreadMessageSummary", back_populates="message", uselist=False)


class ThreadMessageSummary(TimestampMixin, Base):
    __tablename__ = 'thread_message_summary'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_uuid = Column(UUID(as_uuid=True), ForeignKey('thread.uuid'), index=True)
    thread_message_id = Column(Integer, ForeignKey('thread_message.id'), nullable=True)
    summary = Column(String)

    # Relationship back to the summarized message
    message = relationship("ThreadMessage", back_populates="summary")