import time
import datetime
import pandas as pd
import os
from tqdm import tqdm
import json

SYMBOLS = json.load(open("data/all_symbols.json"))

# 12.5.2021. - 18.7.2021.
start_time = datetime.datetime(2021, 5, 12, 12, 0, 50).timestamp() * 1000
end_time = datetime.datetime(2021, 7, 18, 12, 0, 50).timestamp() * 1000

# 18.11.2021. - 23.2.2022.
# start_time = datetime.datetime(2021, 11, 18, 12, 0, 50).timestamp() * 1000
# end_time = datetime.datetime(2022, 2, 23, 12, 0, 50).timestamp() * 1000

# 5.4.2022. - 1.9.2022.
# start_time = datetime.datetime(2022, 4, 5, 12, 0, 50).timestamp() * 1000
# end_time = datetime.datetime(2022, 9, 1, 12, 0, 50).timestamp() * 1000


# mn_time = 1500004800000
# mx_time = 1675208700000

timeframe = 50


def make_pair_csv(fr, to):
    global start_time, end_time

    all_files = os.listdir("data/data-aws")
    all_files = [f for f in all_files if f.startswith(fr + to)]

    if len(all_files) == 0:
        return None

    l = []
    for file in all_files:
        df = pd.read_csv("data/data-aws/" + file,
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
        df = df[(df["time"] >= start_time) & (df["time"] <= end_time)]
        l.append(df)

    df = pd.concat(l, ignore_index=True)

    print(df.shape)

#     mock_df = pd.DataFrame({
#         "time": [mn_time, mx_time],
#     })
#     df = pd.concat((df, mock_df), ignore_index=True)

#     df["time"] = pd.to_datetime(df["time"], unit="ms")

#     df = df.resample(f"{timeframe}min", on="time",  # random number
#                      origin='start',
#                      ).agg({
#                          "open": "first",
#                          "high": "max",
#                          "low": "min",
#                          "close": "last",
#                          "volume": "sum",
#                          "close_time": "last",
#                          "quote_asset_volume": "sum",
#                          "number_of_trades": "sum",
#                          "taker_buy_base_asset_volume": "sum",
#                          "taker_buy_quote_asset_volume": "sum",
#                          "ignore": "sum"
#                      })

#     df["unix"] = df.index.astype(int) // 10 ** 6

#     assert (df["unix"] % (timeframe * 60 * 1000) ==
#             0).all(), f"time is not a multiple of {timeframe} minutes"

#     assert (df["unix"].diff().dropna() == timeframe * 60 *
#             1000).all(), f"time is not a multiple of {timeframe} minutes"

#     df = df[["unix", "open", "high", "low", "close", "volume"]]

#     df.to_csv("data/pairs/" + fr + "," + to + ".csv",
#               index=False, float_format="%.8f")


if __name__ == "__main__":

    for s1 in tqdm(SYMBOLS):
        for s2 in SYMBOLS:
            if s1 == s2:
                continue

            make_pair_csv(s1, s2)

    print(start_time)
    print(end_time)
