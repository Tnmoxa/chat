import asyncio
import json

import pytest

from fastapi.testclient import TestClient
from nacl.encoding import Base64Encoder, HexEncoder
from nacl.signing import SigningKey
from sqlalchemy import select

from chat import app
from chatAPI.chat.models2 import AccountCreate, AccountUpdate, AccountDelete, MessageCreate, MessageDelete, \
    MessageUpdate, Account, Message

client = TestClient(app)


@pytest.fixture
def create_account():
    secret_account_key = SigningKey.generate()
    display_name = 'User'
    account_signature = secret_account_key.sign(display_name.encode('ASCII'), encoder=Base64Encoder).decode('ASCII')
    address = secret_account_key.verify_key.encode(encoder=HexEncoder).decode('ASCII')
    return secret_account_key, display_name, account_signature, address


@pytest.fixture
def create_message(create_account):
    secret_account_key, display_name, account_signature, address = create_account
    message = 'Hello, world!'
    message_signature = secret_account_key.sign(message.encode('ASCII'), encoder=Base64Encoder).decode('ASCII')
    from_address = address
    return (secret_account_key, display_name, account_signature, address), (from_address, message, message_signature)


@pytest.mark.asyncio
async def test_create_read_update_delete_account_message(create_message, db) -> None:
    (secret_account_key, display_name, account_signature, address) = create_message[0]
    (from_address, message, message_signature) = create_message[1]

    data = {'address': "0x" + address, 'display_name': display_name, 'signature': account_signature}
    response = client.post("/account/create", json=data)
    assert response.status_code == 200
    response = client.post("/account/create", json=data)
    assert response.status_code == 404

    display_name = display_name[::-1]
    account_signature = secret_account_key.sign(display_name.encode('ASCII'), encoder=Base64Encoder).decode('ASCII')
    data = {'address': "0x" + address, 'display_name': display_name, 'signature': account_signature}
    response = client.put("/account/update", json=data)
    assert response.status_code == 200
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
    data = {'message_id': message_id, 'from_address': "0x" + from_address[::-1], 'message': message,
            'signature': message_signature}
    response = client.put("/message/update", json=data)
    assert response.status_code == 404

    response = client.delete("/account/delete", params={'address': "0x" + address})
    assert response.status_code == 200
    response = client.delete("/account/delete", params={'address': "0x" + address})
    assert response.status_code == 404

    response = client.delete("/message/delete", params={'message_id': message_id})
    assert response.status_code == 200
    response = client.delete("/message/delete", params={'message_id': message_id})
    assert response.status_code == 404

    async with db.connect() as ac:
        assert len((await ac.execute(select(Account))).all()) == 0


@pytest.mark.asyncio
def test_update_account_message(create_message) -> None:
    (secret_account_key, display_name, account_signature, address) = create_message[0]
    (from_address, message, message_signature) = create_message[1]


# def test_forged_account_message() -> None:
#     secret_account_key = SigningKey.generate()
#     secret_account_key2 = SigningKey.generate()
#
#     display_name = 'User'
#
#     account_forged_signature = secret_account_key2.sign(display_name.encode('ASCII'), encoder=Base64Encoder)
#
#     address = secret_account_key.verify_key.encode(encoder=HexEncoder)
#
#     data = {'address': "0x" + address.decode('ASCII'), 'display_name': display_name,
#             'signature': account_forged_signature.decode('ASCII')}
#     response = client.post("/account/create", json=data)
#     assert response.status_code == 422
#
#     secret_message_key = SigningKey.generate()
#     secret_message_key2 = SigningKey.generate()
#
#     message = 'Hello, world!'
#
#     message_forged_signature = secret_message_key2.sign(message.encode('ASCII'), encoder=Base64Encoder)
#
#     from_address = secret_message_key.verify_key.encode(encoder=HexEncoder)
#     message_id = str(uuid.uuid4())
#     wrote_at = str(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
#
#     data = {'message_id': message_id, 'from_address': "0x" + from_address.decode('ASCII'), 'message': message,
#             'wrote_at': wrote_at,
#             'signature': message_forged_signature.decode('ASCII')}
#     response = client.post("/message/create",
#                            json=data)
#     assert response.status_code == 422


if __name__ == '__main__':
    test_create_account_message(create_account(), create_message())
