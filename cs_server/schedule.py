"""
调度器
"""
import copy
import datetime

from typing import List

from .settings import Settings,get_number
from .transaction import Transaction
from .charge_station import ChargeStation,StationMgmt
import numpy as np

class Scheduler:
	def __init__(self, sm:StationMgmt):
		self.station_mgmt = sm
		self.areaMngt=AreaMgmt(sm.get_slow_stations(),sm.get_fast_stations())

	def toSchedule(self)->None:
		schedule_list = self.areaMngt.system_schedule()  # [[wait_id,station]..],(int,int)
		vis = []
		if self.areaMngt.error_stationId is not None and self.areaMngt.charging[self.areaMngt.error_stationId].__len__()>0:
			for id,station in schedule_list:
				if station not in vis and self.areaMngt.charging[station].__len__()==0:
					vis.append(station)
					self.station_mgmt.start(station,self.areaMngt.charging[self.areaMngt.error_stationId][id])
			self.areaMngt.from_error_to_charge(schedule_list)
			if self.areaMngt.charging[self.areaMngt.error_stationId].__len__()==0:
				schedule_list=self.areaMngt.system_schedule()
		if self.areaMngt.error_stationId is None or self.areaMngt.charging[self.areaMngt.error_stationId].__len__()==0:
			for wait_id, station in schedule_list:
				if station not in vis and self.areaMngt.charging[station].__len__() == 0:
					vis.append(station)
					self.station_mgmt.start(station, self.areaMngt.waiting[wait_id])
			self.areaMngt.from_wait_to_charge(schedule_list)

	def on_finish(self,station_id:int)->None:
		"""完成充电

		Args:
			station (ChargeStation): 完成充电的充电桩
		"""
		# 不用再调用tran.finish()了，前面会自动调用
		self.areaMngt.finish(station_id)
		if self.areaMngt.charging[station_id].__len__()>0:
			self.station_mgmt.start(station_id,self.areaMngt.charging[station_id][0])
		#调度
		self.toSchedule()



	def on_error(self,station_id:int)->None:
		"""充电桩出现异常,只考虑单一充电桩故障且正好该充电桩有车排队的情况

		Args:
			station (str): 出现异常的充电桩
		"""
		#改充电桩正在充电的tran
		tran=self.areaMngt.charging[station_id][0]#Transaction
		#todo 是否需要生成新的tran，还是修改当前的tran继续使用，以下按修改当前tran做
		#生成bill，Transaction.cancelFlag????
		tran.finish(cancel=False)
		self.areaMngt.error_remake(station_id)
		#调度
		self.toSchedule()


	def on_push(self,user_id,mode:int,quantity:float):
		"""充电事务提交了

		Args:
			tran (Transaction): 提交的事务，内部有用户对象
		"""
		# 如果可以提交
		# 用下面的代码
		print("push ")
		if self.areaMngt.waiting.__len__()>=self.areaMngt.waiting_area_size:
			return "wait area full"
		trans=Transaction.new_transation(user_id,mode,datetime.datetime.now(),quantity)
		self.areaMngt.waiting_add(trans)
		print(trans.station_id)
		#调度
		self.toSchedule()
		return trans.wait_id

	def on_update_mode(self,tran:Transaction,mode:int):
		"""充电订单模式更新模式

		Args:
			tran (Transaction): 充电事务
			mode (int): 模式，这里暂定为int
		"""
		# 调用Transaction.update_mode()
		print("update ")
		area=self.areaMngt.get_trans_area(tran.wait_id)
		if area==-2:
			return "not exist"
		elif area==-1:
			#todo 怎么更新排队号？或者不用跟新排队号
			#my_num=get_number(tran.mode)
			tran.update_mode(mode)
			self.areaMngt.to_waiting_area_end(tran.wait_id)
			return "ok"
		elif area>=0:
			return "not allowed to update"
	def on_update_quantity(self,tran:Transaction,value:float)->str:
		"""充电订单模式更新充电量

		Args:
			tran (Transaction): 充电事务
			value (float): 充电量
		"""
		# 调用Transaction.update_quantity()

		print("update quantity")
		area=self.areaMngt.get_trans_area(tran.wait_id)
		if area==-2:
			return "not exist"
		elif area==-1:
			tran.update_quantity(value)
			return "ok"
		elif area>=0:
			return "not allowed to update"
	def on_cancel(self,tran:Transaction):
		"""充电事务取消

		Args:
			tran (Transaction): 充电事务
		"""
		# 如果这个事务在充电，记得调用充电桩的cancel
		# 这个函数调用以后，在上面的充电桩就会finish，不用调用finish了。
		# 其他情况，需要手动调用tran.finish(cancel=True)
		# self.station_mgmt.cancel(station_id=?)
		area=self.areaMngt.get_trans_area(tran.wait_id)
		if area==-2:
			return "not exist"
		else:
			if area>=0 and self.areaMngt.is_charging(tran.wait_id,area):
				#todo
				#充电桩的cancel还未实现,用finish(cancel=False)
				tran.finish()
				self.areaMngt.finish(area)
				#等待队列有订单，调度
				if self.areaMngt.charging[area].__len__()>0:
					self.station_mgmt.start(area,self.areaMngt.charging[area][0])
			else:
				tran.finish(cancel=True)
				self.areaMngt.leaveoff(area,tran.wait_id)
			#有空位，调度
			self.toSchedule()
			return "ok"


	def on_station_on(self,station_id:int):
		"""充电桩启动

		Args:
			station (ChargeStation): 充电桩
		"""
		pass

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
		self.each_queue_size=Settings.CHARGE_AREA_QUEUE_SIZE+1
		self.waiting_area_size=Settings.WAITING_AREA_SIZE
		self.fc_station_number=Settings.NUMBER_FC_STATION
		self.sc_station_number=Settings.NUMBER_SC_STATION
		self.fc_station_speed=Settings.FC_STATION_SPEED
		self.sc_station_speed=Settings.SC_STATION_SPEED
		self.station_sum=self.fc_station_number+self.sc_station_number
		self.slow_station=slow_stations
		self.fast_station=fast_stations
		self.waiting=[]
		self.charging={}
		for i in self.slow_station:
			self.charging[i]=[]
		for i in self.fast_station:
			self.charging[i]=[]
		self.full_station=[]
		self.waitId2area={}# waiting area:-1, charging:>0, 有序字典(python version>=3.6
		self.schedule_mode=0
		self.error_mode=0
		self.error_stationId=None

	# def system_schedule(self):
	# 	if self.waiting.__len__()>0 and self.full_station.__len__()<self.station_sum:
	# 		trans=self.waiting[0]
	# 		del self.waiting[0]
	# 		waiting_time=None
	# 		now_station=None
	# 		for x,y in self.charging:
	# 			if self.station_mode[x]==trans.mode and self.station_waiting_time[x]<waiting_time:
	# 				waiting_time=self.station_waiting_time[x]
	# 				now_station=x;
	# 		if now_station is not None:
	# 			return now_station
	# 	else:
	# 		return None;

	def get_transaction_id(self):
		pass
	def get_waiting(self,transaction_id):
		pass

	def get_charging(self,station_id):
		# if station_id is None and 0<=station_id<self.each_queue_size:
		# 	#todo
		# 	return [x.user for x in self.charging[station_id]]
		pass

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

	def system_schedule(self):
		schedule_list = []
		if self.error_stationId and self.charging[self.error_stationId].__len__()>0:
			station_all=None
			if self.error_stationId in self.fast_station:
				station_all=copy.copy(self.fast_station)
			else:
				station_all=copy.copy(self.fast_station)
			station_all.pop(station_all.index(self.error_stationId))
			station_to_schedule=[]
			queue_remain_num=[]
			quantity_to_wait=[]
			for i in station_all:
				if self.charging[i].__len__()<self.each_queue_size:
					station_to_schedule.append(i)
					queue_remain_num.append(self.each_queue_size-self.charging[i].__len__())
					now=0
					for j in self.charging[i]:
						now=now+j.get_remain_quantity()
					quantity_to_wait.append(now)
			for i,x in enumerate(self.charging[self.error_stationId]):
				if station_to_schedule.__len__()>0:
					pos=quantity_to_wait.index(min(quantity_to_wait))
					schedule_list.append((i,station_to_schedule[pos]))
					queue_remain_num[pos]-=1
					if queue_remain_num[pos]>0:
						quantity_to_wait[pos]+=x.quantity
					else:
						quantity_to_wait.pop(pos)
						queue_remain_num.pop(pos)
						station_to_schedule.pop(pos)
		else:
			a=[[],[]]
			b=[[],[]]
			c=[[],[]]
			for i,x in self.charging.items():
				if self.error_stationId!=i and x.__len__()<self.each_queue_size:
					mode=1
					if i in self.fast_station:
						mode=0   #0:fast
					a[mode].append(i)
					b[mode].append(self.each_queue_size-x.__len__())
					now=0
					for j in x:
						now=now+j.get_remain_quantity()
					c[mode].append(now)
			for i,x in enumerate(self.waiting):
				mode=x.mode
				if a[mode].__len__()>0:
					pos=c[mode].index(min(c[mode]))
					schedule_list.append((i,a[mode][pos]))
					b[mode][pos]-=1
					if b[mode][pos]>0:
						c[mode][pos]-=x.quantity
					else:
						a[mode].pop(pos)
						b[mode].pop(pos)
						c[mode].pop(pos)
		return schedule_list





	def error_remake(self,error_station_id):
		self.error_stationId=error_station_id
		#时间顺序调度
		if self.error_mode==1:
			station_all=None
			if error_station_id in self.fast_station:
				station_all=copy.copy(self.fast_station)
			else:
				station_all=copy.copy(self.slow_station)

			tran_all=[]
			for i in station_all:
				for j in range(1,self.charging[i].__len__()):
					tran_all.append(self.charging[i][j])
					del self.charging[i][j]
			tran_all.append(self.charging[error_station_id][0])
			del self.charging[error_station_id][0]
			my_order=list(copy.copy(self.waitId2area.keys()))
			self.charging[error_station_id]=sorted(tran_all,key=lambda x:my_order.index(x.wait_id))


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

	def from_wait_to_charge(self, schedule_list):
		for id,stationid in schedule_list:
			self.charging[stationid].append(self.waiting[id])
			self.waitId2area[self.waiting[id].wait_id]=stationid
		now=0
		for id,_ in schedule_list:
			self.waiting.pop(id-now)
			now+=1
	def from_error_to_charge(self, schedule_list):
		for id,station in schedule_list:
			self.charging[station].append(self.charging[self.error_stationId][id])
			self.waitId2area[self.charging[self.error_stationId][id].wait_id]=station
		now=0
		for id,_ in schedule_list:
			self.charging[self.error_stationId].pop(id-now)
			now+=1
	def get_trans_area(self, wait_id):
		if self.waitId2area.__contains__(wait_id):
			return self.waitId2area[wait_id]
		else:
			return -2

	def is_charging(self, wait_id, area):
		if self.charging[area].__len__()>0 and self.charging[area][0].wait_id==wait_id:
			return True
		else:
			return False

	def to_waiting_area_end(self, wait_id):
		pos=None
		for i,x in enumerate(self.waiting):
			if x.wait_id==wait_id:
				pos=i
				break
		if pos:
			tran=self.waiting[pos]
			self.waiting.pop(pos)
			self.waiting.append(tran)

	def leaveoff(self, area, wait_id):
		if area==-1:
			pos=None
			for i,x in enumerate(self.waiting):
				if x.wait_id==wait_id:
					pos=i
					break
			if pos:
				wait_id=self.waiting[pos].wait_id
				self.waitId2area.pop(wait_id)
				self.waiting.pop(pos)
		else:
			pos=None
			for i,x in enumerate(self.charging[area]):
				if x.wait_id==wait_id:
					pos=i
					break
			if pos:
				wait_id=self.charging[area][pos].wait_id
				self.waitId2area.pop(wait_id)
				self.charging[area].pop(pos)

	def waiting_add(self, trans):
		self.waiting.append(trans)
		self.waitId2area[trans.wait_id]=-1

	def finish(self, station_id):
		wait_id=self.charging[station_id][0].wait_id
		self.waitId2area.pop(wait_id)
		self.charging[station_id].pop(0)




