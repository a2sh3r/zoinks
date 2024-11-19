import threading

from zoinks.macros import requires_lock

exclusive_lock_1 = threading.Lock()

lock = threading.Lock()


@requires_lock('lock')
def critical_section():
    pass


lock.acquire()
critical_section()
lock.release()

# Warning: Function 'critical_section' requires lock 'lock' but is called without it. (Line: 19, Column: 0)
critical_section()
