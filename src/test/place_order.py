from random import randint
import requests
from pprint import pprint
import math

URL = "http://localhost:8000"


def test1():
    print("test1")

    id = str(randint(0, 100000))

    res = requests.get(f"{URL}/register/nitko{id}").json()

    print(res)

    secret = res["secret"]

    balance_before = requests.get(
        f"{URL}/balance/nitko{id}").json()
    prices = requests.get(f"{URL}/getAllPairs").json()

    res = requests.get(
        f"{URL}/createOrders/nitko{id}/{secret}/USDT,BTC,100").json()

    print(res)

    balance_after = requests.get(f"{URL}/balance/nitko{id}").json()

    expected_usdt = 1000 - 100
    expected_btc = 100 * prices["close_USDT,BTC"]

    print(balance_before["USDT"], balance_before["BTC"])
    print(balance_after["USDT"], balance_after["BTC"])

    assert math.isclose(
        balance_after["USDT"], expected_usdt), f"{balance_after['USDT']} != {expected_usdt}"
    assert math.isclose(
        balance_after["BTC"], expected_btc), f"{balance_after['BTC']} != {expected_btc}"


def test2():
    print("test2")

    id = str(randint(0, 100000))

    res = requests.get(f"{URL}/register/nitko{id}").json()

    print(res)

    secret = res["secret"]

    balance_before = requests.get(
        f"{URL}/balance/nitko{id}").json()
    prices = requests.get(f"{URL}/getAllPairs").json()

    res = requests.get(
        f"{URL}/createOrders/nitko{id}/{secret}/USDT,BTC,100|BTC,ETH,0.00001").json()

    print(res)

    balance_after = requests.get(f"{URL}/balance/nitko{id}").json()

    expected_usdt = 1000 - 100
    expected_btc = 100 * prices["close_USDT,BTC"] - 0.00001
    expected_eth = 0.00001 * prices["close_BTC,ETH"]

    print(prices["close_BTC,ETH"])

    print(balance_before["USDT"], balance_before["BTC"], balance_before["ETH"])
    print(balance_after["USDT"], balance_after["BTC"], balance_after["ETH"])

    assert math.isclose(
        balance_after["USDT"], expected_usdt), f"{balance_after['USDT']} != {expected_usdt}"
    assert math.isclose(
        balance_after["BTC"], expected_btc), f"{balance_after['BTC']} != {expected_btc}"
    assert math.isclose(
        balance_after["ETH"], expected_eth), f"{balance_after['ETH']} != {expected_eth}"


def main():
    test1()
    test2()


if __name__ == '__main__':
    main()
