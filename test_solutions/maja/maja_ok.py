import requests
from pprint import pprint
import random
import time
from tqdm import trange

URL = "http://10.129.0.206:3000"

username = "zmaja" + str(random.randint(0, 100000))


def main():

    res = requests.get(
        f"{URL}/register/{username}")

    if res.status_code != 200:
        print(res.json())

    print("Register: ", res.json())

    secret = res.json()["secret"]

    print("Secret: ", secret)

    pot = 0

    while(pot < 1):
        pot += 1

        # get all
        res = requests.get(
            f"{URL}/getAllPairs/")

        if res.status_code != 200:
            print(res.json())

        data = res.json()

        unique_keys = set()
        for key in data.keys():
            if(not key.startswith("close_")):
                continue

            t1,t2 = key.split(",")
            unique_keys.add(t1[6::])
            unique_keys.add(t2)

        n = len(unique_keys)
        bio = {}; previ = {}; tcost = {}

        for key in unique_keys:
            tcost[key] = 0
            bio[key] = 0
            previ[key] = ""

        p = "USDT" # pocetni cvor
        tcost[p] = -1


        # pprint(data)

        edgeList = []
        for k,v in data.items():
            if(k.startswith("close_")):
                t1,t2 = k.split(",")
                # print(v)
                edgeList += [[t1[6:], t2, -v/1e8]]

        # print(n, len(edgeList))

        for i in range(n+1):
            for e in edgeList:
                a, b, cost = e
                volume1 = data[f"volume_{a},{b}"]
                volume2 = data[f"volume_{b},{a}"]
                if(tcost[b] > -abs(tcost[a]*cost) and volume1 > 1e6 and volume2 > 1e6):
                    tcost[b] = -abs(tcost[a]*cost)
                    previ[b] = a
        
        # print(previ)

        ind = p; cnt = 0 # pocetni cvor
        res = []
        while(not previ[ind] == ind and not bio[ind]):
            cnt+=1
            bio[ind] = 1
            res += [ind]
            ind = previ[ind]

        for i in range(len(res)-2, -1, -1):
            res += [res[i]]
        
        # print(res)

        trans = []

        vol = 100*1e8
        for i in range(len(res)-1): # MNOZI SA 1e8
            conv = data[f"close_{res[i]},{res[i+1]}"]
            alVol = data[f"volume_{res[i]},{res[i+1]}"]
            vol = min(0.99*vol*conv/1e8,alVol)

            trans += [f"{res[i]},{res[i+1]},{int((1e8*vol/conv*0.99))}"]

            

        # place order

        print(trans)

        for tr in trans:
            res = requests.get(f"{URL}/createOrders/{username}/{secret}/{tr}")

            if res.status_code != 200:
                print(res.json())

        # get my balance

        res = requests.get(f"{URL}/balance/{username}")

        if res.status_code != 200:
            print(res.json())

        finalData = res.json()
        print(p, finalData[p] // 1e8)

        print("=======================================================")
    
        time.sleep(1)


if __name__ == '__main__':
    main()
