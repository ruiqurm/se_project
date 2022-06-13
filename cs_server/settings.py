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

	# 服务费单价
	SERVICE_UNIT_PRICE = 0.8

	PEEK_TIME_CHARGE_UNIT_PRICE = 1.0
	COMMON_TIME_CHARGE_UNIT_PRICE = 0.7
	VALLEY_TIME_CHARGE_UNIT_PRICE = 0.4

	# 事务
	TRAN_STATUS_FINISH = 1
	TRAN_STATUS_UNFINISH = 0

	TRAN_CHARGE_MODE_FAST = 1
	TRAN_CHARGE_MODE_SLOW = 0

	# 充电桩
	CHARGE_STATION_STATUS_OFF = 0
	CHARGE_STATION_STATUS_ON = 1
	CHARGE_STATION_STATUS_ERR = 2