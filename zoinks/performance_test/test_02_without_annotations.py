import threading

my_lock = threading.Lock()
shared_var = 0

def print_shared_var():
    global shared_var
    print(f"Current value of shared_var: {shared_var}")

def run():
    print_shared_var()
    with my_lock:
        print_shared_var()
    my_lock.acquire()
    try:
        print_shared_var()
    finally:
        my_lock.release()

if __name__ == "__main__":
    run()