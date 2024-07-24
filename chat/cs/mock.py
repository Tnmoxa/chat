import asyncio

import cs.abc
import typing as t

from cs.states.layers import SettlementCtx
from sqlalchemy.ext.asyncio import AsyncEngine

import cs.states.layers
from cs.sqlantic.models import StateChange, Serialized



class Storage(cs.sqlantic.Storage):
    async def get_last_block(self) -> int:
        return 0


class Settlement(cs.states.layers.Settlement[StateChange]):

    def __init__(self, storage: Storage):
        self.__storage = storage

    @property
    def storage(self) -> Storage:
        return self.__storage


class Execution(cs.states.layers.Execution[StateChange]):

    def __init__(self, storage: Storage):
        self.__storage = storage

    @property
    def storage(self) -> Storage:
        return self.__storage



class Transport(cs.abc.Transport[StateChange, Serialized]):
    """ Петлевым транспортом для тестовых целей """

    def __init__(self):
        super().__init__()
        self._accum = []
        self._block_height = 0

    async def connect(self, *args: t.Any, **kwargs: t.Any) -> None:
        await super().connect(*args, **kwargs)

    async def _send_blob(self, data: bytes, **kwargs: t.Any) -> tuple[int, int]:
        self._block_height += 1
        self._package_index = 0
        self._accum.append((self._block_height, [(self._package_index, data)]))
        return self._block_height, 0

    async def _recv_blobs(self, last_height: int, **kwargs) -> tuple[int, t.Iterable[tuple[int, bytes]]] | None:
        while self.connected:
            if self._accum:
                return self._accum.pop(0)
            await asyncio.sleep(0.1)

    def _make_serialized(self, data: bytes) -> Serialized:
        return Serialized(data)


class Service(cs.abc.Service[StateChange, Serialized]):
    execution: Execution = None
    settlement: Settlement = None

    def __init__(self, engine: AsyncEngine):
        super().__init__()
        storage = Storage(engine)
        self.execution = Execution(storage)
        self.settlement = Settlement(storage)

    async def start(self, *args, **kwargs):
        return await super().start(Transport, *args, **kwargs)

