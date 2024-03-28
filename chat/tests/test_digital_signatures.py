import datetime
import uuid
import pytest

from fastapi.testclient import TestClient
from nacl.encoding import Base64Encoder, HexEncoder
from nacl.signing import SigningKey

from chat import app

client = TestClient(app)


@pytest.fixture
def create_account():
    secret_account_key = SigningKey.generate()
    display_name = 'User'
    account_signature = secret_account_key.sign(display_name.encode('ASCII'), encoder=Base64Encoder)
    address = secret_account_key.verify_key.encode(encoder=HexEncoder)
    return display_name, account_signature, address


@pytest.fixture
def create_message():
    secret_message_key = SigningKey.generate()
    message = 'Hello, world!'
    message_signature = secret_message_key.sign(message.encode('ASCII'), encoder=Base64Encoder)
    from_address = secret_message_key.verify_key.encode(encoder=HexEncoder)
    message_id = str(uuid.uuid4())
    wrote_at = str(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
    return message_id, from_address, message, wrote_at, message_signature


def test_create_account_message(create_account, create_message) -> None:
    display_name, account_signature, address = create_account

    data = {'address': "0x" + address.decode('ASCII'), 'display_name': display_name,
            'signature': account_signature.decode('ASCII')}
    response = client.post("/account/create", json=data)
    assert response.status_code == 200

    response = client.post("/account/create", json=data)
    assert 'already used' in response.__dict__['_content'].decode('utf-8')

    message_id, from_address, message, wrote_at, message_signature = create_message

    data = {'message_id': message_id, 'from_address': "0x" + from_address.decode('ASCII'), 'message': message,
            'wrote_at': wrote_at,
            'signature': message_signature.decode('ASCII')}
    response = client.post("/message/create",
                           json=data)
    assert response.status_code == 200

    response = client.post("/message/create",
                           json=data)
    assert 'already created' in response.__dict__['_content'].decode('utf-8')



def test_forged_account_message() -> None:
    secret_account_key = SigningKey.generate()
    secret_account_key2 = SigningKey.generate()

    display_name = 'User'

    account_forged_signature = secret_account_key2.sign(display_name.encode('ASCII'), encoder=Base64Encoder)

    address = secret_account_key.verify_key.encode(encoder=HexEncoder)

    data = {'address': "0x" + address.decode('ASCII'), 'display_name': display_name,
            'signature': account_forged_signature.decode('ASCII')}
    response = client.post("/account/create", json=data)
    assert response.status_code == 422

    secret_message_key = SigningKey.generate()
    secret_message_key2 = SigningKey.generate()

    message = 'Hello, world!'

    message_forged_signature = secret_message_key2.sign(message.encode('ASCII'), encoder=Base64Encoder)

    from_address = secret_message_key.verify_key.encode(encoder=HexEncoder)
    message_id = str(uuid.uuid4())
    wrote_at = str(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))

    data = {'message_id': message_id, 'from_address': "0x" + from_address.decode('ASCII'), 'message': message,
            'wrote_at': wrote_at,
            'signature': message_forged_signature.decode('ASCII')}
    response = client.post("/message/create",
                           json=data)
    assert response.status_code == 422

if __name__=='__main__':
    test_create_account_message(create_account(),create_message())