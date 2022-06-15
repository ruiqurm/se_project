import time
from typing import Dict, Optional, Tuple, List
from cs_server.model import BillModel, UserModel, ChargeStationModel, TransactionModel, SqliteDatabase, init
import pytest
from cs_server.charge_station import ChargeStation, StationMgmt
from cs_server.user import User
from cs_server.transaction import Transaction, Bill
from cs_server.settings import Settings
from cs_server.driver import Driver
from cs_server.schedule import Scheduler
import datetime
from cs_server import settings


@pytest.fixture
def clear_db():
    init()
    ChargeStationModel.delete().execute()
    UserModel.delete().execute()
    TransactionModel.delete().execute()
    BillModel.delete().execute()


def setup() -> Tuple[Driver, Scheduler, StationMgmt]:
    d = Driver(None)
    stations = [
        ChargeStation.create_station(0, d),
        ChargeStation.create_station(0, d),
        ChargeStation.create_station(0, d),
        ChargeStation.create_station(1, d),
        ChargeStation.create_station(1, d)
    ]
    # for station in stations:
    #     station.turn_on()
    sm = StationMgmt(stations)
    sch = Scheduler(sm)
    d.scheduler = sch
    return d, sch, sm


def virtual_time_to_real_interval(t2: datetime.datetime,t1:datetime.datetime) -> float:
    # 计算真实睡眠时间
    return ((t2 - t1) / Settings.TIME_FLOW_RATE).total_seconds()


class Command:
    unuse_user = []
    vid_to_user: Dict[int, User] = {}
    base = settings.TODAY_DATETIME
    def __init__(self, triger_time: datetime.time, v1, v2, v3, v4):
        self.triger_time = triger_time
        self.type = v1
        if v1 == "A":
            vid = v2
            self.vid = vid
            if vid not in self.vid_to_user:
                u = self.unuse_user.pop(0)
                self.user = u
                self.vid_to_user[vid] = u
            else:
                # 取消
                u = self.vid_to_user[vid]
                self.user = u
            if v3 == 'T':
                self.mode = Settings.TRAN_CHARGE_MODE_SLOW
            elif v3 == 'F':
                self.mode = Settings.TRAN_CHARGE_MODE_FAST
            else:
                self.mode = None
            if v4 > 0:
                self.quantity = float(v4)
            else:
                # 取消
                self.quantity = None
        elif v1 == "B":
            station_id = int(v2[1:])
            if v2[0] == 'F':
                station_id += 3
            self.station_id = station_id
            self.station_mode = bool(v4)
        else:
            vid = v2
            self.vid = vid
            if vid not in self.vid_to_user:
                raise "No such vid"
            u = self.vid_to_user[vid]
            self.user = u
            if v3 == 'T':
                self.mode = Settings.TRAN_CHARGE_MODE_SLOW
            elif v3 == 'F':
                self.mode = Settings.TRAN_CHARGE_MODE_FAST
            else:
                self.mode = None
            if v4 == 0:
                self.quantity = 0
            elif v4 < 0:
                self.quantity = None
            else:
                self.quantity = float(v4)

    def execute(self, driver: Driver, station_mgmt: StationMgmt):
        if self.type == 'A':
            if self.quantity is not None:
                driver.push(self.user, self.mode, self.quantity)
            else:
                t = self.user.get_running_transaction()
                driver.signal_station_cancel(t)
        elif self.type == 'B':
            if self.station_mode == True:
                station_mgmt.turn_on(self.station_id)
            else:
                station_mgmt.turn_off(self.station_id)
        elif self.type == 'C':
            t = self.user.get_running_transaction()
            if self.quantity is not None:
                driver.update_quantity(t, self.quantity)
            if self.mode is not None:
                driver.update_mode(t, self.mode)

    def time(self) -> datetime.datetime:
        return self.base + datetime.timedelta(hours=self.triger_time.hour, minutes=self.triger_time.minute,
                                         seconds=self.triger_time.second)

    def __str__(self):
        if self.type == 'A':
            if self.quantity is None:
                return f"[{self.triger_time.strftime('%H:%M:%S')}]取消 {self.vid}"
            if self.mode == Settings.TRAN_CHARGE_MODE_SLOW:
                mode = "T 慢充"
            else:
                mode = "F 快充"
            return f"[{self.triger_time.strftime('%H:%M:%S')}]添加 事务{self.vid},绑定到用户{self.user.username},类型{mode},充电量{self.quantity}"
        elif self.type == "B":
            if self.station_mode:
                return f"[{self.triger_time.strftime('%H:%M:%S')}]启动 充电桩{self.station_id}"
            else:
                return f"[{self.triger_time.strftime('%H:%M:%S')}]故障 充电桩{self.station_id}"
        elif self.type == "C":
            if self.mode == Settings.TRAN_CHARGE_MODE_SLOW:
                mode = "T 慢充"
            elif self.mode == Settings.TRAN_CHARGE_MODE_FAST:
                mode = "F 快充"
            else:
                mode = ""
            if self.quantity < 0:
                quantity = ""
            else:
                quantity = str(self.quantity)
            if self.quantity > 0 and self.mode is not None:
                return f"[{self.triger_time.strftime('%H:%M:%S')}]修改 {self.vid} 充电量={quantity},模式={mode}"
            elif self.quantity > 0:
                return f"[{self.triger_time.strftime('%H:%M:%S')}]修改 {self.vid} 充电量={quantity}"
            elif self.mode > 0:
                return f"[{self.triger_time.strftime('%H:%M:%S')}]修改 {self.vid} 模式={mode}"


