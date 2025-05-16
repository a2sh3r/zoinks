import threading

exclusive_lock_1 = threading.Lock()

lock = threading.Lock()

def critical_section():
    pass

def run():
    lock.acquire()
    critical_section()
    lock.release()

if __name__ == "__main__":
    run()