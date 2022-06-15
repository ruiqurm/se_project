"""
调度器
"""
import datetime

from typing import List

from .settings import Settings
from .transaction import Transaction
from .charge_station import ChargeStation,StationMgmt
import numpy as np

class Scheduler:
	def __init__(self, sm:StationMgmt):
		self.station_mgmt = sm
		self.areaMngt=AreaMgmt(sm.get_slow_stations(),sm.get_fast_stations())
	def on_finish(self,station_id:int)->None:
		"""完成充电

		Args:
			station (ChargeStation): 完成充电的充电桩
		"""
		# 不用再调用tran.finish()了，前面会自动调用
		#完成充电
		self.areaMngt.finish(station_id)
		#为充电桩调度
		if self.areaMngt.simple_schedule(station_id)==0:
			return 0
		#开始为调度到最开始的事务充电
		Transaction.start(station_id)
		return 1

	def on_error(self,station_id:int)->None:
		"""充电桩出现异常

		Args:
			station (str): 出现异常的充电桩
		"""
		stationId = station_id
		#获取充电队列
		charging_queue=self.areaMgmt.charging[stationId]
		#
		for i in charging_queue:
			#为他们生成详单,并加入优先调度队列
			Transaction.finish(i)
			self.priority_queue.append(i)
		#锁定等待区
		AreaMgmt.lock_waitingArea()
		#调度事件

	def on_push(self,user_id,mode:int,quantity:float):
		"""充电事务提交了

		Args:
			tran (Transaction): 提交的事务，内部有用户对象
		"""
		# 如果可以提交
		# 用下面的代码
		Transaction.new_transation(user_id,mode,datetime.datetime.now(),quantity)
		raise
		ret=AreaMgmt.push(userId,model,charging)
		return ret
	def on_update_mode(self,tran:Transaction,mode:int):
		"""充电订单模式更新模式

		Args:
			tran (Transaction): 充电事务
			mode (int): 模式，这里暂定为int
		"""
		# 调用Transaction.update_mode()
		raise
		ret=AreaMgmt.update_mode(uid,mode)
		pass
	def on_update_quantity(self,tran:Transaction,value:float):
		"""充电订单模式更新充电量

		Args:
			tran (Transaction): 充电事务
			value (float): 充电量
		"""
		# 调用Transaction.update_quantity()
		raise
		# ret=AreaMgmt.update_quantity(uid,value)
		pass
	def on_cancel(self,tran:Transaction):
		"""充电事务取消

		Args:
			tran (Transaction): 充电事务
		"""
		# 如果这个事务在充电，记得调用充电桩的cancel
		# 这个函数调用以后，在上面的充电桩就会finish，不用调用finish了。
		# 其他情况，需要手动调用tran.finish(cancel=True)
		# self.station_mgmt.cancel(station_id=?)
		pass

	def on_station_on(self,station_id:int):
		"""充电桩启动

		Args:
			station (ChargeStation): 充电桩
		"""
		raise

	def on_station_off(self,station_id:int):
		"""充电桩关闭

		Args:
			station (str): 充电桩
		"""
		pass