def test_chargeStation(clear_db):
    driver, scheduler, station_mgmt = setup()
    users = [User.register(f"user{i}", f"user{i}") for i in range(1, 31)]
    Command.unuse_user = users
    print()
    commands = [Command(datetime.time(6, 0), 'A', 'V1', 'T', 40),
                Command(datetime.time(6, 5), 'A', 'V2', 'T', 30),
                Command(datetime.time(6, 10), 'A', 'V3', 'F', 100),
                Command(datetime.time(6, 15), 'A', 'V4', 'F', 120),
                Command(datetime.time(6, 20), 'A', 'V2', 'O', 0),
                Command(datetime.time(6, 25), 'A', 'V5', 'T', 20),
                Command(datetime.time(6, 30), 'A', 'V6', 'T', 20),
                Command(datetime.time(6, 35), 'A', 'V7', 'F', 110),
                Command(datetime.time(6, 40), 'A', 'V8', 'T', 20),
                Command(datetime.time(6, 45), 'A', 'V9', 'F', 105),
                Command(datetime.time(6, 50), 'A', 'V10', 'T', 10),
                Command(datetime.time(6, 55), 'A', 'V11', 'F', 110),
                Command(datetime.time(7, 0), 'A', 'V12', 'F', 90),
                Command(datetime.time(7, 5), 'A', 'V13', 'F', 110),
                Command(datetime.time(7, 10), 'A', 'V14', 'F', 95),
                Command(datetime.time(7, 15), 'A', 'V15', 'T', 10),
                Command(datetime.time(7, 20), 'A', 'V16', 'F', 60),
                Command(datetime.time(7, 25), 'A', 'V17', 'T', 10),
                Command(datetime.time(7, 30), 'A', 'V18', 'T', 7.5),
                Command(datetime.time(7, 35), 'A', 'V19', 'F', 75),
                Command(datetime.time(7, 40), 'A', 'V20', 'F', 95),
                Command(datetime.time(7, 45), 'A', 'V21', 'F', 95),
                Command(datetime.time(7, 50), 'A', 'V22', 'F', 70),
                Command(datetime.time(7, 55), 'A', 'V23', 'F', 80),
                Command(datetime.time(8, 0), 'A', 'V24', 'T', 5),
                Command(datetime.time(8, 20), 'A', 'V25', 'T', 15),
                Command(datetime.time(8, 25), 'B', 'T1', 'O', 0),
                Command(datetime.time(8, 30), 'A', 'V26', 'T', 20),
                Command(datetime.time(8, 35), 'A', 'V27', 'T', 25),
                Command(datetime.time(8, 50), 'B', 'F1', 'O', 0),
                Command(datetime.time(9, 0), 'A', 'V28', 'F', 30),
                Command(datetime.time(9, 10), 'A', 'V1', 'O', 0),
                Command(datetime.time(9, 15), 'B', 'T1', 'O', 1),
                Command(datetime.time(9, 20), 'A', 'V27', 'O', 0),
                Command(datetime.time(9, 25), 'C', 'V21', 'F', 35),
                Command(datetime.time(9, 30), 'A', 'V19', 'O', 0),
                Command(datetime.time(9, 35), 'A', 'V28', 'O', 0),
                Command(datetime.time(9, 40), 'C', 'V23', 'F', 40),
                Command(datetime.time(9, 50), 'A', 'V29', 'T', 30),
                Command(datetime.time(9, 55), 'C', 'V14', 'F', 30),
                Command(datetime.time(10, 0), 'A', 'V30', 'T', 10),
                Command(datetime.time(10, 50), 'B', 'F1', 'O', 1)
                ]
    settings.START_DATETIME = datetime.datetime.now()
    _ = datetime.datetime.today()
    datetime.datetime(year=_.year, month=_.month, day=_.day, hour=Settings.START_TIME.hour,
                      minute=Settings.START_TIME.minute, second=Settings.START_TIME.second)
    for i in commands:
        print(i)
    # 测试
    # for i,command in enumerate(commands):
    #     if i != 0:
    #         last = commands[i-1]
    #         sleep_time = virtual_time_to_real_interval(command.time(),last.time())
    #         time.sleep(sleep_time)
    #     command.execute(driver,station_mgmt)
