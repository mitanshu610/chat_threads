from chat_threads.utils.dao import BaseDao
from sqlalchemy import select, and_, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID
from chat_threads.utils.exceptions import (
    ThreadUpdateError, ThreadDeleteError
)
from chat_threads.threads.models import Thread, ThreadMessage, ThreadMessageSummary
from chat_threads.threads.serializers import ThreadSchema, ThreadMessageSchema


class ThreadDao(BaseDao):

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, db_model=Thread)

    async def get_thread_by_id(self, thread_id: UUID):
        query = select(Thread).where(Thread.uuid == thread_id)
        result = await self._execute_query(query)
        thread = result.scalars().first()
        return ThreadSchema.model_validate(thread)

    async def update_thread(self, thread_uuid: UUID, update_values_dict: dict):
        update_query = update(Thread).where(Thread.uuid == thread_uuid,
                                            Thread.is_deleted==False).values(**update_values_dict)
        result = await self._execute_query(update_query)
        if result.rowcount == 0:
            raise ThreadUpdateError("Thread to update not found")
        return result

    async def get_thread_messages(self, thread_id: UUID, filters: dict = None):
        query = select(ThreadMessage, Thread).join(ThreadMessage).where(
            Thread.uuid == thread_id).order_by(ThreadMessage.id)
        if filters and filters['roles']:
            query = query.where(ThreadMessage.role.in_(filters['roles']))
        result = await self._execute_query(query)
        messages = result.scalars().all()
        return [ThreadMessageSchema.model_validate(message) for message in messages]

    async def get_threads_by_user_email(self, user_email: str, product: str) -> List[ThreadSchema]:
        query = select(Thread).where(and_(Thread.user_email == user_email,
                                          Thread.product == product,
                                          Thread.is_deleted == False)).order_by(Thread.created_at.desc())
        query_result = await self._execute_query(query)
        results = query_result.scalars().all()
        return [ThreadSchema.model_validate(result) for result in results]

    async def get_threads_by_alternate_id(self, alternate_id: int, product: str):
        query = select(Thread).where(and_(Thread.alternate_id == alternate_id,
                                          Thread.product == product))
        result = await self._execute_query(query)
        results = result.scalars().all()
        return [ThreadSchema.model_validate(result) for result in results]

    async def get_thread_messages_by_alternate_id(self, alternate_id: int, product: str, user_id: int):
        query = select(ThreadMessage, Thread).join(ThreadMessage).where(and_(Thread.alternate_id == alternate_id,
                                                                             Thread.product == product)).order_by(
            ThreadMessage.id)
        result = await self._execute_query(query)
        messages = result.scalars().all()
        return [ThreadMessageSchema.model_validate(message) for message in messages]

    async def soft_delete_thread_by_uuid(self, thread_uuid):
        query = (update(Thread).where(Thread.uuid == thread_uuid,
                                      Thread.is_deleted==False).
                 values(is_deleted=True))
        result = await self._execute_query(query)
        if result.rowcount == 0:
            raise ThreadDeleteError("Thread to delete not found")
        return ThreadSchema.model_validate(result)

    async def search_in_thread_message(self, query: str, email: str, product: str):
        search_query = select(Thread).distinct(Thread.id).join(ThreadMessage,
                                                               Thread.uuid == ThreadMessage.thread_uuid).where(
            Thread.user_email == email,
            Thread.product == product,
            Thread.is_deleted == False,
            ThreadMessage.content.ilike(f'%{query}%')
        )

        result = await self._execute_query(search_query)
        threads = result.scalars().all()
        return [ThreadSchema.model_validate(thread) for thread in threads]

    @staticmethod
    async def _get_threads_query(user_email: str, product: str, search_query: str = None, org_id: Optional[str] = None):
        base_query = select(Thread).where(
            and_(
                Thread.user_email == user_email,
                Thread.product == product,
                Thread.is_deleted == False,
            )
        )

        if org_id:
            base_query = base_query.where(Thread.org_id == org_id)
        else:
            base_query = base_query.where(Thread.org_id.is_(None))

        if search_query:
            base_query = base_query.join(ThreadMessage, Thread.uuid == ThreadMessage.thread_uuid).where(
                ThreadMessage.content.ilike(f'%{search_query}%')
            ).distinct(Thread.id)

        base_query = base_query.order_by(Thread.created_at.desc() if not search_query else Thread.id.desc())
        return base_query

    async def get_threads_with_pagination(self, user_email: str, product: str, page: int,
                                          page_size: int, query: str = None, org_id: Optional[str] = None):
        search_query = await self._get_threads_query(user_email, product , search_query=query, org_id=org_id)

        count_query = select(func.count()).select_from(search_query.subquery())
        total_count_result = await self._execute_query(count_query)
        total_count = total_count_result.scalar()

        if page_size > 0:
            search_query = search_query.offset((page - 1) * page_size).limit(page_size)

        result = await self._execute_query(search_query)
        threads = result.scalars().all()

        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1
        has_next = page < total_pages
        has_previous = page > 1

        return {
            "threads": [ThreadSchema.model_validate(t).model_dump() for t in threads],
            "pagination": {
                "total_count": total_count,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
                "has_next": has_next,
                "has_previous": has_previous,
            },
        }


class ThreadMessageDao(BaseDao):

    def __init__(self, session: AsyncSession):
        super().__init__(session, ThreadMessage)

    async def get_thread_messages_by_uuid(self, thread_id: UUID) -> List[ThreadMessage]:
        query = select(ThreadMessage).join(Thread).filter(Thread.uuid == thread_id).order_by(ThreadMessage.created_at)
        result = await self._execute_query(query)
        messages = result.scalars().all()
        return messages


class ThreadMessageSummaryDao(BaseDao):
    """DAO for the ThreadMessageSummary model."""
    def __init__(self, session: AsyncSession):
        super().__init__(session, ThreadMessageSummary)

    async def get_summaries_for_message_ids(self, message_ids: List[int]) -> List[ThreadMessageSummary]:
        """Fetch all summaries for a given list of thread_message_ids."""
        stmt = select(ThreadMessageSummary).where(ThreadMessageSummary.thread_message_id.in_(message_ids))
        result = await self._execute_query(stmt)
        return result.scalars().all()

    async def create_summary(
        self,
        thread_uuid: UUID,
        thread_message_id: int,
        summary_text: str
    ) -> ThreadMessageSummary:
        """Create a new summary entry."""
        new_summary = self.add_object({
            "thread_uuid": thread_uuid,
            "thread_message_id": thread_message_id,
            "summary": summary_text
        })
        return new_summary

    async def update_message_summary(self, summary_uuid: UUID, update_values_dict: dict):
        update_query = update(ThreadMessageSummary).where(ThreadMessageSummary.uuid == summary_uuid).values(**update_values_dict)
        return await self._execute_query(update_query)

    async def get_summaries(self, thread_message_ids: List[UUID]):
        """
       From a given list of thread message ids, find the relevant summaries.
       """
        query = select(ThreadMessageSummary).where(ThreadMessageSummary.thread_message_id.in_(thread_message_ids))
        result = await self.session.execute(query)
        return result.scalars().all()

