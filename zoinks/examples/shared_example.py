from zoinks.macros import shared_variable

import threading

lock = threading.Lock()
counter = 0

@shared_variable('shared_var')
def update_shared_var():
    with lock:
        shared_var = 100