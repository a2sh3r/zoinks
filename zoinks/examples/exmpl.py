import threading

from zoinks.macros import requires_lock, guards_variable

my_lock = threading.Lock()
shared_var = 0


@requires_lock('my_lock')
@guards_variable('shared_var')
def example_function():
    # 'shared_var' protection is required
    shared_var = 10
    print(shared_var)


my_lock.acquire()
example_function()
my_lock.release()
