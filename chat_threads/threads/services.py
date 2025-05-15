import uuid
from typing import List, Optional

from chat_threads.threads.dao import ThreadDao, ThreadMessageDao
from chat_threads.threads.serializers import CreateThreadRequest, CreateMessageRequest

from chat_threads.threads.models import Thread

class ThreadService:

    def __init__(self, connection_handler):
        self.connection_handler = connection_handler
        self.thread_dao = ThreadDao(session=connection_handler.session)
        self.thread_message_dao = ThreadMessageDao(session=connection_handler.session)

    async def update_thread(self, thread_id: uuid.UUID, update_thread_request: CreateThreadRequest):
        update_values = {}
        for attr, value in vars(update_thread_request).items():
            if value is not None:
                update_values[attr] = value
        return await self.thread_dao.update_thread(thread_uuid=thread_id,
                                                   update_values_dict=update_values)

    async def create_thread(self, create_thread_request: CreateThreadRequest):
        thread = self.thread_dao.add_object({
            "title": create_thread_request.title or "New Chat",
            "uuid": uuid.uuid4(),
            "user_email": create_thread_request.requested_by,
            "user_id": create_thread_request.user_id or None,
            "alternate_id": create_thread_request.alternate_id,
            "product": create_thread_request.product,
            "meta": create_thread_request.meta or {},
            "org_id": create_thread_request.org_id or None
        })
        return thread

    async def create_thread_message(self, create_message_request: CreateMessageRequest, user_email: str, org_id: Optional[str] = None):
        if create_message_request.thread_id is None:
            thread = await self.create_thread(create_thread_request=CreateThreadRequest(
                requested_by=user_email,
                title=create_message_request.content[:23] + '...',
                product=create_message_request.product,
                meta={},
                alternate_id=None,
                user_id=None,
                org_id=org_id
            ))
            create_message_request.thread_id = thread.uuid
        thread_message = self.thread_message_dao.add_object({
            "content": create_message_request.content,
            "role": create_message_request.role,
            "display_text": create_message_request.display_text or create_message_request.content,
            "thread_uuid": create_message_request.thread_id,
            "parent_message_id": create_message_request.parent_message_id or None,
            "is_json": create_message_request.is_json,
            "question_config": create_message_request.question_config or None,
            "prompt_details": create_message_request.prompt_details or {}
        })
        return thread_message

    async def list_threads_by_email(self, user_email: str, product: str):
        return await self.thread_dao.get_threads_by_user_email(user_email=user_email, product=product)

    async def list_threads_by_alternate_id(self, alternate_id: int, product: str):
        return await self.thread_dao.get_threads_by_alternate_id(alternate_id=alternate_id, product=product)

    async def update_thread_message(self, thread_id: uuid.UUID, update_message_request: CreateMessageRequest):
        thread_message = await self.thread_message_dao.get_thread_messages_by_id(thread_id)

        if thread_message:
            thread_message.content = update_message_request.content
            thread_message.display_text = update_message_request.display_text
            return thread_message
        else:
            # Handle the case where the thread message with the given UUID is not found
            return None

    async def soft_delete_thread(self, thread_uuid):
        return await self.thread_dao.soft_delete_thread_by_uuid(thread_uuid)

    async def get_thread_messages(self, thread_id: uuid.UUID):
        return await self.thread_dao.get_thread_messages(thread_id)

    async def search_thread_by_content(self, query: str, email: str, product: str):
        return await self.thread_dao.search_in_thread_message(query, email, product)

    async def get_threads_with_pagination(self, user_email: str, product: str, page: int, page_size: int, query: str=None, org_id: Optional[str] = None) -> List[Thread]:

        return await self.thread_dao.get_threads_with_pagination(user_email, product, page, page_size, query, org_id)
