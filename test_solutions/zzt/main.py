import requests
from pprint import pprint
import random
import networkx as nx
import time

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

    while (True):

        # get all
        res = requests.get(
            f"{URL}/getAllPairs/")

        if res.status_code != 200:
            print(res.json())

        data = res.json()

        startingCurr = "USDT"

        G = nx.DiGraph()

        for key in data.keys():
            if not key.startswith("close"):
                continue

            key = key.split("_")[1]

            fr, to = key.split(",")

            G.add_edge(
                fr, to, weight=data["close_"+key], volume=data["volume_"+key])

            volume = data["volume_"+key]
            sell_volume = volume * data["close_"+key]

            G.add_edge(to, fr, weight=0.99*1 /
                       data["close_"+key], volume=sell_volume)

        q = []
        q.append((startingCurr, 1, [startingCurr]))

        while len(q) > 0:
            t = q.pop(0)

            # print(t)

            if t[0] == startingCurr:

                # print(t[2], t[1])
                if t[1] > 1:
                    print("=====================================")

                    print("JACKPOT", t[2], t[1])

                    balance = 100

                    for i in range(len(t[2]) - 1):
                        print(
                            f"buy {t[2][i]} and sell {t[2][i+1]} for {G[t[2][i]][t[2][i+1]]['weight']}")
                        print(
                            f"has volume {G[t[2][i]][t[2][i+1]]['volume']}")
                        print(
                            f"want volume {balance * G[t[2][i]][t[2][i+1]]['weight']}")

                        balance = balance * G[t[2][i]][t[2][i+1]]['weight']

                        if balance > G[t[2][i]][t[2][i+1]]['volume']:
                            print("not enough volume has: ",
                                  G[t[2][i]][t[2][i+1]]['volume'])
                            print("                  need: ", balance)

                            break

                    else:
                        if t[1] > 1.05:
                            assert False

                        print("SUCCESS")

                    print("=====================================")

            for n in G.neighbors(t[0]):

                if t[1]*G[t[0]][n]["weight"] < 1e-8 or t[1]*G[t[0]][n]["weight"] > 1e8:
                    continue

                if G[t[0]][n]["volume"] < 1e-8:
                    continue

                q.append((n, t[1]*G[t[0]][n]["weight"], t[2]+[n]))

        # currencies = set()
        # for key in data.keys():

        #     key = key.split("_")[1]

        #     currencies.add(key.split(",")[0])
        #     currencies.add(key.split(",")[1])

        # # print(data)

        # for currency in currencies:

        #     if currency == startingCurr:
        #         continue

        #     cycle = [startingCurr]
        #     cycle.append(currency)
        #     cycle.append(startingCurr)

        #     balance = 1

        #     for i in range(len(cycle) - 1):
        #         if f"close_{cycle[i]},{cycle[i+1]}" not in data:
        #             balance = -1
        #             break

        #         balance *= data[f"close_{cycle[i]},{cycle[i+1]}"]

        #     if balance > 0:
        #         print(cycle, balance)

        time.sleep(1)


if __name__ == '__main__':
    main()
