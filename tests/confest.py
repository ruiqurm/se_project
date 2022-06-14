from cs_server.model import UserModel,ChargeStationModel,TransactionModel,BillModel
import pytest
from peewee import SqliteDatabase
@pytest.fixture(scope="function", autouse=True)
def execute_before_any_test():
    test_db = SqliteDatabase(':memory:')
    MODELS = [UserModel,ChargeStationModel,TransactionModel,BillModel]
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables(MODELS)