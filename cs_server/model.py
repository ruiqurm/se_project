"""
需要序列化或者持久化的模型

pydantic作为序列化，反序列化的框架
tortoise作为ORM模型
"""
from tortoise.models import Model
from tortoise import fields


class UserModel(Model):
    """用户信息
	"""
    # Defining `id` field is optional, it will be defined automatically
    # if you haven't done it yourself
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)

    def __str__(self):
        return self.username


class TransactionModel(Model):
    """订单
	"""
    id = fields.IntField(pk=True)
    userid = fields.ForeignKeyField('models.UserModel', related_name='transations')
    mode = fields.IntField()
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    waiting_time = fields.TimeField()  # timedelta
    charge_time = fields.TimeField()  # timedelta
    quantity = fields.FloatField()
    serving_fee = fields.FloatField()  # 服务费
    charging_fee = fields.FloatField()  # 充电费
    station_id = fields.IntField()
    status = fields.IntField()

    def __str__(self):
        return self.id


class BillModel(Model):
    """交易记录
	交易记录也可以合并到上面的订单上。
	或者只保存一个time，然后做外键连接
	"""
    id = fields.IntField(pk=True)
    time = fields.DatetimeField(auto_now_add=True)
    station_id = fields.IntField()
    quantity = fields.FloatField()
    duration = fields.IntField()
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    serving_fee = fields.FloatField()  # 服务费
    charging_fee = fields.FloatField()  # 充电费
    total_fee = fields.FloatField()
    pass


class ChargeStationModel(Model):
    """充电桩的状态
	如 累计充电量，累计充电时间，累计充电费用等等
	"""

    id = fields.CharField(max_length=255, pk=True)
    type = fields.IntField()
    status = fields.IntField()
    charging_power = fields.FloatField()
    cumulative_charging_times = fields.IntField()
    cumulative_charging_duration = fields.IntField()
    cumulative_charging_quantity = fields.FloatField()
    cumulative_charging_fee = fields.FloatField()
    cumulative_serviing_fee = fields.FloatField()
    cumulative_total_fee = fields.FloatField()
    pass
