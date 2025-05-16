import threading

lock = threading.Lock()

def worker():
    pass

def run():
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()