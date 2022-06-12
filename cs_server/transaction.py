"""
包括transaction,Bill类
"""
from datetime import datetime, timedelta
from typing import List, Optional, Union
# from .user import User
class Transaction:
	id : str
	user : 'User'
	mode : int
	start_time : datetime
	end_time : datetime
	waiting_time : timedelta
	charge_time : timedelta
	serving_fee : float # 服务费
	charging_fee : float # 充电费
	
	def cancel(self)->None:
		"""取消充电
		"""
		pass

	def update_mode(self,mode:int)->None:
		"""更新充电模式
		"""
		pass

	def update_quantity(self,quantity:float)->None:
		"""更新充电量
		"""
		pass

	def start(self)->None:
		"""开始充电
		"""
		pass

	@classmethod
	def get_running_transaction(cls,user:'User')->Optional['Transaction']:
		"""获取正在进行的订单
		"""
		pass

	@classmethod
	def get_all_transactions(cls,user:'User')->List['Transaction']:
		"""获取所有订单
		"""
		pass

class Bill:
	pass