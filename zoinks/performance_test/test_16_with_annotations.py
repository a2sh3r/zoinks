import threading
from zoinks.macros import guards_variable

counter = 0
total = 0

class Stats:
    @guards_variable("counter")
    @guards_variable("total")
    def update(self):
        global counter, total
        counter += 1
        total += 1

def run():
    s = Stats()
    for _ in range(1000):
        s.update()