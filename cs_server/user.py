"""
用户
"""
from typing import List, Optional
from .transaction import Bill, Transaction
import time
from cryptography.fernet import Fernet
from .settings import Settings

def encode(obj:str)->str:
	f = Fernet(Settings.SECRET_KEY)
	f.encrypt_at_time(obj, time.time())

def decode(token:str)->str:
	f = Fernet(Settings.SECRET_KEY)
	try:
		obj = f.decrypt_at_time(token,Settings.USER_LOGIN_TTL,time.time())
	except Exception:
		return None
	else:
		return obj 
class User:
	id : str
	username : str

	def get_running_transaction(self)->Optional[Transaction]:
		return Transaction.get_running_transaction(self)
	
	def get_all_transactions(self)->List[Transaction]:
		return Transaction.get_all_transactions(self)

	def get_all_bills(self)->List[Bill]:
		pass
	
	@classmethod
	def register(cls,username:str,password:str)->Optional['User']:
		pass

	@classmethod
	def login(cls,username:str,password:str)->Optional['User']:
		pass

	@classmethod
	def get_user(cls,token:str)->Optional['User']:
		pass
