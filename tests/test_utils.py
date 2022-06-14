import datetime
import time
import pytest
from cs_server.model import BillModel,UserModel, ChargeStationModel, TransactionModel,SqliteDatabase,init
import pytest
from cs_server.settings import Settings,now,real_time,START_DATETIME
def test_time():
    Settings.MOCK_DATETIME = False
    t1 = now()
    time.sleep(0.5)
    t2 = now()
    assert (t2 - t1).total_seconds() > 0.5
    assert (t2 - t1).total_seconds() < 0.75

    assert real_time(t2,t1).total_seconds() > 0.5
    assert real_time(t2,t1).total_seconds() < 0.75

    Settings.MOCK_DATETIME = True
    Settings.TIME_FLOW_RATE = 5
    t1 = now()
    time.sleep(0.5)
    t2 = now() # should be +2.5
    assert (t2 - t1).total_seconds() > 2.5
    assert (t2 - t1).total_seconds() < 2.6
    assert t2.hour == Settings.START_TIME.hour
    assert t2.minute == Settings.START_TIME.minute

    assert real_time(t2,t1).total_seconds() > 0.5
    assert real_time(t2,t1).total_seconds() < 0.6

    # higher rate
    Settings.TIME_FLOW_RATE = 30
    t1 = now()
    time.sleep(0.5)
    t2 = now()  # should be +2.5
    assert (t2 - t1).total_seconds() > 15
    assert (t2 - t1).total_seconds() < 16
    assert t2.hour == Settings.START_TIME.hour
    assert t2.minute == Settings.START_TIME.minute

    assert real_time(t2, t1).total_seconds() > 0.5
    assert real_time(t2, t1).total_seconds() < 0.6


def test_higher():
    Settings.MOCK_DATETIME = True
    Settings.TIME_FLOW_RATE = 60
    for i in range(20):
        t1 = now()
        time.sleep(0.5)
        t2 = now()  # should be +2.5
        assert (t2 - t1).total_seconds() > 30
        assert (t2 - t1).total_seconds() < 31

        assert real_time(t2, t1).total_seconds() > 0.5
        assert real_time(t2, t1).total_seconds() < 0.6


