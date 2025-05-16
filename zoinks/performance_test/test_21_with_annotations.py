import threading
from zoinks.macros import requires_lock

lock = threading.Lock()

@requires_lock("lock")
def secured_function():
    pass

def run():
    for _ in range(1000):
        secured_function()