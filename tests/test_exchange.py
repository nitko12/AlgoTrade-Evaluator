
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

    def test_maja_sol(self):
        exchange = Exchange(
            True, "/Users/nitkonitkic/Documents/hackathon/data/data2.csv")

        pairs = exchange.getAllPairs()

        # test buying BTC with USDT

        # 'USDT,ATM,3623188400', 'ATM,BUSD,10036231868', 'BUSD,USDT,10035228244'

        secret = exchange.register("nitko")

        balance_usdt_to_atm = int(
            0.03995 * exchange.getBalance("nitko")["USDT"])

        # self.assertEqual(
        #     balance_usdt_to_atm, 1000 * 10 ** 8)

        # print(balance_usdt_to_atm)

        balance_atm_to_busd = balance_usdt_to_atm * \
            pairs["close_USDT,ATM"] // 10 ** 8

        # self.assertEqual(
        #     balance_atm_to_busd, 3623188400)

        # print(balance_atm_to_busd)

        balance_busd_to_usdt = balance_atm_to_busd * \
            pairs["close_ATM,BUSD"] // 10 ** 8

        # print("has volume", pairs["volume_ATM,BUSD"])

        # self.assertEqual(
        #     balance_busd_to_usdt, 10036231868)

        # print(balance_busd_to_usdt)

        exchange.createOrders(
            "nitko", secret, f"USDT,ATM,{balance_usdt_to_atm}|ATM,BUSD,{balance_atm_to_busd}|BUSD,USDT,{balance_busd_to_usdt}")

        end_usdt = balance_busd_to_usdt * \
            pairs["close_BUSD,USDT"] // 10 ** 8

        balance_after = exchange.getBalance("nitko")

        # print(balance_after["USDT"], end_usdt)

    def test_maja_sol2(self):

        # 'USDT,BRL,52450000000', 'BRL,ATOM,966285825', 'ATOM,USDT,10128608007'

        exchange = Exchange(
            True, "/Users/nitkonitkic/Documents/hackathon/data/data2.csv")

        pairs = exchange.getAllPairs()

        secret = exchange.register("nitko")

        balance_usdt_to_brl = int(100 * 10 ** 8)

        print(balance_usdt_to_brl)

        balance_brl_to_atom = balance_usdt_to_brl * \
            pairs["close_USDT,BRL"] // 10 ** 8

        print(balance_brl_to_atom)

        balance_atom_to_usdt = balance_brl_to_atom * \
            pairs["close_BRL,ATOM"] // 10 ** 8

        print(balance_atom_to_usdt)

        balance_end = balance_atom_to_usdt * \
            pairs["close_ATOM,USDT"] // 10 ** 8

        print("close", pairs["close_ATOM,USDT"])

        print(balance_end)

        exchange.createOrders(
            "nitko", secret, f"USDT,BRL,{balance_usdt_to_brl}|BRL,ATOM,{balance_brl_to_atom}|ATOM,USDT,{balance_atom_to_usdt}")


if __name__ == "__main__":
    main()
