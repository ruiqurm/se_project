"""
用户
"""
from typing import List, Optional, Any
from .model import UserModel
from .transaction import Bill, Transaction
import time
from cryptography.fernet import Fernet
from .settings import Settings

def encode(obj: str) -> str:
    f = Fernet(Settings.SECRET_KEY)
    return f.encrypt_at_time(obj.encode(), int(time.time())).decode()


def decode(token: str) -> Optional[str]:
    f = Fernet(Settings.SECRET_KEY)
    try:
        obj = f.decrypt_at_time(token.encode(), Settings.USER_LOGIN_TTL, int(time.time()))
    except Exception:
        return None
    else:
        return obj.decode()


class User:
    increment_id = 0

    def __init__(self, _id: int, username: str, password: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.id = _id
        self.username = username
        self.password = password

    def get_running_transaction(self) -> Optional[Transaction]:
        return Transaction.get_running_transaction(self.id)

    def get_all_transactions(self) -> List[Transaction]:
        return Transaction.get_all_transactions(self.id)

    def get_all_bills(self) -> List[Bill]:
        return Bill.get_user_bills(self.id)

    @classmethod
    def register(cls, username: str, password: str) -> Optional['User']:
        founds = list(UserModel.select().where(UserModel.username==username))
        if len(founds) > 0:
            return None
        # new_id = cls.increment_id
        m = UserModel.create(username=username, password=password)
        # cls.increment_id += 1
        return User(_id=m.id, username=username, password=password)

    @classmethod
    def login(cls, username: str, password: str) -> Optional[str]:
        founds = list(UserModel.select().where(UserModel.username==username))
        if len(founds) < 1:
            return None
        if  founds[0].password != password:
            return None
        return encode(str(founds[0].id))

    @classmethod
    def get_user(cls, token: str) -> Optional['User']:
        str_id = decode(token)
        if str_id is None:
            return None
        _id = int(str_id)
        return User.get_user_by_id(_id)

    @classmethod
    def get_user_by_id(cls, _id: int):
        try:
            user = UserModel.get_by_id(_id)
        except Exception:
            return None
        found_dict = user.__dict__['__data__']
        return User(_id=found_dict["id"], username=found_dict["username"], password=found_dict["password"])
