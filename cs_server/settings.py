"""
配置
"""
from cryptography.fernet import Fernet
class Settings:
	# 密钥
	# SECRET_KEY = Fernet.generate_key()
	SECRET_KEY = b"wWMA-DqJEVi5s9bztbxHHanYUKKrocb-2mei0jrLQ8I="
	USER_LOGIN_TTL = 60 * 60 * 24  
	# 快充基站数量
	NUMBER_FC_STATION = 3
	# 块冲基站充电速度
	FC_STATION_SPEED=5
	# 慢充基站数量
	NUMBER_SC_STATION = 3
	# 慢冲基站充电速度
	SC_STATION_SPEED=2
	# 等候区大小
	WAITING_AREA_SIZE = 3

	# **每个**充电桩后面队列长度
	CHARGE_AREA_QUEUE_SIZE = 3
