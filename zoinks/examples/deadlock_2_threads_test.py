import threading

from zoinks.macros import requires_lock, guards_variable

@requires_lock("lock1")
@requires_lock("lock2")
def thread1():
    lock1.acquire()
    lock2.acquire()
    lock2.release()
    lock1.release()

@requires_lock("lock2")
@requires_lock("lock1")
def thread2():
    lock2.acquire()
    lock1.acquire()
    lock1.release()
    lock2.release()

lock1 = threading.Lock()
lock2 = threading.Lock()

t1 = threading.Thread(target=thread1)
t2 = threading.Thread(target=thread2)

t1.start()
t2.start()

t1.join()
t2.join()