class AreaMgmt:
	def __init__(self, slow_stations: List[int],fast_stations:List[int]):
		# slow_stations 慢充电桩id列表
		# fast_stations 快充电桩id列表
		raise
		self.each_queue_size=Settings.CHARGE_AREA_QUEUE_SIZE
		self.waiting_area_size=Settings.WAITING_AREA_SIZE
		self.fc_station_number=Settings.NUMBER_FC_STATION
		self.sc_station_number=Settings.NUMBER_SC_STATION
		self.fc_station_speed=Settings.FC_STATION_SPEED
		self.sc_station_speed=Settings.SC_STATION_SPEED
		self.station_sum=self.fc_station_number+self.sc_station_number
		self.waiting=[]
		self.charging=[[] for i in range(self.station_sum)]
		self.uid2transaction={}
		self.schedule_mode=0
		self.error_mode=0
		self.lock=0
		self.error_queue_id=None

	def get_transaction_id(self):
		pass
	def get_waiting(self,transaction_id):
		pass

	def get_charging(self,station_id):
		if station_id is None and 0<=station_id<self.each_queue_size:
			#todo
			return [x.user for x in self.charging[station_id]]

	def push(self,uid,mode,value):
		#超过等待区上限
		if len(self.waiting)>=self.waiting_area_size:
			return 0
		# 取不到号，todo
		charging_id=None#取号，todo
		#transaction_id=self.get_transaction_id()
		#参数 todo
		tmp=Transaction(uid,charging_id,mode,value,area='waiting')
		self.uid2transaction[uid]=tmp
		self.waiting.append(tmp)
		return 1
	def update_quantity(self,uid,value):
		if self.uid2transaction[uid] is None:
			return -1
		elif self.uid2transaction[uid].area=='waiting':
			self.uid2transaction[uid].update(value)
			return 1
		else:
			#在充电区，用户要充电需要取消充电，重新提交申请
			return 0
	def update_mode(self,uid,mode):
		if self.uid2transaction[uid] is not None:
			return -1
		elif self.uid2transaction[uid].area=='waiting':
			tmp=None
			for i in range(len(self.waiting)):
				if self.waiting[i].user==uid:
					tmp=self.waiting[i]
					del self.waiting[i]
					break
			if tmp:
				id=None #取号 todo
				tmp.id=id
				self.waiting.append(tmp)
				return 1
		else:
			# 在充电区，删除事务，用户要充电需要取消充电，重新提交申请
			return 0

	def cancel(self,uid):
		if self.uid2transaction[uid] is None:
			return -1
		elif self.uid2transaction[uid].area=='waiting':
			for i in range(len(self.waiting)):
				if(self.waiting[i].user==uid):
					del self.waiting[i]
					break
			del self.uid2transaction[uid]
			return 1
		else:
			station_id=self.uid2transaction[uid].station_id
			for i in range(len(self.charging[station_id])):
				if self.charging[station_id][i].user==uid:
					del self.charging[station_id][i]
					break
			del self.uid2transaction[uid]
			return 1

	def finish(self,station_id):
		pass
		# self.charging[station_id].pop(0)
	def try_unlock(self):
		if len(self.charging[self.error_queue_id])==0:
			self.lock=0
			self.error_queue_id=None
			self.single_best_schedule()
			return 1
		return 0
	def get_mode(self,station_id):
		#todo
		if station_id<self.fc_station_number:
			return 'F'
		else:
			return 'S'
	def get_insert_pos(self,arr,value):
		#arr有序，二分查找插入位置
		l,r=0,len(arr)
		mid=None
		pos=None
		while l<=r:
			mid=(l+r)/2
			if(arr[mid].quantity<value):
				l=mid+1
			else:
				pos=mid
				r=mid-1
		return pos
	def simple_schedule(self,station_id):
		#station_id充电桩有空位
		mode=self.get_mode(station_id)
		selected_i=None
		if self.lock:
			#找到出错队列的第一个对应模式的用户
			for i in range(len(self.charging[self.error_queue_id])):
				if self.charging[self.error_queue_id].mode==mode:
					selected_i=i
					break
			if selected_i is None:
				return 0
			pos=self.get_insert_pos(self.charging[station_id],self.charging[self.error_queue_id][selected_i].quantity)
			self.charging[station_id].insert(pos,self.charging[self.error_queue_id][selected_i])
			del self.charging[self.error_queue_id][selected_i]
			self.try_unlock()
			return 1
		else:
			#找到等待区第一个对应充电模式的用户
			for i in range(len(self.waiting)):
				if self.waiting[i].mode==mode:
					selected_i=i
					break
			if selected_i is None:
				return 0
			#二分查找最佳插入位置
			pos=self.get_insert_pos(self.charging[station_id],self.waiting[selected_i].quantity)
			self.charging[station_id].insert(pos,self.waiting[selected_i])
			del self.waiting[selected_i]
			return 1

	def error_remake(self,error_station_id):
		self.error_queue_id=error_station_id
		self.lock=1
		#时间顺序调度
		if self.error_mode==1:
			mode=self.get_mode(error_station_id)
			tmp=[]
			for i,x in enumerate(self.charging):
				if self.get_mode(i)==mode:
					tmp.extend(x)
					self.charging[i]=[]
			tmp.sort(key=lambda x:x.id)
			station_num=None
			if mode=='F':
				station_num=self.fc_station_number
			else:
				station_num=self.sc_station_number
			station_num-=1
			be=station_num*self.each_queue_size
			self.charging[self.error_queue_id]=tmp[be:]
			tmp=np.array(tmp[:be]).reshape((-1,station_num)).T.tolist()
			for i in range(len(self.charging)):
				if self.get_mode(i)==mode and self.error_queue_id!=i:
					self.charging[i]=tmp[0]
					del tmp[0]


	def single_best_schedule(self):
		pass

	def batch_best_scheduel(self,user_list):
		user_list.sort(key=lambda x:x.value)
		self.waiting=user_list[self.station_sum*self.each_queue_size:]
		pos_weight=[]
		for i in range(self.station_sum):
			speed=None
			if self.get_mode(i)=='F':
				speed=self.fc_station_speed
			else:
				speed=self.sc_station_speed
			for j in range(self.each_queue_size):
				pos_weight.append([i,j,speed*(self.each_queue_size-j)])
		pos_weight.sort(key=lambda x:x[2],reverse=1)
		for now,x in enumerate(user_list):
			i,j=pos_weight[now][0],pos_weight[now][1]
			#参数 todo
			self.charging[i][j]=Transaction(user=x[0],value=x[1])




	def is_available(self):
		pass
	def lock(self):
		pass
	def size(self):
		pass