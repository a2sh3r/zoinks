import threading

my_lock = threading.Lock()

class SharedData:
    def __init__(self):
        self.shared_var = 0

    def print_shared_var(self):
        print(f"Current value of shared_var in class: {self.shared_var}")

def run():
    shared_data = SharedData()
    shared_data.print_shared_var()
    with my_lock:
        shared_data.print_shared_var()
    my_lock.acquire()
    try:
        shared_data.print_shared_var()
    finally:
        my_lock.release()

if __name__ == "__main__":
    run()