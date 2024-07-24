from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from cs.sqlantic.models import StateStoreModel


class Account(StateStoreModel):
    """ User's account """
    __tablename__ = 'accounts'

    address: Mapped[str] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(nullable=False)
    signature: Mapped[str] = mapped_column(nullable=False)
    # last_name: Mapped[str | None] = mapped_column(default=None)
    state_index: Mapped[int] = mapped_column(default=0)


AccountCreate = Account.create_model
AccountUpdate = Account.update_model
AccountDelete = Account.delete_model


class Message(StateStoreModel):
    """ User's messages """
    __tablename__ = 'messages'

    message_id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    from_address: Mapped[str] = mapped_column(ForeignKey('accounts.address'), nullable=False)
    signature: Mapped[str] = mapped_column(nullable=False)
    message: Mapped[str] = mapped_column(nullable=False, default=None)
    wrote_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now())
    state_index: Mapped[int] = mapped_column(default=0)


MessageCreate = Message.create_model
MessageUpdate = Message.update_model
MessageDelete = Message.delete_model
