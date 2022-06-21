"""
序列化器

把模型转成json格式

这一部分应该只有web部分需要用到
下面列举了一下可能需要序列化的类
"""
import pydantic
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from .settings import now

class StationStatus(pydantic.BaseModel):
	time = now()
	id: int
	type: int
	status: int
	charge_frequency: int
	charge_duration: float
	charge_quantity: float
	cumulative_charging_times: int
	cumulative_charging_duration: float
	cumulative_charging_quantity: float
	cumulative_charging_fee: float
	cumulative_serviing_fee: float
	cumulative_total_fee: float

class Transaction(pydantic.BaseModel):
	pass

class User(pydantic.BaseModel):
	username : str
	password : str

class Bill(pydantic.BaseModel):
	user_id: int
	wait_id: str
	id: Optional[int]
	time: datetime
	station_id: int
	quantity: float
	duration: timedelta
	start_time: datetime
	end_time: datetime
	serving_fee: float
	charging_fee: float
	total_fee: float

class Snapshot():
	"""
	每次动作后，充电区内的状态
	"""
	description : str
	detail : Optional[str]
	waiting_area : List[str]
	station_area : Dict[int,List[str]]