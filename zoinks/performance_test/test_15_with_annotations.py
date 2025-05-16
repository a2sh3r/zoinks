import threading
from zoinks.macros import guards_variable

global_counter = 0

class Counter:
    @guards_variable("global_counter")
    def inc(self):
        global global_counter
        global_counter += 1

def run():
    c = Counter()
    for _ in range(1000):
        c.inc()