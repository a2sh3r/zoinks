import threading
from zoinks.macros import guards_variable, requires_lock

# Lock for thread safety
my_lock = threading.Lock()

class SharedData:
    def __init__(self):
        self.shared_var = 0

    @requires_lock('my_lock')
    @guards_variable('shared_var')
    def increment_shared_var(self):
        self.shared_var += 1

# Instance of SharedData
shared_data = SharedData()

# Correct call with locking
with my_lock:
    shared_data.increment_shared_var()  # No warnings

# Incorrect call without locking
shared_data.increment_shared_var()  # Warning expected
