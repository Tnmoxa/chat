import os.path

from sqlalchemy.ext.asyncio import create_async_engine


def create_engine():
    path = os.path.abspath(os.path.dirname(__file__))
    return create_async_engine(os.environ.get('DATABASE_URL', f'sqlite+aiosqlite:///{path}/chat.sqlite'))
