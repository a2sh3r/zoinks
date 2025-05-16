import threading
import time

lock_a = threading.Lock()
lock_b = threading.Lock()

start_event = threading.Event()


class SharedCounter:
    def __init__(self):
        self.count = 0

    def deadlock_method(self):
        start_event.wait()
        with lock_a:
            print("SharedCounter has lock_a")
            with lock_b:
                print("SharedCounter has lock_b")
                self.count += 1


class AnotherClass:
    def reverse_deadlock(self):
        start_event.wait()
        with lock_b:
            print("AnotherClass has lock_b")
            with lock_a:
                print("AnotherClass has lock_a")


counter = SharedCounter()
another = AnotherClass()

t1 = threading.Thread(target=counter.deadlock_method)
t2 = threading.Thread(target=another.reverse_deadlock)

t1.start()
t2.start()

print("Waiting for threads to finish...")

time.sleep(0.1)

start_event.set()

t1.join()
t2.join()

print("Threads finished.")