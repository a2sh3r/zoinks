import threading
from zoinks.macros import requires_lock

lock = threading.Lock()

@requires_lock("lock")
def critical_section():
    pass

def run():
    lock.acquire()
    critical_section()
    lock.release()
    critical_section()  # Должен быть warning

run()