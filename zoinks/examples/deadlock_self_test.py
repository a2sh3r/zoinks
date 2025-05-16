import threading

lock = threading.Lock()

def func():
    lock.acquire()
    print("First lock acquired")
    lock.acquire()
    print("Second lock acquired")
    lock.release()
    lock.release()

t = threading.Thread(target=func)
t.start()
t.join()