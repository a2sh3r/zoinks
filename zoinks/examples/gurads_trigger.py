import threading
from zoinks.macros import requires_lock, guards_variable

my_lock = threading.Lock()
shared_var = 0  # Shared variable defined outside of any function

@requires_lock('my_lock')
@guards_variable('shared_var')  # Indicating that shared_var needs protection
def increment_shared_var():
    global shared_var
    # Accessing shared_var without acquiring the lock
    print(f"Current value of shared_var: {shared_var}")  # This should trigger a warning

# Simulate concurrent execution
threads = []
for _ in range(5):
    t = threading.Thread(target=increment_shared_var)
    threads.append(t)
    t.start()

for t in threads:
    t.join()