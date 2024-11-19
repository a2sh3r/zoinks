import threading
from zoinks.macros import guards_variable, requires_lock

my_lock = threading.Lock()


class SharedData:
    def __init__(self):
        self.shared_var = 0

    @requires_lock('my_lock')
    def method_that_requires_lock(self):
        print("This method requires a lock.")

    @requires_lock('my_lock')
    @guards_variable('shared_var')
    def increment_shared_var(self):
        self.shared_var += 1


shared_data = SharedData()

with my_lock:
    shared_data.method_that_requires_lock()
    shared_data.increment_shared_var()

shared_data.method_that_requires_lock()  # Warning expected
shared_data.increment_shared_var()  # Warning expected
