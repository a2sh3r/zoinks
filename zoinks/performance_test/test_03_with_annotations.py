import threading
from zoinks.macros import requires_lock, guards_variable

my_lock = threading.Lock()

class SharedData:
    def __init__(self):
        self.shared_var = 0

    @requires_lock("my_lock")
    @guards_variable("shared_var")
    def increment_shared_var(self):
        self.shared_var += 1

def run():
    shared_data = SharedData()
    with my_lock:
        shared_data.increment_shared_var()

if __name__ == "__main__":
    run()