import threading

class User:
    def __init__(self):
        self.balance = 0

class Account:
    def add_bonus(self, user):
        user.balance += 1

def run():
    user = User()
    acc = Account()
    for _ in range(1000):
        acc.add_bonus(user)