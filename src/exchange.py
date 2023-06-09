
import math
from pprint import pprint
from balances import Balances
import pandas as pd
import time

DAMPING_FACTOR = 1.1

class Exchange:
    def __init__(self, test, path="../data/round1.csv") -> None:

        self.test = test
        self.forced_time = None

        self.df = pd.read_csv(path)

        # self.df.to_csv("test_hash.csv", index=False)


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
        self.original_volume = {}

        # print(all_currencies)

    def getOriginalVolume(self):
        return self.original_volume
    
    def setOriginalVolume(self, volume):
        self.original_volume = volume

    def setTest(self, test):
        self.test = test

    def setForcedTime(self, to_time):
        self.forced_time = to_time

    def regenerateVolume(self):
        self.last_volume_update = self.getTime()

        new_volume = {}
        new_original_volume = {}
        new_this_tick_volume = {}

        original_volume = self.getOriginalVolume()

        for column in self.df.columns:
            if column.startswith("volume_"):

                # za test
                if column in original_volume:
                    # print(self.volume[column] ,"a", original_volume[column])

                    if original_volume[column] == 0:
                        old_remaining = 1
                    else:
                        old_remaining = self.volume[column] / original_volume[column]

                    # volume

                    new_real = self.df[column].iloc[self.last_volume_update]

                    factor = old_remaining * DAMPING_FACTOR
                    factor = min(max(0, factor), 1)

                    new_volume[column] = factor * new_real
                    new_original_volume[column] = new_real
                    new_this_tick_volume[column] = factor * new_real

                else:
                      
                    new_volume[column] = self.df[column].iloc[self.last_volume_update]
                    new_original_volume[column] = self.df[column].iloc[self.last_volume_update]
                    new_this_tick_volume[column] = self.df[column].iloc[self.last_volume_update]

                # self.volume[column] = self.df[column].iloc[self.last_volume_update]

        self.volume = new_volume
        self.setOriginalVolume(new_original_volume)

    def getTime(self):

        if self.forced_time is not None:
            return self.forced_time

        # za majin sanity
        return int(time.time() - self.start_time) // 30

        # return 0

    def getAllPairs(self):

        return self.getAllPairsAtTime(self.getTime(), include_volume=True)

    def getAllVolumes(self):

        time_now = self.getTime()

        if time_now != self.last_volume_update:
            self.regenerateVolume()

        # za Majin sanity
        # self.regenerateVolume()

        return self.volume

    def getAllPairsAtTime(self, at_time, include_volume=False):
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

        if include_volume:
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
        return self.balances.register(user)

    def getBalance(self, user):
        return self.balances.getBalance(user)

    def resetBalance(self, user, secret):
        if not self.test:
            raise Exception("Not in test mode")

        self.balances.resetBalance(user, secret)

    def getAllBalances(self):
        return self.balances.getAllBalances()