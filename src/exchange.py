
from pprint import pprint
from balances import Balances
import pandas as pd
import time


class Exchange:
    def __init__(self, test, path="../data/data2.csv") -> None:

        self.test = test

        self.df = pd.read_csv(path)

        for column in self.df.columns:
            if column.startswith("close_") or column.startswith("volume_") or column == "time":
                self.df[column] = self.df[column].astype(int)
            else:
                assert False, "Unknown column " + column

        self.start_time = time.time()

        all_currencies = set()

        for column in self.df.columns:
            if column.startswith("close_"):
                pair = column.split("_")[1]
                currency1, currency2 = pair.split(",")

                all_currencies.add(currency1)
                all_currencies.add(currency2)

        self.balances = Balances(all_currencies)

        self.last_volume_update = -1
        self.volume = {}
        self.initial_volume = {}

        # print(all_currencies)

    def setTest(self, test):
        self.test = test

    def regenerateVolume(self):
        self.last_volume_update = self.getTime()

        self.initial_volume = self.volume.copy()

        for column in self.df.columns:
            if column.startswith("volume_"):

                # za test
                # if column in self.initial_volume:

                #     used = self.volume[column] / \
                #         self.initial_volume[column]

                #     new = (1 * 0.3 + used * 0.7)

                #     self.volume[column] = int(new *
                #                               self.df[column].iloc[self.last_volume_update])

                # else:
                #       self.volume[column] = self.df[column].iloc[self.last_volume_update]
                self.volume[column] = self.df[column].iloc[self.last_volume_update]

    def getTime(self):

        # za majin sanity
        # return int(time.time() - self.start_time)

        return 0

    def getAllPairs(self):

        return self.getAllPairsAtTime(self.getTime())

    def getAllVolumes(self):

        time_now = self.getTime()

        if time_now != self.last_volume_update:
            self.regenerateVolume()

        # za Majin sanity
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
                out[column] = int(self.df[column].iloc[at_time])

        # print(self.getAllVolumes().items())

        for key, value in self.getAllVolumes().items():
            pair = key.split("_")[1]

            out["volume_" + pair] = int(value)

        # for key, value in out.items():
        #     assert isinstance(value, int), "Value " + \
        #         str(value) + " is not int for key " + key

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
