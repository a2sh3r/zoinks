import threading

counter = 0
total = 0

class Stats:
    def update(self):
        global counter, total
        counter += 1
        total += 1

def run():
    s = Stats()
    for _ in range(1000):
        s.update()