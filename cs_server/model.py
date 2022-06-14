"""
需要序列化或者持久化的模型

pydantic作为序列化，反序列化的框架
tortoise作为ORM模型
"""
from datetime import timedelta
import datetime

# from tortoise.models import Model
# from tortoise import fields
#
# from tortoise import Tortoise, run_async
from typing import Optional

from peewee import *

# async def init():
#     # Here we create a SQLite DB using file "db.sqlite3"
#     #  also specify the app name of "models"
#     #  which contain models from "app.models"
#     await Tortoise.init(
#         db_url='sqlite://db.sqlite3',
#         modules={'models': ['cs_server.model']}
#     )
#     # Generate the schema
#     await Tortoise.generate_schemas()
#
db = SqliteDatabase('db.sqlite3')


class TimeDeltaField(IntegerField):
    def db_value(self, duration:Optional[timedelta]):
        """
        Python -> DataBase
        """
        if isinstance(duration, timedelta):
            return super().adapt(duration.total_seconds())  # call
        elif duration is None:
            return None
        raise TypeError("Wrong type, must be timedelta")


    def python_value(self, db_val):
        """
        DataBase -> Python
        """
        if db_val is None:
            return None
        return timedelta(seconds=db_val)

class UserModel(Model):
    """用户信息
	"""
    # Defining `id` field is optional, it will be defined automatically
    # if you haven't done it yourself
    username = CharField(max_length=255)
    password = CharField(max_length=255)

    def __str__(self):
        return self.username
    class Meta:
        database = db

class TransactionModel(Model):
    """订单
	"""
    user = ForeignKeyField(UserModel, backref='transations',null=True)
    mode = IntegerField()
    start_time = DateTimeField()
    end_time = DateTimeField(null=True)
    waiting_time = TimeDeltaField(null=True)  # timedelta
    charge_time = TimeDeltaField(null=True)  # timedelta
    quantity = FloatField()
    serving_fee = FloatField(null=True)  # 服务费
    charging_fee = FloatField(null=True)  # 充电费
    station_id = IntegerField(null=True)
    status = IntegerField()

    def __str__(self):
        return self.id
    class Meta:
        database = db

class BillModel(Model):
    """交易记录
	交易记录也可以合并到上面的订单上。
	或者只保存一个time，然后做外键连接
	"""
    time = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(UserModel, backref='bill')
    station_id = IntegerField()
    quantity = FloatField()
    duration = TimeDeltaField()
    start_time = DateTimeField()
    end_time = DateTimeField()
    serving_fee = FloatField()  # 服务费
    charging_fee = FloatField()  # 充电费
    total_fee = FloatField()
    class Meta:
        database = db

class ChargeStationModel(Model):
    """充电桩的状态
	如 累计充电量，累计充电时间，累计充电费用等等
	"""
    type = IntegerField()
    status = IntegerField()
    charging_power = FloatField()
    cumulative_charging_times = IntegerField()
    cumulative_charging_duration = TimeDeltaField()
    cumulative_charging_quantity = FloatField()
    cumulative_charging_fee = FloatField()
    cumulative_serviing_fee = FloatField()
    cumulative_total_fee = FloatField()
    class Meta:
        database = db
def init():
    db.create_tables([UserModel, ChargeStationModel,TransactionModel,BillModel])
# from functools import wraps
# def sync_wrapper(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         return run_async(f(*args,**kwargs))
#     return decorated

# run_async(init())