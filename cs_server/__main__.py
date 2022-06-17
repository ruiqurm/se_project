"""
web服务器运行的地方
"""
import uvicorn
from fastapi import FastAPI
from .user import User
from .driver import Driver
from typing import List, Optional
from .transaction import Bill, Transaction
from .schedule import AreaMgmt, Scheduler
from .charge_station import StationStatus, ChargeStation, StationMgmt
from .model import init
from . import serializers
class A:
    def get_waiting(self, id):
        return 0

    def get_charging(self, id):
        return ["t1", "t2"]
class DumbScheduler:
	def __init__(self, sm:StationMgmt):
		self.station_mgmt = sm
		self.areaMngt=A()
	def on_finish(self,station_id:int)->None:
		pass

	def on_push(self,user_id,mode:int,quantity:float):
		pass
	def on_update_mode(self,tran:Transaction,mode:int):
		pass
	def on_update_quantity(self,tran,value:float):
		pass
	def on_cancel(self,tran):
		pass

	def on_station_on(self,station_id:int):
		raise

	def on_station_off(self,station_id:int):
		pass
driver: Optional[Driver] = None
station_mgmt: Optional[StationMgmt] = None
scheduler: Optional[Scheduler] = None

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """
    初始化
    """
    global driver,station_mgmt,scheduler
    init()
    d = Driver(None)
    stations = [
        ChargeStation.create_station(0, d),
        ChargeStation.create_station(0, d),
        ChargeStation.create_station(0, d),
        ChargeStation.create_station(1, d),
        ChargeStation.create_station(1, d)
    ]
    sm = StationMgmt(stations)
    sch = DumbScheduler(sm)
    # for station in stations:
    #     station.turn_on()
    d.scheduler = sch
    driver = d
    station_mgmt = sm
    scheduler = sch

@app.post("/register",response_model=serializers.User)
def register(username: str, password: str) -> User:
    """注册
    username: 用户名 \n
    password: 密码 \n
    返回注册成功的用户
    """
    u = User.register(username, password)
    return u


@app.post("/login")
def login(username: str, password: str) -> str:
    """登录
    username: 用户名 \n
    password: 密码 \n
    返回一个token
    """
    return User.login(username, password)


@app.post("/transaction")
def transaction(Id: str, charge_mode: int, charge_quantity: float) -> None:
    "提交充电请求"
    u = User.get_user(Id)
    driver.push(u, charge_mode, charge_quantity)


@app.post("/updateMode")
def updateMode(Id: str, new_mode: str) -> None:
    "修改充电模式"
    u = User.get_user(Id)
    t = u.get_running_transaction()
    driver.update_mode(t, new_mode)


@app.post("/updateQuantity")
def updateQuantity(Id: str, new_quantity: float) -> None:
    "修改充电量"
    u = User.get_user(Id)
    t = u.get_running_transaction()
    driver.update_quantity(t, new_quantity)


@app.post("/cancel")
def cancel(Id: str) -> None:
    "取消充电请求"
    u = User.get_user(Id)
    t = u.get_running_transaction()
    driver.signal_station_cancel(t)


@app.post("/getTransaction")
def getTransaction(Id: str) -> str:
    "查看本车排队号码"
    u = User.get_user(Id)
    t = u.get_running_transaction()
    return t.wait_id


@app.post("/getWaiting")
def getWaiting(Id: str) -> int:
    "查看本充电模式下前车等待数量"
    u = User.get_user(Id)
    t = u.get_running_transaction()
    return scheduler.areaMngt.get_waiting(t.id)


@app.post("/getBills")
def getBills(Id: str) -> List[Bill]:
    "查看充电详单"
    u = User.get_user(Id)
    return u.get_all_bills()


@app.post("/stationOn")
def stationOn(stationId: int) -> None:
    "启动充电桩"
    station_mgmt.turn_on(stationId)


@app.post("/stationOff")
def stationOff(stationId: int) -> None:
    "关闭充电桩"
    station_mgmt.turn_off(stationId)


@app.post("/stationStatus")
def stationStatus() -> List[StationStatus]:
    "充电桩状态"
    return station_mgmt.get_status()


@app.post("/stationId")
def stationId(stationId: int):
    "每个充电柱车辆"
    return scheduler.areaMngt.get_charging(stationId)


@app.get("/statistics")
def statistics():
    "数据统计"
    return "statistics"


if __name__ == '__main__':
    uvicorn.run(app)