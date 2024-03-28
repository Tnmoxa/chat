from datetime import datetime
from nacl.exceptions import BadSignatureError
from pydantic import BaseModel,  model_validator
from nacl.signing import VerifyKey

from chat.new_types import Bytes64, BytesHex, UUIDv4


class AccountKey(BaseModel):
    """ Account keys """
    address: BytesHex


class AccountPost(AccountKey):
    """ Account create/update message """
    display_name: str
    signature: Bytes64

    @model_validator(mode='after')
    def check_signature(self) -> 'AccountPost':
        try:
            verify_key = VerifyKey(self.address)
            if len(self.signature) == 64:
                verify_key.verify(self.display_name.encode('utf-8'), self.signature)
            else:
                verify_key.verify(self.signature)
        except BadSignatureError:
            raise ValueError('Signature was forged or corrupt')
        return self


class AccountDelete(AccountKey):
    """ Account delete message """


class MessageKey(BaseModel):
    """ Message keys """
    message_id: UUIDv4
    from_address: BytesHex


class MessagePost(MessageKey):
    """ Message create/update message """
    message: str
    wrote_at: datetime
    signature: Bytes64

    @model_validator(mode='after')
    def check_signature(self) -> 'MessagePost':
        try:
            verify_key = VerifyKey(self.from_address)
            if len(self.signature) == 64:
                verify_key.verify(self.message.encode('utf-8'), self.signature)
            else:
                verify_key.verify(self.signature)
        except BadSignatureError:
            raise ValueError('Signature was forged or corrupt')
        return self


class MessageDelete(MessageKey):
    """ Message delete message """
