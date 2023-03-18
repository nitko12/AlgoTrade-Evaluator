import pandas as pd
import os
from tqdm import tqdm
import json
import datetime
from random import shuffle

round_name = "round_3"


def main():

    len_full = 42912

    files = list(os.listdir("data/rounds/" + round_name))

    shuffle(files)

    df_master = pd.read_csv("data/rounds/" + round_name + "/" + files[0])
    df_master["time_"] = pd.to_datetime(df_master['time'], unit='ms')
    df_master = df_master.set_index("time_")

    df_master = df_master.rename(
        columns={
            x: x + "_" + files[0].split(".")[0]
            for x in df_master.columns if x != "time_"
        })

    # print(df_master)

    # exit()

    # print(df_master.shape)

    print(df_master.shape)

    assert df_master.shape[0] == len_full

    for file in tqdm(files[1:]):
        df = pd.read_csv("data/rounds/" + round_name + "/" + file)

        # print(df.shape)

        if df.shape[0] != len_full:
            continue

        is_nan = df.isna().any().any()

        if is_nan:
            continue

        df["time_"] = pd.to_datetime(df['time'], unit='ms')

        df_master = df_master.join(df.set_index(
            "time_"), rsuffix="_" + file.split(".")[0])

    print(df_master.shape)

    for column in df_master.columns:
        print(column)

    df_master.to_parquet("data/rounds/" + round_name + ".parquet")


if __name__ == "__main__":
    main()
