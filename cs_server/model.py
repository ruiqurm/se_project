"""
需要序列化或者持久化的模型

pydantic作为序列化，反序列化的框架
tortoise作为ORM模型
"""
import tortoise
from tortoise.models import Model
from tortoise import fields

class UserModel(Model):
	"""用户信息
	"""
	# Defining `id` field is optional, it will be defined automatically
	# if you haven't done it yourself
	username = fields.CharField(max_length=255)
	password = fields.CharField(max_length=255)
	def __str__(self):
		return self.username

class TransactionModel(Model):
	"""订单
	"""
	# user = fields.ForeignKeyField('models.UserModel', related_name='transactions')
	# charge_type = fields.CharField(max_length=16)
	pass

class BillModel(Model):
	"""交易记录
	交易记录也可以合并到上面的订单上。
	或者只保存一个time，然后做外键连接
	"""
	# time = fields.DatetimeField(auto_now_add=True)
	pass

class ChargeStationModel(Model):
	"""充电桩的状态
	如 累计充电量，累计充电时间，累计充电费用等等
	"""
	pass