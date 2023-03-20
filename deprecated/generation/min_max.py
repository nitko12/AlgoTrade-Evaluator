
import pandas as pd
import os
from tqdm import tqdm

# 1500004800000 1675209300000

if __name__ == "__main__":
    mn_time = None
    mx_time = None

    for x in tqdm(os.listdir("data/data-aws")):
        df = pd.read_csv("data/data-aws/" + x,
                         names=["time",
                                "open",
                                "high",
                                "low",
                                "close",
                                "volume",
                                "close_time",
                                "quote_asset_volume",
                                "number_of_trades",
                                "taker_buy_base_asset_volume",
                                "taker_buy_quote_asset_volume",
                                "ignore"])

        if mn_time is None:
            mn_time = df["time"].min()
        mn_time = min(mn_time, df["time"].min())

        if mx_time is None:
            mx_time = df["time"].max()
        mx_time = max(mx_time, df["time"].max())

    print(mn_time, mx_time)
