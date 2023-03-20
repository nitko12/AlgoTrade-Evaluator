import json
import random
import pandas as pd
from pprint import pprint
import networkx as nx
import math
import gurobipy as gp
from gurobipy import GRB
from tqdm import tqdm
import os

from json import encoder


path = "/Users/nitkonitkic/Documents/hackathon/data/rounds/round_1"


def main():

    d = {}

    for f in tqdm(os.listdir(path)):
        # print(f)
        if f.endswith(".csv"):
            df = pd.read_csv(os.path.join(path, f))
            df = df.dropna()

            target = 1620817500000

            row = df[df['time'] == target]

            if len(row) == 0:
                continue

            row = row.iloc[0]

            fr, to = f.split(".")[0].split(",")

            d[f"close_{fr},{to}"] = row['close']
            d[f"volume_{fr},{to}"] = row['volume']

            d[f"close_{to},{fr}"] = 1 / row['close']
            d[f"volume_{to},{fr}"] = row['volume']

    json.encoder.FLOAT_REPR = lambda f: ("%.6f" % f)
    json.dump(d, open("snapshot.json", "w"))


if __name__ == '__main__':
    main()
