"""
测试 测试的函数
"""
import time

def foo():
    return time.time()

def test_mocktime(monkeypatch):
    now = foo()

    monkeypatch.setattr(time, "time", lambda :now+3600)
    assert foo() - now == 3600

