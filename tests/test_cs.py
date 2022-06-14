import time
from typing import Dict,Optional
from cs_server.model import BillModel,UserModel, ChargeStationModel, TransactionModel,SqliteDatabase,init
import pytest
from cs_server.charge_station import ChargeStation
from cs_server.user import User
from cs_server.transaction import Transaction, Bill
from cs_server.settings import Settings
class DumbDriver:
	def __init__(self) -> None:
		self.record : Dict[str, Optional[int]] = {
			"mode":None,
			"quantity":None,
			"cancel":None,
			"off":None,
			"on":None,
			"finish":None,
			"error":None
		}
	def update_mode(self, tran,mode)->None:
		self.record["mode"] = tran.id

	def update_quantity(self, tran,value)->None:
		self.record["quantity"] = tran.id

	def signal_station_cancel(self,station)->None:
		self.record["cancel"] = station.id

	def signal_station_off(self,station)->None:
		self.record["off"] = station.id

	def signal_station_on(self,station)->None:
		self.record["on"] = station.id

	def signal_station_finish(self,station)->None:
		self.record["finish"] = station.id

	def signal_station_error(self,station)->None:
		self.record["error"] = station.id

@pytest.fixture
def get_clear_db():
	test_db = SqliteDatabase(':memory:')
	MODELS = [BillModel,UserModel, ChargeStationModel, TransactionModel]
	test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
	test_db.connect()
	test_db.create_tables(MODELS)
	return "ok"
@pytest.fixture
def clear_db():
	init()
	ChargeStationModel.delete().execute()
	UserModel.delete().execute()
	TransactionModel.delete().execute()
	BillModel.delete().execute()
@pytest.fixture
def test_assert_database_is_empty(get_clear_db):
	from cs_server.model import BillModel, UserModel, ChargeStationModel, TransactionModel
	try:
		assert len(list(ChargeStationModel.select())) == 0
		assert len(list(UserModel.select())) == 0
		assert len(list(TransactionModel.select())) == 0
		assert len(list(BillModel.select())) == 0

	except Exception as e:
		print(e)

def test_chargeStation(clear_db):
	import datetime
	driver = DumbDriver()
	Settings.SC_STATION_SPEED = 2*3600 # 1s充完
	Settings.MOCK_DATETIME = False
	cs = ChargeStation.create_station(0,driver)
	assert cs.status == Settings.CHARGE_STATION_STATUS_OFF
	cs.turn_on()
	assert driver.record["on"] == cs.id
	cs.turn_off()
	assert driver.record["off"] == cs.id

	u = User.register("ruiqurm","123456")
	if u is None:
		u = list(UserModel.select())[0]
	t = Transaction.new_transation(u.id,0,datetime.datetime.now(),1) # 0.5s完成
	cs.start(t)
	assert driver.record["finish"] is None
	time.sleep(1)
	assert t.status == Settings.TRAN_STATUS_FINISH
	assert cs.now_tran is None
	assert driver.record["finish"] == cs.id

	# 测试取消
	t = Transaction.new_transation(u.id, 0, datetime.datetime.now(), 1)  # 0.5s完成
	driver.record["finish"] = None
	cs.start(t)
	assert driver.record["finish"] is None
	cs.cancel()
	assert t.status == Settings.TRAN_STATUS_FINISH
	assert cs.now_tran is None
	assert driver.record["finish"] is None
	assert driver.record["cancel"] == cs.id
	time.sleep(1)
	assert driver.record["finish"] is None

	# 测试汇报错误
	t = Transaction.new_transation(u.id, 0, datetime.datetime.now(), 1)  # 0.5s完成
	driver.record["error"] = None
	cs.start(t)
	assert driver.record["finish"] is None
	cs.report_error()
	assert cs.status == Settings.CHARGE_STATION_STATUS_ERR
	assert t.status == Settings.TRAN_STATUS_FINISH
	assert driver.record["error"] == cs.id
	assert cs.now_tran is None


def test_chargeStationMgmt():
	pass

