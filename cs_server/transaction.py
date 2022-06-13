"""
包括transaction,Bill类
"""
from datetime import datetime, timedelta
from typing import List, Optional, Any
from . import settings
from .model import TransactionModel, BillModel


def less(time1: datetime, time2: datetime):
    return time1.__le__(time2)


def inc(num: int) -> int:
    num += 1
    num %= 7
    return num


periods = [7, 3, 5, 3, 3, 2, 1]
prices = [
    settings.Settings.VALLEY_TIME_CHARGE_UNIT_PRICE,
    settings.Settings.COMMON_TIME_CHARGE_UNIT_PRICE,
    settings.Settings.PEEK_TIME_CHARGE_UNIT_PRICE,
    settings.Settings.COMMON_TIME_CHARGE_UNIT_PRICE,
    settings.Settings.PEEK_TIME_CHARGE_UNIT_PRICE,
    settings.Settings.COMMON_TIME_CHARGE_UNIT_PRICE,
    settings.Settings.VALLEY_TIME_CHARGE_UNIT_PRICE
]


class Transaction:
    def __init__(self, _id: int,
                 userid: int,  #
                 mode: int,  #
                 start_time: datetime,  #
                 end_time: datetime,
                 waiting_time: timedelta,
                 charge_time: timedelta,
                 quantity: float,  #
                 serving_fee: float,
                 charging_fee: float,
                 station_id: int,
                 status: int,  # 事务是否已经完成
                 **kwargs: Any):
        super().__init__(**kwargs)
        self.id = _id
        self.userid = userid
        self.mode = mode
        self.tran_start_time = start_time
        self.end_time = end_time
        self.waiting_time = waiting_time
        self.charge_time = charge_time
        self.quantity = quantity
        self.serving_fee = serving_fee
        self.charging_fee = charging_fee
        self.station_id = station_id
        self.status = status
        self.start_time = datetime.now()
        self.speed = settings.Settings.SC_STATION_SPEED
        self.cancelFlag = False

    def calculate_serving_fee(self) -> float:
        return self.quantity * settings.Settings.SERVICE_UNIT_PRICE

    def calculate_charging_fee(self) -> float:
        fee = 0.0
        idx = 6

        time = datetime(year=self.start_time.year, month=self.start_time.month, day=self.start_time.day, hour=0,
                        minute=0, second=0, microsecond=0)
        while less(time, self.start_time):
            idx = inc(idx)
            time = time + timedelta(hours=periods[idx])

        last_time = self.start_time
        while less(time, self.end_time):
            t = (time - last_time).total_seconds()
            # 秒 * 元/度 * 度/时
            fee += t * prices[idx] * (self.speed / 3600.0)
            last_time = time
            idx = inc(idx)
            time += timedelta(hours=periods[idx])

        t = (self.end_time - last_time).total_seconds()
        fee += t * periods[idx] * (self.speed / 3600.0)
        return fee

    def calculate_end_time(self):
        # 度 / 度/秒
        t = self.quantity / (self.speed / 3600.0)
        time = timedelta(seconds=t)
        self.end_time = self.start_time + time

    def finish(self) -> None:
        """取消充电
		"""
        if self.cancelFlag:
            return
        self.cancelFlag = True

        end_time = datetime.now()
        if less(end_time, self.end_time):
            self.end_time = end_time
            # 秒 * 度/时
            self.quantity = (self.end_time - self.start_time).total_seconds() * (self.speed / 3600.0)

        self.charge_time = self.end_time - self.start_time
        self.serving_fee = self.calculate_serving_fee()
        self.charging_fee = self.calculate_charging_fee()

        #
        bill = Bill.new_bill(
            station_id=self.station_id,
            quantity=self.quantity,
            start_time=self.start_time, end_time=self.end_time,
            serving_fee=self.serving_fee, charging_fee=self.charging_fee,
            total_fee=self.serving_fee + self.charging_fee,
            duration=int(self.charge_time.total_seconds())
        )
        bill.save()
        self.status = settings.Settings.TRAN_STATUS_FINISH
        TransactionModel.filter(id=self.id).update(
            **dict(charge_time=self.charge_time, charging_fee=self.charging_fee, quantity=self.quantity,
                   serving_fee=self.serving_fee, status=self.status, end_time=self.end_time)
        )

    def update_mode(self, mode: int) -> None:
        """更新充电模式
		"""
        self.mode = mode
        if self.mode == settings.Settings.TRAN_CHARGE_MODE_SLOW:
            self.speed = settings.Settings.SC_STATION_SPEED
        else:
            self.speed = settings.Settings.FC_STATION_SPEED
        await TransactionModel.filter(id=self.id).update(**dict(mode=mode))

    def update_quantity(self, quantity: float) -> None:
        """更新充电量
		"""
        self.quantity = quantity
        await TransactionModel.filter(id=self.id).update(**dict(quantity=quantity))

    def start(self, station_id) -> None:
        """开始充电
		"""
        self.station_id = station_id
        self.start_time = datetime.now()
        self.calculate_end_time()
        self.waiting_time = self.start_time - self.tran_start_time
        await TransactionModel.filter(id=self.id).update(
            **dict(station_id=station_id, waiting_time=self.waiting_time, end_time=self.end_time)
        )

    @classmethod
    def get_running_transaction(cls, userid: int) -> Optional['Transaction']:
        """获取正在进行的订单
		"""
        founds = await TransactionModel.filter(userid=userid, status=0).all()
        if len(founds) < 1:
            return None
        found_dict = founds[0].__dict__
        return Transaction(_id=found_dict["id"], userid=found_dict["userid"], mode=found_dict["mode"],
                           start_time=found_dict["start_time"],
                           end_time=found_dict["end_time"], waiting_time=found_dict["waiting_time"],
                           quantity=found_dict["quantity"], station_id=found_dict["station_id"],
                           charge_time=found_dict["charge_time"], serving_fee=found_dict["serving_fee"],
                           charging_fee=found_dict["charging_fee"], status=found_dict["status"])

    @classmethod
    def get_all_transactions(cls, userid: int) -> List['Transaction']:
        """获取所有订单
		"""
        trans_list = []
        founds = await TransactionModel.filter(userid=userid).all()
        for found in founds:
            found_dict = found.__dict__
            trans_list.append(
                Transaction(_id=found_dict["id"], userid=found_dict["userid"], mode=found_dict["mode"],
                            start_time=found_dict["start_time"],
                            end_time=found_dict["end_time"], waiting_time=found_dict["waiting_time"],
                            quantity=found_dict["quantity"], station_id=found_dict["station_id"],
                            charge_time=found_dict["charge_time"], serving_fee=found_dict["serving_fee"],
                            charging_fee=found_dict["charging_fee"], status=found_dict["status"])
            )
        return trans_list

    increment_id = 0

    @classmethod
    def new_transation(cls, userid: int, mode: int, start_time: datetime, quantity: float):
        cls.increment_id += 1
        t = datetime.now() - datetime.now()
        await TransactionModel.create(id=cls.increment_id, userid=userid, mode=mode, start_time=start_time,
                                      end_time=None,
                                      waiting_time=None, charge_time=None, quantity=quantity, serving_fee=0,
                                      charging_fee=0, station_id=0, status=0)
        return Transaction(_id=cls.increment_id, userid=userid, mode=mode, start_time=start_time,
                           end_time=datetime.now(), waiting_time=t, charge_time=t, quantity=quantity, serving_fee=0,
                           charging_fee=0, station_id=0, status=0)


