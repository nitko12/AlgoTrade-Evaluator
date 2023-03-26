
import unittest
import pandas as pd
import sys

sys.path.append("../src") # noqa: E402

from exchange import Exchange



test_df_path = "test.csv"



class TestVolumeChange(unittest.TestCase):

    def test1(self):

        USDT = 1400000000000 * 10 ** 8

        exchange = Exchange(True, test_df_path)

        secret = exchange.register("nitko")
        exchange.balances.balances["nitko"]["USDT"] = USDT  

        # test USDT,BTC

        print("Testing dry run:")

        exchange.setForcedTime(0)
        pairs = exchange.getAllPairs()
        volume_before_no_buy = pairs["volume_USDT,BTC"] / 10 ** 8

        exchange.setForcedTime(1)
        pairs = exchange.getAllPairs()
        volume_after_no_buy = pairs["volume_USDT,BTC"] / 10 ** 8

        print("volume at 0 normally:", volume_before_no_buy)
        print("volume at 1 normally:", volume_after_no_buy)

        print()

        print("Testing with buy run:")

        exchange = Exchange(True, test_df_path)

        secret = exchange.register("nitko")
        exchange.balances.balances["nitko"]["USDT"] = USDT  

        exchange.setForcedTime(0)
        exchange.createOrders("nitko", secret, f"USDT,BTC,{USDT}")

        print("bought 100000000000 USDT of BTC")

        exchange.setForcedTime(0)
        pairs = exchange.getAllPairs()
        volume_before_after_buy = pairs["volume_USDT,BTC"] / 10 ** 8

        print("volume at 0 after buy:", volume_before_after_buy)

        for x in range(1, 10):

            exchange.setForcedTime(x)
            pairs = exchange.getAllPairs()

            volume_after_after_buy = pairs["volume_USDT,BTC"] / 10 ** 8

            print("volume at", x, "after buy:", volume_after_after_buy)
            print("close at", x, "after buy:", pairs["close_USDT,BTC"])




if __name__ == "__main__":

    unittest.main()