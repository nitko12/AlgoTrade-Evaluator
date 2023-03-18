import requests
from pprint import pprint
import random

URL = "http://localhost:3000"

username = "nitko" + str(random.randint(0, 100000))


def main():

    res = requests.get(
        f"{URL}/register/{username}")

    if res.status_code != 200:
        print(res.json())

    print("Register: ", res.json())

    secret = res.json()["secret"]

    print("Secret: ", secret)

    # place order

    res = requests.get(
        f"{URL}/createOrders/{username}/{secret}/USDT,BTC,100")

    if res.status_code != 200:
        print(res.json())

    # get my balance

    res = requests.get(
        f"{URL}/balance/{username}")

    if res.status_code != 200:
        print(res.json())

    pprint(res.json())


if __name__ == '__main__':
    main()
