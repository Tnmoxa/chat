from typing import Annotated

from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete, and_
from sqlalchemy import create_engine

from chatAPI.chat.models2 import AccountCreate, AccountUpdate, AccountDelete, MessageCreate, MessageDelete, \
    MessageUpdate, Account, Message
from chatAPI.chat.envars import DATABASE_URL

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


def get_keys(request: Request):
    return dict(**request.query_params)



@app.post("/account/create", status_code=200)
async def create_account(account: AccountCreate, response: Response):
    with Session(autoflush=False, bind=database) as session:
        acc_check = session.execute(select(Account).where(Account.address == account.address)).scalar()
        if acc_check:
            response.status_code = 404
            response.body = 'Account already exists'
        else:
            session.add(account.create_state())
            session.commit()


@app.get("/account/read", status_code=200)
async def read_message(account: Annotated[dict, Depends(get_keys)], response: Response):
    with Session(autoflush=False, bind=database) as session:
        acc_check = session.execute(select(Account).where(Account.address == account['address'])).scalar()
        if not acc_check:
            response.status_code = 404
            response.body = 'Account not found'
        else:
            return JSONResponse(
                content=[{'address': acc_check.address, 'display_name': acc_check.display_name,
                          'signature': acc_check.signature}])


@app.put('/account/update', status_code=200)
async def put_account(account: AccountUpdate, response: Response):
    with Session(autoflush=False, bind=database) as session:
        acc_check = session.execute(select(Account).where(Account.address == account.address)).scalar()
        if not acc_check:
            response.status_code = 404
            response.body = 'Account not found'
        else:
            account.update_state(acc_check)
            session.add(acc_check)
            session.commit()


@app.delete("/account/delete", status_code=200)
async def delete_account(keys: Annotated[dict, Depends(get_keys)], response: Response):
    account = AccountDelete(**keys)
    with Session(autoflush=False, bind=database) as session:
        acc_check = session.execute(select(Account).where(Account.address == account.address)).scalar()
        if not acc_check:
            response.status_code = 404
            response.body = 'Account not found'
        else:
            session.delete(acc_check)
            session.commit()


@app.post("/message/create", status_code=200)
async def create_message(message: MessageCreate, response: Response):
    with Session(autoflush=False, bind=database) as session:
        mess_check = session.execute(select(Message).where(
            and_(Message.signature == message.signature, Message.from_address == message.from_address))).scalar()
        if mess_check:
            response.status_code = 404
            response.body = 'Message already exists'
        else:
            session.add(message.create_state())
            session.commit()


@app.get("/message/read", status_code=200)
async def read_message(message: Annotated[dict, Depends(get_keys)], response: Response):
    with Session(autoflush=False, bind=database) as session:
        mess_check = session.execute(select(Message).where(Message.from_address == message['from_address'])).scalar()
        if not mess_check:
            response.status_code = 404
            response.body = 'Message not found'
        else:
            return JSONResponse(
                content=[{'from_address': mess_check.from_address, 'message': mess_check.message, 'signature': mess_check.signature,
                          'message_id': mess_check.message_id, }])


@app.put('/message/update', status_code=200)
async def put_message(message: MessageUpdate, response: Response):
    with Session(autoflush=False, bind=database) as session:
        mess_check = session.execute(select(Message).where(
            and_(Message.message_id == message.message_id, Message.from_address == message.from_address))).scalar()
        if not mess_check:
            response.status_code = 404
            response.body = 'Message not found'
        else:
            message.update_state(mess_check)
            session.add(mess_check)
            session.commit()


@app.delete("/message/delete", status_code=200)
async def delete_message(keys: Annotated[dict, Depends(get_keys)], response: Response):
    message = MessageDelete(message_id=keys['message_id'])
    with Session(autoflush=False, bind=database) as session:
        mess_check = session.execute(select(Message).where(
            Message.message_id == message.message_id)).scalar()
        if not mess_check:
            response.status_code = 404
            response.body = 'Message not found'
        else:
            session.delete(mess_check)
            session.commit()
