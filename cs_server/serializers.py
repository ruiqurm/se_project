"""
序列化器

把模型转成json格式

这一部分应该只有web部分需要用到
下面列举了一下可能需要序列化的类
"""
import pydantic


class StationStatus(pydantic.BaseModel):
	pass

class Transaction():
	pass

class User(pydantic.BaseModel):
	username : str
	password : str

class Bill():
	pass