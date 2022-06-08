"""
配置
"""

class Settings:
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
