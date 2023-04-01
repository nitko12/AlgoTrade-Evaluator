from collections import defaultdict
import json
from pprint import pprint
import random
from fastapi import FastAPI, HTTPException, Request
import pandas as pd
import time
from exchange import Exchange
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import pickle

from fastapi.middleware.cors import CORSMiddleware

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

TEST = False

exchange = Exchange(TEST)

# /getAllPairs
# /getPairs
# /getHistoricalPairs
# /createOrder
# /balance
# /register
# /resetBalance


wrong_requests = defaultdict(int)
ips = {}


@app.get("/getTime")
@limiter.limit("5/second")
async def getTime(request: Request):
    """
    Returns the current time in seconds since the start of the exchange.

    Rate limit: 5/second
    """

    return exchange.getTime()


@app.get("/getAllPairs")
@limiter.limit("5/second")
async def getAllPairs(request: Request):
    """
    Returns all pairs and their current close price and volume.

    Rate limit: 5/second
    """
    try:

        all_pairs = exchange.getAllPairs()

    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))

    return all_pairs


@ app.get("/getPairs/{pairs}")
@ limiter.limit("5/second")
async def getPairs(request: Request, pairs: str):
    """
    Returns the current close price and volume for the given pairs,

    e.g. /getPairs/ETH,USD|BTC,USD

    Rate limit: 5/second
    """

    to_get = pairs.split("|")

    out = {}

    try:
        all_pairs = exchange.getAllPairs()
    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))

    for pair in to_get:
        if "close_" + pair not in all_pairs:
            raise HTTPException(status_code=400, detail="Pair not found")

        if "volume_" + pair not in all_pairs:
            raise HTTPException(status_code=400, detail="Pair not found")

        out["close_" + pair] = all_pairs["close_" + pair]
        out["volume_" + pair] = all_pairs["volume_" + pair]

    return out


@ app.get("/getHistoricalPairs/{time_to_get}/{pairs}")
@ limiter.limit("5/second")
async def getHistoricalPairs(request: Request, time_to_get: int, pairs: str):
    """
    Returns the close price and volume for the given pairs at the given time,
    time is in seconds since the start of the exchange and pairs is a pipe separated list of pairs.

    e.g. /getHistoricalPairs/100/ETH,USD|BTC,USD

    Rate limit: 5/second
    """

    to_get = pairs.split("|")

    out = {}

    try:
        all_pairs = exchange.getAllPairsAtTime(time_to_get)
    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))

    for pair in to_get:
        if "close_" + pair not in all_pairs:

            raise HTTPException(status_code=400, detail="Pair not found")

        if "volume_" + pair not in all_pairs:

            raise HTTPException(status_code=400, detail="Pair not found")

        out["close_" + pair] = all_pairs["close_" + pair]
        out["volume_" + pair] = all_pairs["volume_" + pair]

    return out


@ app.get("/createOrders/{user}/{secret}/{orders}")
@ limiter.limit("10/second")
async def createOrders(request: Request, user: str, secret: str, orders: str):
    """
    Places the given orders for the given user, orders is a pipe separated list of orders,

    e.g. /createOrders/user/secret/BTC,USD,100|ETH,USD,100

    Rate limit: 10/second
    """

    try:
        exchange.createOrders(user, secret, orders)
    except Exception as e:

        wrong_requests[user] += 1

        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Orders created"}


@ app.get("/register/{user}")
@ limiter.limit("1/second")
async def register(request: Request, user: str):
    """
    Registers the given user and returns a secret,
    be sure to save the secret as it is needed to reset the balance and
    to place orders.

    Rate limit: 1/second
    """

    try:
        secret = exchange.register(user)

        ips[user] = request.client.host
    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))

    return {"secret": secret}


@ app.get("/resetBalance/{user}/{secret}")
@ limiter.limit("1/second")
async def resetBalance(request: Request, user: str, secret: str):
    """
    Resets the balance of the given user to 1000 USD and all others to 0.
    Must be used only in test mode.

    Rate limit: 1/second
    """

    try:
        exchange.resetBalance(user, secret)
    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Balance reset"}


