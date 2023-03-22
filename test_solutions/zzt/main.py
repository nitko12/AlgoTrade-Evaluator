import requests
from pprint import pprint
import random
import networkx as nx
import time

URL = "http://localhost:3000"

username = "nitko"


def placeOrder(user, secret, order):

    orderText = ""

    for fr, to, amount in order:
        orderText += f"{fr},{to},{int(amount * 10 ** 8)}|"

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
                fr, to, weight=data["close_"+key] / (10 ** 8), volume=data["volume_"+key] / (10 ** 8))

        q = []
        q.append((startingCurr, 1, [startingCurr]))

        # q.append((startingCurr, 10, ['USDT', 'BNB', 'UPUSDT', 'ETH', 'USDT']))

        while len(q) > 0:
            t = q.pop(0)

            # print(t)

            if t[0] == startingCurr:

                # print(t[2], t[1])
                if t[1] > 1:
                    print("=====================================")

                    print("JACKPOT", t[2], t[1])

                    balance = 100

                    volumes = [100]

                    failed_volume_check = False

                    for i in range(len(t[2]) - 1):

                        volume_has = G[t[2][i]][t[2][i+1]]['volume']
                        volume_want = balance * G[t[2][i]][t[2][i+1]]['weight']

                        print(
                            f"buy {t[2][i]} and sell {t[2][i+1]} for {G[t[2][i]][t[2][i+1]]['weight']}")
                        print(
                            f"has volume {volume_has}")
                        print(
                            f"want volume {volume_want}")

                        if volume_want > volume_has:
                            print("========== not enough volume has: ",
                                  volume_has, "\n ========= want: ", volume_want)
                            failed_volume_check = True

                        volumes.append(volume_want)

                        balance = 0.999999 * balance * \
                            G[t[2][i]][t[2][i+1]]['weight']

                        if balance < 1e-8:
                            print("not enough balance")
                            break

                    else:

                        print("SUCCESS")

                        failed = placeOrder(username, secret, [
                            (t[2][i], t[2][i+1], volumes[i]) for i in range(len(t[2]) - 1)])

                        if t[1] > 1.05 and not failed:
                            print("we bad, nije dobro, idem plakat")

                        assert failed == failed_volume_check

                    print("=====================================")
                else:

                    # print("FAIL " + str(t[1]))

                    pass

            for n in G.neighbors(t[0]):

                if G[t[0]][n]["volume"] < 1e-8:
                    continue

                q.append((n, t[1] * G[t[0]][n]["weight"], t[2]+[n]))

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
