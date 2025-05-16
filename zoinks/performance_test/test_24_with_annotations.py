import threading
from zoinks.macros import guards_variable

shared_list = []

@guards_variable("shared_list")
def append_to_list():
    shared_list.append(1)

def run():
    threads = [threading.Thread(target=append_to_list) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()