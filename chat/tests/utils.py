from sqlalchemy.ext.asyncio import create_async_engine


def create_engine():
    return create_async_engine(f"sqlite+aiosqlite:///chat.sqlite")