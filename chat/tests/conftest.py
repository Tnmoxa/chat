import pytest_asyncio

from cs.sqlantic.models import StateStoreModel

from chatAPI.chat.tests.utils import create_engine


@pytest_asyncio.fixture()
async def db():
    engine = create_engine()
    async with engine.connect() as async_conn:
        await async_conn.run_sync(StateStoreModel.metadata.drop_all)
        await async_conn.run_sync(StateStoreModel.metadata.create_all)
    return engine
