# Chat Threads

A backend service for managing chat threads between users and AI assistants.

## Overview

Chat Threads provides a database model and API for storing and retrieving conversations between users and AI assistants. It supports multiple products, thread management, and message tracking.

## Features

- Thread creation and management
- Message storage with parent-child relationships
- Support for different AI products (Co-Pilot, Doc Creator, etc.)
- Message summarization
- Soft deletion of threads
- Organization and user tracking

## Installation

```bash
pip install chat_threads
```

Or install from source:

```bash
git clone https://github.com/mitanshu610/chat_threads.git
cd chat_threads
pip install -e .
```

## Database Setup

This package uses SQLAlchemy models. You'll need to set up a database and run migrations using Alembic.

### Setting Up Alembic

1. Install Alembic:

```bash
pip install alembic
```

2. Initialize Alembic in your project:

```bash
mkdir -p migrations
cd migrations
alembic init alembic
```

3. Configure Alembic:

Edit `alembic.ini` to set your database URL:

```ini
# Database URL
sqlalchemy.url = postgresql://username:password@localhost/dbname
```

Edit `migrations/alembic/env.py` to import your models:

```python
from chat_threads.threads.models import Base
from chat_threads.utils.orm_utils import Base

# Add metadata to the context
target_metadata = Base.metadata
```

4. Create a migration:

```bash
alembic revision --autogenerate -m "Create initial tables"
```

5. Run the migration:

```bash
alembic upgrade head
```

## Usage

### Creating a Database Session

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Create engine
engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/dbname")

# Create session factory
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Create session
async def get_session():
    async with async_session() as session:
        yield session
```

### Creating a Thread

```python
from chat_threads.threads.services import ThreadService
from chat_threads.threads.serializers import CreateThreadRequest

async def create_thread(session):
    thread_service = ThreadService(session)
    
    thread_request = CreateThreadRequest(
        title="New Conversation",
        product="co_pilot",
        requested_by="user@example.com",
        user_id=123,
        meta={"source": "web"},
        org_id="org_123"
    )
    
    thread = await thread_service.create_thread(thread_request)
    return thread
```

### Adding Messages to a Thread

```python
from chat_threads.threads.serializers import CreateMessageRequest
from chat_threads.utils.constants import Role

async def add_message(session, thread_uuid):
    thread_service = ThreadService(session)
    
    message_request = CreateMessageRequest(
        role=Role.USER,
        content="Hello, can you help me with something?",
        product="co_pilot",
        display_text=None,  # Will default to content
        is_json=False,
        thread_id=thread_uuid,
        parent_message_id=None,
        requested_by="user@example.com",
        question_config=None,
        prompt_details=None
    )
    
    message = await thread_service.create_thread_message(
        message_request, 
        user_email="user@example.com",
        org_id="org_123"
    )
    return message
```

### Retrieving Threads

```python
async def get_user_threads(session, user_email, product):
    thread_service = ThreadService(session)
    threads = await thread_service.list_threads_by_email(
        user_email=user_email, 
        product=product
    )
    return threads
```

### Paginated Thread Retrieval

```python
async def get_paginated_threads(session, user_email, product, page=1, page_size=10, query=None, org_id=None):
    thread_service = ThreadService(session)
    result = await thread_service.get_threads_with_pagination(
        user_email=user_email,
        product=product,
        page=page,
        page_size=page_size,
        query=query,
        org_id=org_id
    )
    return result
```

### Soft Deleting a Thread

```python
async def delete_thread(session, thread_uuid):
    thread_service = ThreadService(session)
    result = await thread_service.soft_delete_thread(thread_uuid)
    return result
```

## Models

### Thread

The main conversation container:

- `id`: Primary key
- `uuid`: Unique identifier (UUID)
- `title`: Thread title
- `user_id`: Optional user ID
- `user_email`: User's email
- `is_deleted`: Soft deletion flag
- `product`: Product enum (CO_PILOT, DOC_CREATOR, etc.)
- `meta`: JSON metadata
- `last_message_id`: ID of the last message
- `org_id`: Optional organization ID

### ThreadMessage

Individual messages in a thread:

- `id`: Primary key
- `thread_uuid`: Foreign key to Thread
- `parent_message_id`: Optional parent message ID
- `content`: Message content
- `role`: Role enum (USER, SYSTEM, ASSISTANT)
- `display_text`: Optional display text
- `is_json`: Flag for JSON content
- `is_disliked`: Optional dislike flag
- `is_deleted`: Soft deletion flag
- `user_id`: Optional user ID
- `question_config`: JSONB configuration
- `prompt_details`: JSONB prompt details

### ThreadMessageSummary

Summaries of messages:

- `uuid`: Primary key (UUID)
- `thread_uuid`: Foreign key to Thread
- `thread_message_id`: Foreign key to ThreadMessage
- `summary`: Summary text

## Upgrading SQLAlchemy

Note: This project currently uses SQLAlchemy 1.4.48. If you plan to upgrade to SQLAlchemy 2.0, be aware of the migration changes documented in the SQLAlchemy 2.0 Migration Guide.

## License

[MIT License](LICENSE)

## Contributors

- Mitanshu Bhatt (mitanshubhatt@gofynd.com)
