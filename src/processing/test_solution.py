import pandas as pd
import matplotlib.pyplot as plt

import networkx as nx
import math
import gurobipy as gp
from gurobipy import GRB

import random


def get_best_sol(G):
    m = gp.Model("mip2")

    # Create variables

    # silent

    m.setParam("OutputFlag", 0)

    x = m.addVars(G.edges(), vtype=GRB.BINARY, name="x")

    m.addConstrs((x.sum(fr, "*") <= 1 for fr in G.nodes()), "deg1_fr")
    m.addConstrs((x.sum("*", to) <= 1 for to in G.nodes()), "deg1_to")

    m.addConstrs((x.sum("*", node) == x.sum(node, "*")
                 for node in G.nodes()), "deg1_to")

    total_profit = gp.quicksum(
        x[fr, to] * G[fr][to]["weight"]
        for fr, to in G.edges()
    )

    m.setObjective(
        total_profit,
        GRB.MAXIMIZE)

    m.optimize()

    G2 = nx.DiGraph()

    for fr, to in G.edges():
        if x[fr, to].x > 0.5:
            G2.add_edge(fr, to, weight=G[fr][to]["weight"])

    best = 0

    for cycle in nx.simple_cycles(G2):
        print(cycle)

        balance = 0

        # print(cycle)

        for i in range(len(cycle)):
            fr = cycle[i]
            to = cycle[(i+1) % len(cycle)]

            balance += G[fr][to]["weight"]

        # print(balance)

        if balance > best:
            best = balance

    return best


def main():
    df = pd.read_parquet('data/rounds/round_1_augmented.parquet')

    for row in df.iloc:

        G = nx.DiGraph()

        for edge in row.to_dict():

            if edge.startswith('close_'):
                fr, to = edge.split('_')[-1].split(',')

                # offset = random.gauss(0, 0.0001)

                new_weight = row[edge]

                G.add_edge(fr, to, weight=math.log(new_weight))

        print(get_best_sol(G))


if __name__ == '__main__':
    main()
