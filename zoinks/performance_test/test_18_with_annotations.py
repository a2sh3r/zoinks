import threading
from zoinks.macros import requires_lock

lock = threading.Lock()

@requires_lock("lock")
def worker():
    pass

def run():
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()