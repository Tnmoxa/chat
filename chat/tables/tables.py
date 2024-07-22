from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from sqlalchemy import Table, Column, func, PrimaryKeyConstraint
from sqlalchemy.dialects.sqlite import DATETIME, TEXT
from sqlalchemy.orm import registry

from chat.new_types import Bytes64, BytesHex, UUIDv4

mapper_registry = registry()
mapped = mapper_registry.mapped
metadata = mapper_registry.metadata


@dataclass
class Account:
    address: BytesHex
    display_name: str
    signature: Bytes64


@dataclass
class Message:
    message_id: UUIDv4
    from_address: BytesHex
    message: str
    signature: Bytes64
    wrote_at: datetime = datetime.now(timezone.utc).replace(tzinfo=None)


accounts = Table(
    'accounts',
    metadata,
    Column('address', TEXT, primary_key=True),
    Column('display_name', TEXT),
    Column('signature', TEXT),
)

messages = Table(
    'messages',
    metadata,
    Column('message_id', TEXT),
    Column('from_address', TEXT),
    Column('message', TEXT),
    Column('wrote_at', DATETIME, default=func.now()),
    Column('signature', TEXT),
    PrimaryKeyConstraint('message_id', 'from_address', name='messages'),
)

mapper_registry.map_imperatively(Account, accounts, )

mapper_registry.map_imperatively(Message, messages)
