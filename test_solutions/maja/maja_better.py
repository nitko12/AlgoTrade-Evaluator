import requests
from pprint import pprint
import random
import time

URL = "http://localhost:3000"

username = "maja" + str(random.randint(0, 100000))


def main():

    res = requests.get(
        f"{URL}/register/{username}")

    if res.status_code != 200:
        print(res.json())

    print("Register: ", res.json())

    secret = res.json()["secret"]

    print("Secret: ", secret)

    pot = 0

    while (pot < 2):
        pot += 1

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

        # print("len", len(pot2), len(pot2))

        currGain = 0
        trans = []
        volume = []
        money = []
        startVolume = int(1e8*100)  # startingCurr
        for key2 in pot2:
            for key3 in pot3:
                k2 = key2[0].split(",")[1]
                k3 = key3[0].split(",")[0][6::]

                key23 = f"close_{k2},{k3}"
                if (key23 in data):
                    # allowed volumes
                    alVol1 = data[f"volume_{startingCurr},{k2}"]
                    alVol2 = data[f"volume_{k2},{k3}"]
                    alVol3 = data[f"volume_{k3},{startingCurr}"]

                    vol2 = int(min(startVolume*key2[1] // 1e8, alVol1))
                    vol3 = int(min(vol2*data[key23] // 1e8, alVol2))
                    vol4 = int(min(vol3*key3[1] // 1e8, alVol3))

                    if (vol4 > currGain):
                        trans = [f"{startingCurr},{k2},{vol2}",
                                 f"{k2},{k3},{vol3}", f"{k3},{startingCurr},{vol4}"]
                        volume = [data[f"volume_{startingCurr},{k2}"],
                                  data[f"volume_{k2},{k3}"], data[f"volume_{k3},{startingCurr}"]]
                        money = [data[f"close_{startingCurr},{k2}"],
                                 data[f"close_{k2},{k3}"], data[f"close_{k3},{startingCurr}"]]
                        currGain = vol4

        print("currGain:", currGain // 1e8)
        print("transakcije:", trans)
        print("volume:", volume)
        print("money: ", money)

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
        print(startingCurr, finalData[startingCurr] // 1e8)

        print("=======================================================")

        time.sleep(1)


if __name__ == '__main__':
    main()
