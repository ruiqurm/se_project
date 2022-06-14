"""
充电桩，充电桩管理
"""
from datetime import datetime, timedelta
from typing import List, Optional
from threading import Timer
from . import driver
from .model import ChargeStationModel
from .transaction import Transaction
from .settings import Settings,now,real_time


class StationStatus:
    def __init__(self,
                 _id: int,
                 _type: int,
                 status: int,
                 charge_frequency: int,  # 系统启动后充电次数
                 charge_duration: timedelta,  # 系统启动后充电时长,单位秒
                 charge_quantity: float,  # 系统启动后充电量,单位瓦
                 cumulative_charging_times: int,  # 累计充电次数
                 cumulative_charging_duration: timedelta,  # 累计充电时长,单位秒
                 cumulative_charging_quantity: float,  # 累计充电量,单位瓦
                 cumulative_charging_fee: float,  # 累计充电费用,单位元
                 cumulative_serviing_fee: float,  # 累计服务费用,单位元
                 cumulative_total_fee: float,  # 累计总费用,单位元
                 ):
        self.time = now()
        self.id = _id
        self.type = _type
        self.status = status
        self.charge_frequency = charge_frequency
        self.charge_duration = charge_duration
        self.charge_quantity = charge_quantity
        self.cumulative_charging_times = cumulative_charging_times
        self.cumulative_charging_duration = cumulative_charging_duration
        self.cumulative_charging_quantity = cumulative_charging_quantity
        self.cumulative_charging_fee = cumulative_charging_fee
        self.cumulative_serviing_fee = cumulative_serviing_fee
        self.cumulative_total_fee = cumulative_total_fee


