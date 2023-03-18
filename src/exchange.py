
from balances import Balances
import pandas as pd
import time


class Exchange:
    def __init__(self, test) -> None:

        self.test = test

        self.df = pd.read_parquet('../data/rounds/round_1_augmented.parquet')
        self.start_time = time.time()

        all_currencies = set()

        for column in self.df.columns:
            if column.startswith("close_") and not column.startswith("close_time"):
                pair = column.split("_")[1]
                currency1, currency2 = pair.split(",")

                all_currencies.add(currency1)
                all_currencies.add(currency2)

        self.balances = Balances(all_currencies)

        self.last_volume_update = 0
        self.volume = {}

        # print(all_currencies)

    def setTest(self, test):
        self.test = test

    def regenerateVolume(self):
        self.last_volume_update = self.getTime()

        for column in self.df.columns:
            if column.startswith("volume_"):
                self.volume[column] = self.df[column].iloc[self.last_volume_update]

    def getTime(self):
        return int(time.time() - self.start_time)

    def getAllPairs(self):
        return self.getAllPairsAtTime(self.getTime())

    def getAllVolumes(self):

        time_now = self.getTime()

        if time_now != self.last_volume_update:
            self.regenerateVolume()

        return self.volume

    def getAllPairsAtTime(self, at_time):
        time_now = self.getTime()

        if at_time > time_now:
            raise Exception("Time in future")

        if at_time < 0:
            raise Exception("Time in past")

        out = {}

        for column in self.df.columns:
            if column.startswith("close_") and not column.startswith("close_time"):
                out[column] = self.df[column].iloc[at_time]

        for key, value in self.getAllVolumes().items():
            pair = key.split("_")[1]

            out[pair] = value

        return out

    def createOrders(self, user, secret, orders):
        self.balances.validate(user, secret)

        self.balances.createOrders(
            user, orders, self.getAllPairs(), self.getAllVolumes())

    def register(self, user):
        if not self.test:
            raise Exception("Not in test mode")

        return self.balances.register(user)

    def getBalance(self, user):
        return self.balances.getBalance(user)

    def resetBalance(self, user, secret):
        if not self.test:
            raise Exception("Not in test mode")

        self.balances.resetBalance(user, secret)