class Bill:
    def __init__(self, _id: int,
                 time: datetime,
                 station_id: int,
                 quantity: float,
                 duration: int,
                 start_time: datetime,
                 end_time: datetime,
                 serving_fee: float,
                 charging_fee: float,
                 total_fee: float):
        self.id = _id
        self.time = time
        self.station_id = station_id
        self.quantity = quantity
        self.duration = duration
        self.start_time = start_time
        self.end_time = end_time
        self.serving_fee = serving_fee
        self.charging_fee = charging_fee
        self.total_fee = total_fee

    def save(self):
        BillModel.create(
            **dict(
                id=self.id, time=self.time, station_id=self.station_id, quantity=self.quantity,
                duration=self.duration, start_time=self.start_time, end_time=self.end_time,
                serving_fee=self.serving_fee, charging_fee=self.charging_fee,
                total_fee=self.total_fee
            )
        )

    @classmethod
    def get_user_bills(cls, userid) -> List['Bill']:
        founds = await BillModel.filter(userid=userid).all()
        bill_list = []
        for found in founds:
            found_dict = found.__dict__
            bill_list.append(Bill(_id=found_dict["id"], time=found_dict["time"], station_id=found_dict["station_id"],
                                  quantity=found_dict["quantity"], duration=found_dict["duration"],
                                  start_time=found_dict["start_time"], end_time=found_dict["end_time"],
                                  serving_fee=found_dict["serving_fee"], charging_fee=found_dict["charging_fee"],
                                  total_fee=found_dict["total_fee"]))
        return bill_list

    increment_id = 0

    @classmethod
    def new_bill(cls, station_id: int, quantity: float, start_time: datetime, end_time: datetime, serving_fee: float,
                 charging_fee: float, total_fee: float, duration: int) -> Optional['Bill']:
        cls.increment_id += 1
        bill = Bill(_id=-cls.increment_id, time=datetime.now(), station_id=station_id,
                    quantity=quantity,
                    start_time=start_time, end_time=end_time,
                    serving_fee=serving_fee, charging_fee=charging_fee,
                    total_fee=total_fee, duration=duration)
        return bill
