import requests
from pprint import pprint
import random
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

        pot2 = [[k, v] for k, v in data.items() if k.split(",")[0] ==
                f"close_{startingCurr}"]
        pot3 = [[k, v] for k, v in data.items() if k.split(",")[0].startswith(
            "close_") and k.split(",")[1] == f"{startingCurr}"]

        print("len", len(pot2), len(pot2))

        currGain = 0
        err = 0
        trans = []
        cnt = 0
        startValue = 100  # startingCurr
        for key2 in pot2:
            for key3 in pot3:
                k2 = key2[0].split(",")[1]
                k3 = key3[0].split(",")[0][6::]

                # print(k2, k3)

                # if(k2 == k3):
                #     print(key2[1]*key3[1])
                #     if(key2[1]*key3[1] > 0.1):
                #         cnt += 1

                key23 = f"close_{k2},{k3}"
                if (key23 in data):
                    # allowed volumes
                    alVol1 = data[f"volume_{startingCurr},{k2}"]
                    alVol2 = data[f"volume_{k2},{k3}"]
                    alVol3 = data[f"volume_{k3},{startingCurr}"]

                    vol1 = min(startValue, alVol1)
                    vol1 = float(str(f"{vol1:10f}"))

                    vol2 = min(vol1*key2[1], alVol2)
                    vol2 = float(str(f"{0.999*vol2:10f}"))

                    vol3 = min(vol2*data[key23], alVol3)
                    vol3 = float(str(f"{0.999*vol3:10f}"))

                    print(vol3*key3[1])

                    if (vol3*key3[1] > currGain):
                        trans = [f"{startingCurr},{k2},{vol1}",
                                 f"{k2},{k3},{vol2}", f"{k3},{startingCurr},{vol3}"]
                        money = [data[f"close_{startingCurr},{k2}"],
                                 data[f"close_{k2},{k3}"], data[f"close_{k3},{startingCurr}"]]
                        currGain = vol3*key3[1]

        print("currGain:", currGain)
        print(trans)
        print(money)
        print(startValue * money[0] * money[1] * money[2])

        # place order

        for tr in trans:
            res = requests.get(f"{URL}/createOrders/{username}/{secret}/{tr}")

            if res.status_code != 200:
                print(res.json())

        # get my balance

        res = requests.get(f"{URL}/balance/{username}")

        if res.status_code != 200:
            print(res.json())

        finalData = res.json()
        print(startingCurr, finalData[startingCurr])

        time.sleep(1)


if __name__ == '__main__':
    main()
