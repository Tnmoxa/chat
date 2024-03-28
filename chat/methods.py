from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, delete, and_
from sqlalchemy import create_engine

from chat.models import AccountPost, AccountDelete, MessagePost, MessageDelete
from chat.tables import accounts, Account, messages, Message
from chat.envars import DATABASE_URL

database = create_engine(DATABASE_URL)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Session = sessionmaker(autoflush=False, bind=database)


@app.post("/account/create")
async def create_account(account: AccountPost):
    with Session(autoflush=False, bind=database) as session:
        acc = Account(account.address, account.display_name, account.signature)
        acc_check = session.execute(select(accounts).where(Account.address == acc.address)).scalar()
        if acc_check:
            return f'{account.display_name} already used'
        session.add(acc)
        session.commit()
    return f'{account} create'


@app.delete("/account/delete")
async def delete_account(account: AccountDelete):
    with Session(autoflush=False, bind=database) as session:
        acc = session.execute(select(accounts).where(Account.address == account.address)).scalar()
        if not acc:
            return f'{account.address} not found'
        session.execute(delete(accounts).where(Account.address == account.address))
        session.commit()
    return f'{account.address} deleted'


@app.post("/message/create")
async def create_message(message: MessagePost):
    with Session(autoflush=False, bind=database) as session:
        mess = Message(**message.model_dump())
        mess_check = session.execute(select(messages).where(
            and_(Message.message_id == mess.message_id,
                 Message.from_address == mess.from_address))).scalar()
        if mess_check:
            return f'{message.message_id, message.from_address} already created'
        session.add(mess)
        session.commit()
    return f'{message.message} create'


@app.delete("/message/delete")
async def delete_message(message: MessageDelete):
    with Session(autoflush=False, bind=database) as session:
        mess_check = session.execute(select(messages).where(
            and_(Message.message_id == message.message_id, Message.from_address == message.from_address))).scalar()
        if not mess_check:
            return f'{message.message_id, message.from_address} not found'
        session.execute(delete(messages).where(
            and_(Message.message_id == message.message_id.bytes, Message.from_address == message.from_address)))
        session.commit()
    return f'{message.message_id} deleted'
