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

