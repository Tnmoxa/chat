from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select

from chatAPI.chat.database.models2 import AccountCreate, AccountUpdate, AccountDelete, MessageCreate, MessageDelete, \
    MessageUpdate, Account, Message
from cs.states.errors import StateAlreadyExists, StateNotFound
from chatAPI.chat.cs.mock import Service as CeleStorm
from chatAPI.chat.utils import create_engine

cs = CeleStorm(create_engine())


@asynccontextmanager
async def lifespan(_: FastAPI):
    await cs.start()
    yield
    await cs.stop()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_cele_storm():
    try:
        if not cs.active:
            raise RuntimeError('CeleStorm is not active')
        yield cs
    finally:
        pass


def get_keys(request: Request):
    return dict(**request.query_params)


@app.post("/account/create", status_code=200)
async def post_account(account: AccountCreate, response: Response, cs: CeleStorm = Depends(get_cele_storm)):
    try:
        async with cs.submitter() as submit:
            await submit(account)
    except StateAlreadyExists:
        response.status_code = 404
        response.body = 'Account already exists'


@app.get("/account/read", status_code=200)
async def get_message(account: Annotated[dict, Depends(get_keys)], response: Response):
    async with create_engine().connect() as session:
        acc_check = (await session.execute(select(Account).where(Account.address == account['address']))).fetchone()
        if not acc_check:
            response.status_code = 404
            response.body = 'Account not found'
        else:
            return JSONResponse(
                content=[{'address': acc_check.address, 'display_name': acc_check.display_name,
                          'signature': acc_check.signature}])


@app.put('/account/update', status_code=200)
async def put_account(account: AccountUpdate, response: Response, cs: CeleStorm = Depends(get_cele_storm)):
    try:
        async with create_engine().connect() as session:
            acc_check = (
                await session.execute(select(Account).where(Account.address == account.address))).fetchone()
        account = AccountUpdate.from_store(acc_check, display_name=account.display_name, signature=account.signature)
        async with cs.submitter() as submit:
            await submit(account)
    except (StateNotFound, AttributeError):
        response.status_code = 404
        response.body = 'Account not found'


@app.delete("/account/delete", status_code=200)
async def delete_account(keys: Annotated[dict, Depends(get_keys)], response: Response,
                         cs: CeleStorm = Depends(get_cele_storm)):
    try:
        async with create_engine().connect() as session:
            account_delete = AccountDelete.from_store(
                (await session.execute(select(Account).where(Account.address == keys['address']))).fetchone())
        async with cs.submitter() as submit:
            await submit(account_delete)
    except (StateNotFound, AttributeError):
        response.status_code = 404
        response.body = 'Account not found'


@app.post("/message/create", status_code=200)
async def post_message(message: MessageCreate, response: Response, cs: CeleStorm = Depends(get_cele_storm)):
    try:
        async with cs.submitter() as submit:
            await submit(message)
    except StateAlreadyExists:
        response.status_code = 404
        response.body = 'Message already exists'


@app.get("/message/read", status_code=200)
async def get_message(message: Annotated[dict, Depends(get_keys)], response: Response):
    async with create_engine().connect() as session:
        mess_check = (
            await session.execute(select(Message).where(Message.from_address == message['from_address']))).fetchone()
        if not mess_check:
            response.status_code = 404
            response.body = 'Message not found'
        else:
            return JSONResponse(
                content=[{'from_address': mess_check.from_address, 'message': mess_check.message,
                          'signature': mess_check.signature,
                          'message_id': mess_check.message_id, }])


@app.put('/message/update', status_code=200)
async def put_message(message: MessageUpdate, response: Response, cs: CeleStorm = Depends(get_cele_storm)):
    try:
        async with create_engine().connect() as session:
            mess_check = (
                await session.execute(select(Message).where(Message.message_id == message.message_id))).fetchone()
        message = MessageUpdate.from_store(mess_check, message=message.message, signature=message.signature)
        async with cs.submitter() as submit:
            await submit(message)
    except (StateNotFound, AttributeError):
        response.status_code = 404
        response.body = 'Message not found'


@app.delete("/message/delete", status_code=200)
async def delete_message(keys: Annotated[dict, Depends(get_keys)], response: Response,
                         cs: CeleStorm = Depends(get_cele_storm)):
    try:
        async with create_engine().connect() as session:
            message = MessageDelete.from_store(
                (await session.execute(select(Message).where(Message.message_id == keys['message_id']))).fetchone())
        async with cs.submitter() as submit:
            await submit(message)
    except (StateNotFound, AttributeError):
        response.status_code = 404
        response.body = 'Message not found'
