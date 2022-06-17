"""
web服务器运行的地方
"""
import uvicorn
from fastapi import FastAPI
from .user import User
from .driver import Driver
from typing import List
from .transaction import Bill
from .schedule import AreaMgmt
from .charge_station import StationStatus, ChargeStation

app = FastAPI()

@app.post("/register")
def register(username: str, password: str) -> User:
    "注册"
    u = User.register(username, password)
    return u

@app.post("/login")
def login(username: str, password: str) -> str:
    "登陆"
    return User.login(username, password)

@app.post("/transaction")
def transaction(Id: str, charge_mode: str, charge_quantity: str) -> None:
    "提交充电请求"
    u = User.get_user(Id)
    Driver.push(u, charge_mode, charge_quantity)

@app.post("/updateMode")
def updateMode(Id: str, new_mode: str) -> None:
    "修改充电模式"
    u = User.get_user(Id)
    t = u.get_running_transaction()
    Driver.update_mode(t, new_mode)

@app.post("/updateQuantity")
def updateQuantity(Id: str, new_quantity: str) -> None:
    "修改充电量"
    u = User.get_user(Id)
    t = u.get_running_transaction()
    Driver.update_quantity(t, new_quantity)

@app.post("/cancel")
def cancel(Id: str) -> None:
    "取消充电请求"
    u = User.get_user(Id)
    t = u.get_running_transaction()
    Driver.signal_station_cancel(t)

@app.post("/getTransaction")
def getTransaction(Id: str) -> str:
    "查看本车排队号码"
    u = User.get_user(Id)
    t = u.get_running_transaction()
    return t.wait_id

@app.post("/getWaiting")
def getWaiting(Id: str) -> str:
    "查看本充电模式下前车等待数量"
    u = User.get_user(Id)
    t = u.get_running_transaction()
    return AreaMgmt.get_waiting(t.id)

@app.post("/getBills")
def getBills(Id: str) -> List[Bill]:
    "查看充电详单"
    u = User.get_user(Id)
    return u.get_all_bills()

@app.post("/stationOn")
def stationOn(stationId: str) -> None:
    "启动充电桩"
    Driver.signal_station_on(stationId)

@app.post("/stationOff")
def stationOn(stationId: str) -> None:
    "关闭充电桩"
    Driver.signal_station_off(stationId)

@app.post("/stationStatus")
def stationStatus() -> List[StationStatus]:
    "充电桩状态"
    status_list = []
    status_list.append(ChargeStation.get_status())
    return status_list

@app.post("/stationId")
def stationId(stationId: str):
    "每个充电柱车辆"
    return AreaMgmt.get_charging(stationId)

@app.get("/statistics")
def statistics():
    "数据统计"
    return "statistics"

if __name__ == '__main__':
    uvicorn.run(app)
