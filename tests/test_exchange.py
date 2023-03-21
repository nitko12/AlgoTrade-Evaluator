
from unittest import TestCase, main
import sys
from pprint import pprint
sys.path.append("../src")


from exchange import Exchange  # noqa: E402


# {'close_BTC,ETH': 7508500,
#  'close_BTC,USDT': 1723629000000,
#  'close_ETH,USDT': 129588000000,
#  'close_USDT,BTC': 1713334999999,
#  'volume_BTC,ETH': 5087836849,
#  'volume_BTC,USDT': 449850331000,
#  'volume_ETH,USDT': 844810080000,
#  'volume_USDT,BTC': 7732113362639810}

class TestExchange(TestCase):

    def test_basic(self):
        exchange = Exchange(
            True, "test.csv")

        pairs = exchange.getAllPairs()

        # test buying BTC with USDT

        secret = exchange.register("nitko")

        balance_before = exchange.getBalance("nitko")["USDT"]

        self.assertEqual(
            balance_before, 1000 * 10 ** 8)

        # 1000 USDT = 0.05801 BTC
        # 1000 * 10 ** 8 USDT = 5801000 BTC

        exchange.createOrders(f"nitko", secret, f"USDT,BTC,{balance_before}")

        balance_after = exchange.getBalance("nitko")

        will_get = balance_before * pairs["close_USDT,BTC"] // 10 ** 8

        self.assertEqual(
            balance_after["USDT"], 0)

        self.assertEqual(
            balance_after["BTC"], will_get)

    def test_chain(self):
        exchange = Exchange(
            True, "test.csv")

        pairs = exchange.getAllPairs()

        # test buying BTC with USDT

        secret = exchange.register("nitko")

        balance_usdt_to_btc = exchange.getBalance("nitko")["USDT"]

        # 1000 USDT = 0.05801 BTC
        # 1000 * 10 ** 8 USDT = 5801000 BTC

        # 0.05801 BTC = 0.7687312817484 ETH
        # 5801000 BTC = 76873128 ETH

        self.assertEqual(
            balance_usdt_to_btc, 1000 * 10 ** 8)

        balance_btc_to_eth = balance_usdt_to_btc * \
            pairs["close_USDT,BTC"] // 10 ** 8

        self.assertEqual(
            balance_btc_to_eth, 5801000)

        balance_eth_to_usdt = balance_btc_to_eth * \
            pairs["close_BTC,ETH"] // 10 ** 8

        self.assertEqual(
            balance_eth_to_usdt, 76873128)

        exchange.createOrders(
            f"nitko", secret, f"USDT,BTC,{balance_usdt_to_btc}|BTC,ETH,{balance_btc_to_eth}|ETH,USDT,{balance_eth_to_usdt}")

        end_usdt = balance_eth_to_usdt * \
            pairs["close_ETH,USDT"] // 10 ** 8

        balance_after = exchange.getBalance("nitko")

        self.assertEqual(
            balance_after["USDT"], end_usdt)

        self.assertEqual(
            balance_after["BTC"], 0)

        self.assertEqual(
            balance_after["ETH"], 0)

    def test_low_volume(self):

        exchange = Exchange(
            True, "test.csv")

        pairs = exchange.getAllPairs()

        secret = exchange.register("nitko")

        exchange.balances.balances["nitko"]["USDT"] = 10 ** 30  # inf

        can_buy = (10 ** 8 * pairs["volume_USDT,BTC"]
                   ) // pairs["close_USDT,BTC"]

        exchange.createOrders(
            "nitko", secret, f"USDT,BTC,{can_buy + 10000}")

        exchange.regenerateVolume()

        with self.assertRaises(Exception):
            exchange.createOrders(
                "nitko", secret, f"USDT,BTC,{can_buy + 20000}")


if __name__ == "__main__":
    main()
