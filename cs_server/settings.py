"""
配置
"""
from typing import Optional

from cryptography.fernet import Fernet


class Settings:
    # 密钥
    # SECRET_KEY = Fernet.generate_key()
    SECRET_KEY = b"wWMA-DqJEVi5s9bztbxHHanYUKKrocb-2mei0jrLQ8I="
    USER_LOGIN_TTL = 60 * 60 * 24
    # 快充基站数量
    NUMBER_FC_STATION = 3
    # 块冲基站充电速度
    FC_STATION_SPEED = 5
    # 慢充基站数量
    NUMBER_SC_STATION = 3
    # 慢冲基站充电速度
    SC_STATION_SPEED = 2
    # 等候区大小
    WAITING_AREA_SIZE = 3

    # **每个**充电桩后面队列长度
    CHARGE_AREA_QUEUE_SIZE = 3

    # 服务费单价
    SERVICE_UNIT_PRICE = 0.8

    PEEK_TIME_CHARGE_UNIT_PRICE = 1.0  # 峰值充电费
    COMMON_TIME_CHARGE_UNIT_PRICE = 0.7  # 普通充电费
    VALLEY_TIME_CHARGE_UNIT_PRICE = 0.4  # 谷值充电费

    # 事务
    TRAN_STATUS_FINISH = 1  # 事务结束状态标识
    TRAN_STATUS_UNFINISH = 0  # 事务未结束状态标识

    TRAN_CHARGE_MODE_FAST = 1  # 充电桩快充状态标识
    TRAN_CHARGE_MODE_SLOW = 0  # 充电桩慢充状态标识

    # 充电桩
    CHARGE_STATION_STATUS_OFF = 0  # 充电桩关闭状态标识
    CHARGE_STATION_STATUS_ON = 1  # 充电桩开启状态标识
    CHARGE_STATION_STATUS_ERR = 2  # 充电桩异常状态标识

    PERSIST_ID = False

s_id = 1
f_id = 1
if Settings.PERSIST_ID:
    import os
    import pickle

    if os.path.exists("./id_persist.pkl"):
        s_id, f_id = pickle.load(open("id_persist.pkl", "rb"))


def get_number(mode: int):
	global s_id,f_id
	if mode == 0:
		num = "S" + str(s_id)
		s_id += 1
		if Settings.PERSIST_ID:
			import pickle
			pickle.dump((s_id,f_id),open("id_persist.pkl", "wb"))
		return num
	elif mode == 1:
		num = "F" + str(f_id)
		f_id += 1
		if Settings.PERSIST_ID:
			import pickle
			pickle.dump((s_id,f_id),open("id_persist.pkl", "wb"))
		return num
	else:
		raise
