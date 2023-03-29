import json
from pprint import pprint
from fastapi import FastAPI, HTTPException, Request
import pandas as pd
import time
from exchange import Exchange
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

TEST = False

exchange = Exchange(TEST)

# /getAllPairs
# /getPairs
# /getHistoricalPairs
# /createOrder
# /balance
# /register
# /resetBalance


@app.get("/getTime")
@limiter.limit("25/second")
async def getTime(request: Request):
    """
    Returns the current time in seconds since the start of the exchange.

    Rate limit: 25/second
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

    e.g. /createOrders/user/secret/BTC,USD,100,1|ETH,USD,100,1

    Rate limit: 10/second
    """

    try:
        exchange.createOrders(user, secret, orders)
    except Exception as e:

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

@ app.get("/")
@ limiter.limit("20/second")
async def index(request: Request):
    """
    Returns a wholesome message.

    Rate limit: 20/second
    """

    return {"message": "Drago nam je da si tu!\nNo ovdje nema ništa, dokumentaciju možeš naći na URL-u /docs"}

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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0",
                port=8000, log_level="info")