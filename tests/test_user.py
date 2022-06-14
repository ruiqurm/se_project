import asyncio

from cs_server.user import encode,decode,User
import time
import pytest


def test_encode():
    s = encode("hello,world")
    assert  "hello,world" == decode(s)

def test_encode_out_of_time(monkeypatch):
    s = encode("hello,world")
    now = time.time()
    monkeypatch.setattr(time, "time", lambda: now + 3600*25)
    assert decode(s) is None
from tortoise.contrib.test import finalizer, initializer
import os
@pytest.fixture(scope="session", autouse=True)
def initialize_tests(request):
    initializer(["cs_server.model"], db_url="sqlite://:memory:")
    request.addfinalizer(finalizer)

def test_User():
    async def t():
        u2 = await User.register("sadas","asdasd")
        print("ok")
    asyncio.run(t())
    # assert u.id == u2.id