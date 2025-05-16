import threading
from zoinks.macros import guards_variable

shared_var = 0

@guards_variable("shared_var")
def update_var():
    global shared_var
    shared_var += 1

def run():
    for _ in range(1000):
        update_var()