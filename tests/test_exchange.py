
import sys
from pprint import pprint
sys.path.append("../src")


from exchange import Exchange  # noqa: E402


exchange = Exchange(
    True, "test.csv")

# {'close_BTC,ETH': 1325170284,
#  'close_ETH,USDT': 128839000000,
#  'close_USDT,BTC': 5801,
#  'volume_BTC,ETH': 108181980000,
#  'volume_ETH,USDT': 844810080000,
#  'volume_USDT,BTC': 488564772000}


def test1():

    pairs = exchange.getAllPairs()

    secret = exchange.register("nitko")

    balance_before = exchange.getBalance("nitko")
    print(balance_before)

    # 1000 USDT = 0.05801 BTC
    # 1000 * 10 ** 8 USDT = 5801000 BTC

    to_buy = 1000 * 10 ** 8
    exchange.createOrders(f"nitko", secret, f"USDT,BTC,{to_buy}")

    balance_after = exchange.getBalance("nitko")
    print(balance_after)

    will_get = to_buy * pairs["close_USDT,BTC"] // 10 ** 8

    assert balance_after["USDT"] == 0, f"{balance_after['USDT']} != 0"
    assert balance_after["BTC"] == will_get, f"{balance_after['BTC']} != {to_buy}"

    print("TEST1: OK")


if __name__ == "__main__":
    test1()
