from threading import Thread, Lock
from secrets import token_hex

BASE = "USDT"


class Balances:

    def __init__(self, all_currencies):
        print("Creating balances")
        self.balances = {}
        self.all_currencies = all_currencies
        self.secrets_to_user = {}

        self.balance_mutex = Lock()

    def register(self, user):

        # print(self.balances)

        if user in self.balances:
            raise Exception("User already registered")

        secret = token_hex(16)
        self.secrets_to_user[secret] = user

        self.balances[user] = {}
        for currency in self.all_currencies:
            self.balances[user][currency] = 0

        self.balances[user][BASE] = 1000

        return secret

    def validate(self, user, secret):
        if user not in self.balances:
            raise Exception("User not registered")

        if secret not in self.secrets_to_user:
            raise Exception("Secret not registered")

        if self.secrets_to_user[secret] != user:
            raise Exception("Secret not for user")

        return True

    def resetBalance(self, user, secret):
        self.validate(user, secret)

        self.balances[user] = {}

        for currency in self.all_currencies:
            self.balances[user][currency] = 0

        self.balances[user][BASE] = 1000

    def getBalance(self, user):

        if user not in self.balances:
            raise Exception("User not registered")

        return self.balances[user]

    def createOrders(self, user, orders, prices, volumes):
        self.balance_mutex.acquire()

        try:
            all_orders = orders.split("|")

            if len(set(all_orders)) != len(all_orders):
                raise Exception("Duplicate orders")

            new_user_balance = self.balances[user].copy()

            for order in all_orders:
                fr, to, amount = order.split(",")

                if len(amount) > 10:
                    raise Exception("Too many decimals")

                amount = float(amount)

                if fr not in new_user_balance:

                    raise Exception(
                        "User does not have currency to buy " + fr + " " + str(new_user_balance))

                if to not in new_user_balance:
                    raise Exception(
                        "User does not have currency to buy " + to + " " + str(new_user_balance))

                if new_user_balance[fr] < amount:
                    raise Exception(
                        "User does not have enough to buy " + to + " " + str(new_user_balance))

                if amount > volumes["volume_" + fr + "," + to]:
                    raise Exception("Not enough volume on " +
                                    fr + "," + to + " " + str(volumes))

                if amount *\
                        prices["close_" + fr + "," + to] < 1e-8:
                    raise Exception("Too small order")

                if amount < 1e-8:
                    raise Exception("Too small order")

                if amount *\
                        prices["close_" + fr + "," + to] > 1e8:
                    raise Exception("Too big order")

                if amount > 1e8:
                    raise Exception("Too big order")

                volumes["volume_" + fr + "," + to] -= amount
                new_user_balance[fr] -= amount
                new_user_balance[to] += amount *\
                    prices["close_" + fr + "," + to]

            self.balances[user] = new_user_balance
        finally:
            self.balance_mutex.release()
