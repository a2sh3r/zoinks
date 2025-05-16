import threading

from zoinks.macros import requires_lock

lock_x = threading.Lock()
lock_y = threading.Lock()

start_event = threading.Event()

@requires_lock("lock_x")
@requires_lock("lock_y")
def update_with_xy():
    start_event.wait()
    with lock_x:
        print("Thread 1 has lock_x")
        with lock_y:
            print("Thread 1 has lock_y")

@requires_lock("lock_y")
@requires_lock("lock_x")
def update_with_yx():
    start_event.wait()
    with lock_y:
        print("Thread 2 has lock_y")
        with lock_x:
            print("Thread 2 has lock_x")

t1 = threading.Thread(target=update_with_xy)
t2 = threading.Thread(target=update_with_yx)

t1.start()
t2.start()


start_event.set()
йййййй
t1.join()
t2.join()