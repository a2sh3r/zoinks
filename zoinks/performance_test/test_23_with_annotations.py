import threading
from zoinks.macros import requires_lock

lock = threading.Lock()

@requires_lock("lock")
def dangerous_call():
    pass

def run():
    for _ in range(1000):
        dangerous_call()