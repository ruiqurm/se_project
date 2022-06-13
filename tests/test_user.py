from cs_server.user import encode,decode
import time
def test_encode():
    s = encode("hello,world")
    assert  "hello,world" == decode(s)

def test_encode_out_of_time(monkeypatch):
    s = encode("hello,world")
    now = time.time()
    monkeypatch.setattr(time, "time", lambda: now + 3600*25)
    assert decode(s) is None