class ChargeStation:
    """充电桩基类
    还需要实现model.py 里的ORM模型
    下面的代码是为了方便IDE自动提示，实现时去掉
    """

    def __init__(self, _id: int,  # 充电桩编号
                 _type: int,  # 充电桩类型
                 status: int,  #
                 charging_power: float,  # 充电功率 度/小时
                 cumulative_charging_times: int,  # 累计充电次数
                 cumulative_charging_duration: timedelta,  # 累计充电时长,单位秒
                 cumulative_charging_quantity: float,  # 累计充电量,单位瓦
                 cumulative_charging_fee: float,  # 累计充电费用,单位元
                 cumulative_serviing_fee: float,  # 累计服务费用,单位元
                 cumulative_total_fee: float,  # 累计总费用,单位元
                 _driver: driver.Driver
                 ):
        self.id = _id
        self.type = _type
        self.status = status
        self.charging_power = charging_power
        self.cumulative_charging_times = cumulative_charging_times
        self.cumulative_charging_duration = cumulative_charging_duration
        self.cumulative_charging_quantity = cumulative_charging_quantity
        self.cumulative_charging_fee = cumulative_charging_fee
        self.cumulative_serviing_fee = cumulative_serviing_fee
        self.cumulative_total_fee = cumulative_total_fee
        self.driver = _driver
        self.t = None
        self.now_tran = None

        # self.initial_id = _id
        # self.initial_type = _type
        # self.initial_status = status
        self.initial_charging_power = charging_power
        self.initial_cumulative_charging_times = cumulative_charging_times
        self.initial_cumulative_charging_duration = cumulative_charging_duration
        self.initial_cumulative_charging_quantity = cumulative_charging_quantity
        self.initial_cumulative_charging_fee = cumulative_charging_fee
        self.initial_cumulative_serviing_fee = cumulative_serviing_fee
        self.initial_cumulative_total_fee = cumulative_total_fee

    @classmethod
    def create_station(cls, type: int, driver: driver.Driver):
        m = ChargeStationModel.create(type=type, status=Settings.CHARGE_STATION_STATUS_OFF,
                                      charging_power=Settings.SC_STATION_SPEED if Settings.TRAN_CHARGE_MODE_SLOW
                                      else Settings.FC_STATION_SPEED,
                                      cumulative_charging_times=0,
                                      cumulative_charging_duration=timedelta(seconds=0),
                                      cumulative_charging_quantity=0,
                                      cumulative_charging_fee=0,
                                      cumulative_serviing_fee=0,
                                      cumulative_total_fee=0
                                      )
        return cls(_id=m.id, _type=type, status=Settings.CHARGE_STATION_STATUS_OFF,
                   charging_power=Settings.SC_STATION_SPEED
                   if Settings.TRAN_CHARGE_MODE_SLOW else Settings.FC_STATION_SPEED,
                   cumulative_charging_times=0,
                   cumulative_charging_duration=timedelta(seconds=0),
                   cumulative_charging_quantity=0,
                   cumulative_charging_fee=0,
                   cumulative_serviing_fee=0,
                   cumulative_total_fee=0, _driver=driver)

    def turn_on(self):
        """开启充电桩
        主要用于演示
        调用driver.signal_station_on()
        """
        ChargeStationModel.update(status=Settings.CHARGE_STATION_STATUS_ON)\
            .where(ChargeStationModel.id == self.id).execute()
        self.driver.signal_station_on(station=self)

    def turn_off(self):
        """关闭充电桩
        主要用于演示
        调用driver.signal_station_off()
        """
        if self.now_tran is not None:
            self.cancel()
        ChargeStationModel.update(status=Settings.CHARGE_STATION_STATUS_OFF) \
            .where(ChargeStationModel.id == self.id).execute()
        self.driver.signal_station_off(station=self)

    def get_status(self) -> StationStatus:
        """获取充电桩状态(见作业要求)
        """
        return StationStatus(
            _id=self.id,
            _type=self.type,
            status=self.status,
            charge_frequency=self.cumulative_charging_times - self.initial_cumulative_charging_times,
            charge_duration=self.cumulative_charging_duration - self.initial_cumulative_charging_duration,
            charge_quantity=self.cumulative_charging_quantity - self.initial_cumulative_charging_quantity,
            cumulative_charging_times=self.cumulative_charging_times,
            cumulative_charging_duration=self.cumulative_charging_duration,
            cumulative_charging_quantity=self.cumulative_charging_quantity,
            cumulative_charging_fee=self.cumulative_charging_fee,
            cumulative_serviing_fee=self.cumulative_serviing_fee,
            cumulative_total_fee=self.cumulative_total_fee,
        )

    def __finish_tran(self, tran: Transaction):
        tran.finish()
        self.cumulative_charging_duration += tran.charge_time
        self.cumulative_charging_times += 1
        self.cumulative_charging_quantity += tran.quantity
        self.cumulative_charging_fee += tran.charging_fee
        self.cumulative_serviing_fee += tran.serving_fee
        self.cumulative_total_fee += tran.charging_fee + tran.serving_fee

        ChargeStationModel.update(
            cumulative_charging_duration=self.cumulative_charging_duration,
            cumulative_charging_times=self.cumulative_charging_times,
            cumulative_charging_quantity=self.cumulative_charging_quantity,
            cumulative_charging_fee=self.cumulative_charging_fee,
            cumulative_serviing_fee=self.cumulative_serviing_fee,
            cumulative_total_fee=self.cumulative_total_fee,
        ).where(ChargeStationModel.id == self.id).execute()
        self.now_tran = None
        self.driver.signal_station_finish(station=self)

    def start(self, tran: Transaction) -> None:
        """开始充电
        启动定时器，n秒后，调用driver.signal_station_finish()
        """
        if self.now_tran is not None:
            return
        self.now_tran = tran
        tran.start(station_id=self.id)
        self.t = Timer(real_time(tran.end_time,tran.start_time).total_seconds(), self.__finish_tran, (tran,))
        self.t.start()

    def cancel(self) -> None:
        """取消定时器
        用于取消充电事务时
        """
        if self.now_tran is None:
            return
        self.t.cancel()
        self.now_tran.finish()
        self.now_tran = None
        self.driver.signal_station_cancel(station=self)

    def report_error(self) -> None:
        """汇报一个错误
        主要用于演示.调用driver.signal_station_error()
        """
        self.status = Settings.CHARGE_STATION_STATUS_ERR
        ChargeStationModel.update(status=self.status).where(ChargeStationModel.id == self.id).execute()
        if self.now_tran is not None:
            self.t.cancel()
            self.now_tran.finish()
            self.now_tran = None
        self.driver.signal_station_error(station=self)


class StationMgmt:
    """充电桩管理
    """

    def __init__(self, stations: List[ChargeStation]) -> None:
        self.stations = {}  # dict[int,ChargeStation]
        for s in stations:
            self.stations[s.id] = s
        self.f_id = 0
        self.s_id = 0

    def get_status(self) -> List[StationStatus]:
        status_list = []
        for _id, station in self.stations:
            status_list.append(station.get_status())
        return status_list

    def turn_on(self,station_id:int):
        self.stations[station_id].turn_on()

    def turn_off(self,station_id:int):
        self.stations[station_id].turn_off()

    def turn_error(self,station_id:int):
        self.stations[station_id].report_error()

    def cancel(self, station_id: int):
        self.stations[station_id].cancel()

    def start(self, station_id: int, tran: Transaction) -> None:
        """开始充电

        Args:
            station_id (str): 充电桩ID
            tran (Transaction): 充电订单
        """
        station = self.stations.get(station_id)
        station.start(tran=tran)

