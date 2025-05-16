import threading

global_counter = 0

class Counter:
    def inc(self):
        global global_counter
        global_counter += 1

def run():
    c = Counter()
    for _ in range(1000):
        c.inc()