"""
充电桩，充电桩管理
"""
from typing import List
from .transaction import Transaction
class StationStatus:
	id : str
	type : int
	status : int
	charge_frequency:int # 系统启动后充电次数
	charge_duration:int # 系统启动后充电时长,单位秒
	charge_quantity:float # 系统启动后充电量,单位瓦

	cumulative_charging_times : int # 累计充电次数
	cumulative_charging_duration : int # 累计充电时长,单位秒
	cumulative_charging_quantity : float # 累计充电量,单位瓦
	cumulative_charging_fee : float # 累计充电费用,单位元
	cumulative_serviing_fee : float # 累计服务费用,单位元
	cumulative_total_fee : float # 累计总费用,单位元

class ChargeStation:
	"""充电桩基类
	还需要实现model.py 里的ORM模型
	下面的代码是为了方便IDE自动提示，实现时去掉
	"""
	id : str
	type : int
	status : int
	charging_power : float
	cumulative_charging_times : int # 累计充电次数
	cumulative_charging_duration : int # 累计充电时长,单位秒
	cumulative_charging_quantity : float # 累计充电量,单位瓦
	cumulative_charging_fee : float # 累计充电费用,单位元
	cumulative_serviing_fee : float # 累计服务费用,单位元
	cumulative_total_fee : float # 累计总费用,单位元

	def turn_on():
		"""开启充电桩
		主要用于演示
		调用driver.signal_station_on()
		"""
		pass

	def turn_off():
		"""关闭充电桩
		主要用于演示
		调用driver.signal_station_off()
		"""
		pass

	def get_status()->StationStatus:
		"""获取充电桩状态(见作业要求)
		"""
		raise
		return StationStatus()

	def start(tran:Transaction)->None:
		"""开始充电
		启动定时器，n秒后，调用driver.signal_station_finish()
		"""
		pass

	def cancel()->None:
		"""取消定时器
		用于取消充电事务时
		"""
		pass

	def report_error()->None:
		"""汇报一个错误
		主要用于演示.调用driver.signal_station_error()
		"""
		pass

	

class StationMgmt:
	"""充电桩管理
	"""
	def __init__(self,station:List[ChargeStation]) -> None:
		pass
	
	def get_status(self)->List[StationStatus]:
		pass
	
	def start(self,station_id:str,tran:Transaction)->None:
		"""开始充电

		Args:
			station_id (str): 充电桩ID
			tran (Transaction): 充电订单
		"""
		pass

	def get_number(self)->str:
		"""取号
		"""
		pass

