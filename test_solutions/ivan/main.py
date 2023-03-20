import requests
from pprint import pprint
import random
import time
import networkx as nx
import math
import matplotlib.pyplot as plt
import json

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

    while True:

        res = requests.get(
            f"{URL}/getAllPairs")

        G = nx.DiGraph()

        if res.status_code != 200:
            print(res.json())

            continue

        all_pairs = set()

        res_json = res.json()
        res_json = json.load(open("test.json"))

        for pair in res_json:
            print(pair, res_json[pair])

        exit()

        time.sleep(1)


if __name__ == '__main__':
    main()
