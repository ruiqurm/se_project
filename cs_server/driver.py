"""
全局的调度器
"""
from .charge_station import ChargeStation
from .transaction import Transaction
from .schedule import Scheduler
import asyncio
import threading
class Driver:
	def __init__(self,sche:Scheduler) -> None:
		self.scheduler = sche

	def update_mode(self, tran:Transaction,mode)->None:
		self.scheduler.on_update_mode(tran,mode)

	def update_quantity(self, tran:Transaction,value)->None:
		self.scheduler.on_update_mode(tran,value)

	def cancel(self,tran:Transaction)->None:
		self.scheduler.on_cancel(tran)

	def signal_station_off(self,station:ChargeStation)->None:
		# asyncio.create_task(self.scheduler.on_station_off())
		t = threading.Thread(target=self.scheduler.on_station_off, args=(station.id,))
		t.start()

	def signal_station_on(self,station:ChargeStation)->None:
		# asyncio.create_task(self.scheduler.on_station_on())
		t = threading.Thread(target=self.scheduler.on_station_on, args=(station.id,))
		t.start()

	def signal_station_finish(self,station:ChargeStation)->None:
		# asyncio.create_task(self.scheduler.on_station_on())
		t = threading.Thread(target=self.scheduler.on_finish, args=(station.id,))
		t.start()

	def signal_station_error(self,station:ChargeStation)->None:
		# asyncio.create_task(self.scheduler.on_station_on())
		t = threading.Thread(target=self.scheduler.on_error, args=(station.id,))
		t.start()		