
import pandas as pd
import os
from tqdm import tqdm
import json
import datetime

# 1500004800000 1675209300000

# 12.5.2021. - 18.7.2021.
# round_name = "round_1"
# start_time = int(datetime.datetime(2021, 5, 12, 12, 0, 50).timestamp() * 1000)
# end_time = int(datetime.datetime(2021, 7, 18, 12, 0, 50).timestamp() * 1000)

# 18.11.2021. - 23.2.2022.
# round_name = "round_2"
# start_time = datetime.datetime(2021, 11, 18, 12, 0, 50).timestamp() * 1000
# end_time = datetime.datetime(2022, 2, 23, 12, 0, 50).timestamp() * 1000

# 5.4.2022. - 1.9.2022.
round_name = "round_3"
start_time = datetime.datetime(2022, 4, 5, 12, 0, 50).timestamp() * 1000
end_time = datetime.datetime(2022, 9, 1, 12, 0, 50).timestamp() * 1000


def main():
    SYMBOLS = json.load(open("data/all_symbols.json"))

    all_files = os.listdir("data/data-aws")

    cnt = 0

    for fr in tqdm(SYMBOLS):
        for to in SYMBOLS:
            if fr == to:
                continue

            pair_files = [f for f in all_files if f.startswith(fr + to)]
            cnt += len(pair_files)

            l = []

            for fname in pair_files:
                df = pd.read_csv("data/data-aws/" + fname,
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

                df["time_"] = pd.to_datetime(df['time'], unit='ms')

                # print(df.shape)

                df = df.resample("5min", on="time_", origin=start_time).agg({
                    "time": "last",
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                    "close_time": "last",
                    "quote_asset_volume": "sum",
                    "number_of_trades": "sum",
                    "taker_buy_base_asset_volume": "sum",
                    "taker_buy_quote_asset_volume": "sum",
                    "ignore": "last"
                }).reset_index(drop=True)

                if df.shape[0] == 0:
                    continue

                l.append(df)

            if len(l) == 0:
                continue

            df = pd.concat(l, ignore_index=True)

            # sort by time

            df = df.sort_values(by="time")

            if df.shape[0] == 0:
                continue

            df.to_csv(f"data/rounds/{round_name}/{fr},{to}.csv",
                      index=False, float_format="%.8f")

    assert cnt == len(all_files)


if __name__ == "__main__":
    main()