@ app.get("/balance/{user}")
@ limiter.limit("20/second")
async def balance(request: Request, user: str):
    """
    Returns the balance of the given user in all currencies.

    Rate limit: 20/second
    """

    try:
        balance = exchange.getBalance(user)
    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))

    return balance

wholesome_messages = [
    "If you're lost and looking for direction, fear not! Our /docs section has all the answers (well, most of them).",
    "Are you a curious cat? Scratch that itch with our /docs section!",
    "Feeling like a lost puppy? Our /docs section will help you find your way.",
    "Let's get down to business (to read our /docs).",
    "Want to know what makes us tick? Check out our /docs section, where all our secrets are revealed!",
    "Boredom busters! Visit our /docs section for fun facts and interesting tidbits.",
    "You're about to enter the twilight zone...of our /docs section!",
    "Don't worry, we don't bite (but our /docs section might).",
    "You won't believe what's in our /docs section! (Actually, you probably will - but it's still worth a look.)",
    "Our /docs section: where dreams come true (or at least, where you'll find answers to your burning questions).",
    "Get ready to take a deep dive into the abyss of our /docs section!",
    "Looking for some light reading? Our /docs section has got you covered.",
    "Come for the information, stay for the memes. Our /docs section is full of 'em!",
    "Why do birds suddenly appear? To show you the way to our /docs section, of course.",
    "Looking for answers? Our /docs section has more knowledge than Google (well, that might be a stretch).",
    "Are you a fan of mysteries? Check out our /docs section to unravel the secrets of our company.",
    "Need a good laugh? Our /docs section is funnier than a dad joke (we promise).",
    "Come one, come all! Our /docs section is open 24/7 for all your curiosity needs.",
    "Our /docs section: the cure for your boredom (and your insomnia).",
    "Have you ever seen a unicorn? No? Well, you won't find one in our /docs section either - but it's still worth checking out.",
    "Our /docs section: where the magic happens (well, not really, but it's still pretty cool).",
    "Need a break from reality? Our /docs section is a portal to a world of knowledge.",
    "They say curiosity killed the cat - but our /docs section will only make you smarter.",
    "Looking for a thrill? Our /docs section is more exciting than a roller coaster (well, maybe not that exciting, but you get the point).",
    "Our /docs section: the ultimate guide to our company (and the ultimate cure for boredom).",
    "Don't be shy! Our /docs section won't bite (we can't make any promises about the other sections though).",
    "Need a distraction from your daily routine? Our /docs section is the perfect way to spice things up.",
    "You won't believe what's in our /docs section...until you check it out for yourself!",
    "Knowledge is power - and our /docs section is full of it.",
    "Drago nam je da si tu!\nNo ovdje nema ništa, dokumentaciju možeš naći na URL-u /docs"
]


@ app.get("/")
@ limiter.limit("20/second")
async def index(request: Request):
    """
    Returns a wholesome message.

    Rate limit: 20/second
    """

    return {"message": random.choice(wholesome_messages)}

TOP_SECRET = "42_je_fora_broj"


@ app.get("/getAllBalances")
@ limiter.limit("20/second")
async def getAllBalances(request: Request, secret: str):
    """
    Returns the balance of all users in all currencies.

    Rate limit: 20/second
    """

    if secret != TOP_SECRET:
        raise HTTPException(status_code=400, detail="Invalid secret")

    try:
        balance = exchange.getAllBalances()
    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))

    return balance


@ app.get("/getAllBalancesCondensed")
@ limiter.limit("20/second")
async def getAllBalancesCondensed(request: Request, secret: str):
    """
    Returns the balance of all users in all currencies.

    Rate limit: 20/second
    """

    if secret != TOP_SECRET:
        raise HTTPException(status_code=400, detail="Invalid secret")

    try:
        balance = exchange.getAllBalances()
    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))

    out = {}

    for user in balance:
        d = {}

        for pair in balance[user]:
            if balance[user][pair] != 0:
                d[pair] = balance[user][pair]

        out[user] = d

    return out


@ app.get("/getIPsAndWrongRequests")
@ limiter.limit("20/second")
async def getIPsAndWrongRequests(request: Request, secret: str):

    if secret != TOP_SECRET:
        raise HTTPException(status_code=400, detail="Invalid secret")

    return {"ips": ips, "wrong_requests": wrong_requests}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0",
                port=8000, log_level="info")
