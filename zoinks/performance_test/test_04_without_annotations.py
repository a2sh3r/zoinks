import threading

lock = threading.Lock()

def critical_section():
    pass

def run():
    lock.acquire()
    critical_section()
    lock.release()
    critical_section()

run()