import requests
from pprint import pprint
import random
import networkx as nx
import time
import pandas as pd


URL = "http://localhost:3000"

username = "nitko" + str(random.randint(0, 100000))


def placeOrder(user, secret, order):

    orderText = ""

    for fr, to, amount in order:
        orderText += f"{fr},{to},{int(amount )}|"

    orderText = orderText[:-1]

    print("Order text: ", orderText)

    res = requests.get(
        f"{URL}/createOrders/{user}/{secret}/{orderText}")

    print("Order: ", res.json())

    return "detail" in res.json()


def main():

    res = requests.get(
        f"{URL}/register/{username}")

    if res.status_code != 200:
        print(res.json())

    print("Register: ", res.json())

    secret = res.json()["secret"]

    print("Secret: ", secret)

    # get all
    res = requests.get(
        f"{URL}/getAllPairs/")

    if res.status_code != 200:
        print(res.json())

    data = res.json()

    startingCurr = "USDT"

    # 10000000000
    # 52450000000
    # 966285825
    # 10128608007

    placeOrder(username, secret, [
        ('USDT', 'BRL', 10000000000),
        ('BRL', 'ATOM', 52450000000),
        ('ATOM', 'USDT', 966285825),
    ])

    print("close_USDT,BRL", data["close_USDT,BRL"])

    balance = requests.get(
        f"{URL}/balance/{username}").json()

    print(balance["BRL"])
    print(int(10000000000 * data["close_USDT,BRL"] // 10 ** 8))

    print()

    print(balance["ATOM"])
    print(int(52450000000 * data["close_BRL,ATOM"] // 10 ** 8))

    print()

    print(balance["USDT"])
    print(int(966285825 * data["close_ATOM,USDT"] // 10 ** 8))
    print(10128608007)

    print("close", data["close_ATOM,USDT"])

    # 'USDT,BRL,52450000000', 'BRL,ATOM,966285825', 'ATOM,USDT,10128608007'


if __name__ == '__main__':
    main()
