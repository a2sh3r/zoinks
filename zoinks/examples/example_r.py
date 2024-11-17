import threading

from zoinks.macros import requires_lock

lock = threading.Lock()
exclusive_lock_1 = threading.Lock()


@requires_lock('lock')
def critical_section():
    # "with lock:" is required
    pass

