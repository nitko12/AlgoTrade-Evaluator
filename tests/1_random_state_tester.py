from collections import defaultdict
import requests
from pprint import pprint
import random
import time
from tqdm import trange

URL = "http://localhost:3000"

username = "zmaja" + str(random.randint(0, 100000))

chain_len = 10

def get_all_pairs():
    res = requests.get(f"{URL}/getAllPairs/")
    if res.status_code != 200:
        print(res.json())
    return res.json()


def get_balance(username):
    res = requests.get(f"{URL}/balance/{username}")
    if res.status_code != 200:
        print(res.json())
    return res.json()

def create_orders(username, secret, l):

    order_str = ""

    for fr, to, amount in l:
        order_str += f"{fr},{to},{amount}|"

    order_str = order_str[:-1]

    res = requests.get(
        f"{URL}/createOrders/{username}/{secret}/{order_str}")
    
    if res.status_code != 200:
        print(res.json())
        raise Exception("Error")
    
    if "error" in res.json():
        print("Error: ", res.json())
        raise Exception("Error")
    
    return res.json()

balances = defaultdict(int)
balances["USDT"] = 1000_0000_0000

def create_order_local(fr, to, close, to_transfer):
    global balances

    balances[fr] -= to_transfer
    balances[to] += int(to_transfer * close // 10 ** 8)

    assert balances[fr] >= 0, f"Error: {fr} {balances[fr]}"
    assert balances[to] >= 0, f"Error: {to} {balances[to]}"

def compare_local_server(username):
    global balances

    balances_server = get_balance(username)

    for key in balances.keys():
        if balances[key] != balances_server[key]:
            print("Error: ", key, balances[key], balances_server[key])
            raise Exception("Error")
        
    print("OK")


def create_max_order(username, secret, fr, to, starting_bal, close, volume):

    to_transfer = min(starting_bal, int(10 ** 8 * volume / close))

    # print("To transfer: ", to_transfer)

    if to_transfer < 100:
        return None, None, None
    
    if to_transfer * close < 100 * 10 ** 8:
        return None, None, None
    
    return fr, to, to_transfer


def test(secret):
    global balances

    balances = get_balance(username)
    pairs = get_all_pairs()

    if "error" in balances:
        print("Error: ", balances)
        return

    if "error" in pairs:
        print("Error: ", pairs)
        return

    orders = []
    order_set = set()

    cnt = 0

    while cnt < chain_len:
        pair = None

        while pair is None or not pair.startswith("close_") or balances[pair[6:].split(",")[0]] < 100:
            pair = random.choice(list(pairs.keys()))

        pair = pair[6::]

        

        close = pairs["close_" + pair]

        fr, to, to_transfer = create_max_order(username, secret, pair.split(",")[0],
                        pair.split(",")[1],
                        balances[pair.split(",")[0]],
                        close,
                        pairs["volume_" + pair])
        
        if (fr, to) in order_set:
            continue

        print("Pair: ", pair)

        order_set.add((fr, to))
        
        if fr is None:
            continue

        create_order_local(fr, to, close, to_transfer)
        orders.append((fr, to, to_transfer))

        cnt += 1

    create_orders(username, secret, orders)
    
    compare_local_server(username)


def main():

    res = requests.get(
        f"{URL}/register/{username}")

    if res.status_code != 200:
        print(res.json())
        exit()

    print("Register: ", res.json())

    secret = res.json()["secret"]

    print("Secret: ", secret)

    while True:
        test(secret)

        time.sleep(1)


if __name__ == '__main__':
    main()
