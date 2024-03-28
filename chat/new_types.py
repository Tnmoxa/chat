from base64 import standard_b64encode, standard_b64decode

from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema, BaseModel
from typing_extensions import Annotated

from pydantic import UUID4


def base64decoder(value):
    if isinstance(value, str):
        value = standard_b64decode(value.encode('ascii'))
    return value


def hex_decoder(value):
    if isinstance(value, str) and len(value) % 2 == 0 and value.lower().startswith('0x'):
        value = bytes.fromhex(value[2:])
    return value


def only_bytes(value):
    if isinstance(value, bytes):
        return value
    raise ValueError('value is not validated as bytes')


Bytes64 = Annotated[
    bytes,
    BeforeValidator(lambda value: only_bytes(base64decoder(value))),
    PlainSerializer(lambda value: standard_b64encode(value).decode('ascii'), return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]

BytesHex = Annotated[
    bytes,
    BeforeValidator(lambda value: only_bytes(hex_decoder(value))),
    PlainSerializer(lambda value: '0x' + value.hex().upper(), return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]

UUIDv4 = Annotated[
    UUID4,
    PlainSerializer(lambda value: str(value), return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]

