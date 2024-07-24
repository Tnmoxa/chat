import json
import os
import pytest
import asyncio

from fastapi.testclient import TestClient
from nacl.encoding import Base64Encoder, HexEncoder
from nacl.signing import SigningKey
from sqlalchemy import select

from chatAPI.chat.cs import app as app_cs
from chatAPI.chat.methods import app as app_default
from chatAPI.chat.database.models2 import Account

apps = {'app_cs': app_cs, 'app_default': app_default}

client = TestClient(apps[os.environ['apps']])


@pytest.fixture
def create_account_data():
    secret_account_key = SigningKey.generate()
    display_name = 'User'
    account_signature = secret_account_key.sign(display_name.encode('ASCII'), encoder=Base64Encoder).decode('ASCII')
    address = secret_account_key.verify_key.encode(encoder=HexEncoder).decode('ASCII')
    return secret_account_key, display_name, account_signature, address


@pytest.fixture
def create_message_data(create_account_data):
    secret_account_key, display_name, account_signature, address = create_account_data
    message = 'Hello, world!'
    message_signature = secret_account_key.sign(message.encode('ASCII'), encoder=Base64Encoder).decode('ASCII')
    from_address = address
    return (secret_account_key, display_name, account_signature, address), (from_address, message, message_signature)


@pytest.mark.asyncio
async def test_create_read_update_delete_account_message(create_message_data, db) -> None:
    (secret_account_key, display_name, account_signature, address) = create_message_data[0]
    (from_address, message, message_signature) = create_message_data[1]

    with TestClient(apps[os.environ['apps']]) as client:
        data = {'address': "0x" + address, 'display_name': display_name, 'signature': account_signature}
        response = client.post("/account/create", json=data)
        assert response.status_code == 200
        await asyncio.sleep(0.2)
        response = client.post("/account/create", json=data)
        assert response.status_code == 404

        display_name = display_name[::-1]
        account_signature = secret_account_key.sign(display_name.encode('ASCII'), encoder=Base64Encoder).decode('ASCII')
        data = {'address': "0x" + address, 'display_name': display_name, 'signature': account_signature}
        response = client.put("/account/update", json=data)
        assert response.status_code == 200
        await asyncio.sleep(0.2)
        data = {'address': "0x" + address[::-1], 'display_name': display_name, 'signature': account_signature}
        response = client.put("/account/update", json=data)
        assert response.status_code == 404
        display_name_get = (json.loads(client.get("/account/read", params={'address': "0x" + address}).content))[0][
            'display_name']
        assert display_name_get == 'resU'

        data = {'from_address': "0x" + from_address, 'message': message,
                'signature': message_signature}
        response = client.post("/message/create", json=data)
        assert response.status_code == 200
        await asyncio.sleep(0.2)
        response = client.post("/message/create", json=data)
        assert response.status_code == 404

        message = message[::-1]
        message_id = (json.loads(client.get("/message/read", params={'from_address': "0x" + from_address}).content))[0][
            'message_id']
        message_signature = secret_account_key.sign(message.encode('ASCII'), encoder=Base64Encoder).decode('ASCII')
        data = {'message_id': message_id, 'from_address': "0x" + from_address, 'message': message,
                'signature': message_signature}
        response = client.put("/message/update", json=data)
        assert response.status_code == 200
        await asyncio.sleep(0.3)
        data = {'message_id': -1, 'from_address': "0x" + from_address, 'message': message,
                'signature': message_signature}
        response = client.put("/message/update", json=data)
        assert response.status_code == 404

        response = client.delete("/account/delete", params={'address': "0x" + address})
        assert response.status_code == 200
        await asyncio.sleep(0.2)
        response = client.delete("/account/delete", params={'address': "0x" + address})
        assert response.status_code == 404

        response = client.delete("/message/delete", params={'message_id': message_id})
        assert response.status_code == 200
        await asyncio.sleep(0.2)
        response = client.delete("/message/delete", params={'message_id': message_id})
        assert response.status_code == 404

        async with db.connect() as ac:
            assert len((await ac.execute(select(Account))).all()) == 0


