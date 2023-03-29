from collections import defaultdict
import json
import math
from random import shuffle
import random
import networkx as nx
import requests
from pprint import pprint
import gurobipy as gp
import pandas as pd
import matplotlib.pyplot as plt

# data = {
#     'close_USDT,BTC': (5801 / 10 ** 8),
#     'close_BTC,ETH': 1325170284 / 10 ** 8,
#     'close_ETH,USDT': 128839000000 / 10 ** 8,

#     # 'close_USDT,SOL': 7047216 / 10 ** 8,
#     # 'close_SOL,BUSD': 1404000000 / 10 ** 8,
#     # 'close_BUSD,USDT': 99990000 / 10 ** 8,

#     'volume_USDT,BTC': 1,
#     'volume_BTC,ETH': 0.0007761624973804515,
#     'volume_ETH,USDT': 1,

#     # 'volume_BUSD,USDT': 100,
#     # 'volume_SOL,BUSD': 100,
#     # 'volume_USDT,SOL': 100
# }

# _data = pd.read_csv("data2.csv").iloc[0].to_dict()


# _data = requests.get("http://localhost:3000/getAllPairs").json()
_data = pd.read_csv("smol.csv").iloc[0].to_dict()

data = {}
for k, v in _data.items():
    if "close" in k or "volume" in k:
        data[k] = (v / 10 ** 8)

    # if "volume" in k:
    #     data[k] = data[k] / 10 ** 8


def makeGraph(data):
    G = nx.DiGraph()

    all_pairs = set()

    for k, _ in data.items():
        fr, to = k.split("_")[1].split(",")

        all_pairs.add((fr, to))

    for fr, to in all_pairs:
        G.add_edge(
            fr, to,
            weight=data[f"close_{fr},{to}"],
            volume=data[f"volume_{fr},{to}"])

    return G


def solve(G, startingCurr, amount):

    G = G.copy()

    # out edges
    all_out_edges = list(G.out_edges(startingCurr, data=True))

    # in edges
    all_in_edges = list(G.in_edges(startingCurr, data=True))

    # remove startingCurr

    G.remove_node(startingCurr)

    # add START and END nodes

    G.add_node("START")
    G.add_node("END")

    # add edges from START to all out edges
    for fr, to, data in all_out_edges:
        G.add_edge("START", to, weight=data["weight"], volume=data["volume"])

    # add edges from all in edges to END
    for fr, to, data in all_in_edges:
        G.add_edge(fr, "END", weight=data["weight"], volume=data["volume"])

    # print(G.edges(data=True))

    m = gp.Model("mip1")

    # set numerical focus
    m.setParam(gp.GRB.Param.NumericFocus, 3)

    # set numerical tolerance
    m.setParam(gp.GRB.Param.IntFeasTol, 1e-9)

    eqs = {
        node: gp.LinExpr()
        for node in G.nodes
    }

    # add variables

    edge_x = m.addVars(G.edges, vtype=gp.GRB.CONTINUOUS, name="x")
    edge_not_zero = m.addVars(G.edges, vtype=gp.GRB.BINARY, name="not_zero")

    # add constraints

    for fr, to, data in G.edges(data=True):
        m.addConstr(edge_x[fr, to] * data["weight"] <= data["volume"])


    for fr, to, data in G.edges(data=True):

        m.addConstr(
            (edge_not_zero[fr, to] == 0) >> (edge_x[fr, to] == 0)
        )

        m.addConstr(
            (edge_not_zero[fr, to] == 1) >> (edge_x[fr, to] >= 1e-8)
        )

        eqs[fr] -= edge_x[fr, to] 
        eqs[to] += edge_x[fr, to] * data["weight"]

    # deg 2 constr

    for node in G.nodes:
        if node == "START":
            m.addConstr(
                gp.quicksum(edge_not_zero["START", to] for to in G.successors(node)) == 1
            )

        elif node == "END":
            m.addConstr(
                gp.quicksum(edge_not_zero[fr, "END"] for fr in G.predecessors(node)) == 1
            )

        else:
            m.addConstr(
                gp.quicksum(edge_not_zero[fr, node] for fr in G.predecessors(node)) ==
                gp.quicksum(edge_not_zero[node, to] for to in G.successors(node))
            )
            m.addConstr(
                gp.quicksum(edge_not_zero[fr, node] for fr in G.predecessors(node)) <=
                1
            )
            m.addConstr(
                gp.quicksum(edge_not_zero[fr, node] for fr in G.predecessors(node)) <=
                1
            )



    start_flow = amount
    end_flow = m.addVar(vtype=gp.GRB.CONTINUOUS, name="end_flow")

    eqs["START"] += start_flow
    eqs["END"] -= end_flow

    for node in G.nodes:
        m.addConstr(eqs[node] == 0)

    eqs["START"] += start_flow
    eqs["END"] -= end_flow
    
    m.setObjective(end_flow, gp.GRB.MAXIMIZE)

    m.optimize()

    transactions = []
    

    G2 = nx.DiGraph()

    for edge, var in edge_x.items():
        if var.x > 0:
            print(f"{edge[0]},{edge[1]},{int(var.x * 10 ** 8)}")
            transactions.append((edge[0], edge[1], var.x))

            G2.add_edge(edge[0], edge[1], weight=var.x)

    
    # balances = {
    #     node: 0
    #     for node in G.nodes
    # }
    # balances["START"] = amount

    # filled = [
    #     0 for _ in range(len(transactions))
    # ]

    # mx = 0

    # def search_order():

    #     nonlocal mx

    #     if sum(filled) > mx:
    #         mx = sum(filled)

    #         print(sum(filled), len(transactions))

    #     if sum(filled) == len(filled):
    #         # print(balances)
    #         return
        
    #     for f, tr in zip(filled, transactions):
    #         if f == 1:
    #             continue

    #         if balances[tr[0]] + 0.1 < tr[2]:
    #             continue

    #         balances[tr[0]] -= tr[2]
    #         balances[tr[1]] += tr[2] * G[tr[0]][tr[1]]["weight"]

    #         filled[transactions.index(tr)] = 1

    #         search_order()

    #         balances[tr[0]] += tr[2]
    #         balances[tr[1]] -= tr[2] * G[tr[0]][tr[1]]["weight"]

    #         filled[transactions.index(tr)] = 0
        
    # search_order()


    # # shuffle transactions

    # # random.shuffle(transactions)

    # while len(transactions) > 0:
    #     # print(len(transactions))
        
    #     for fr, to, value in transactions:

    #         if balances[fr] < value:
    #             continue

    #         balances[fr] -= value
    #         balances[to] += value

    #         # print(f"{fr},{to},{value}")

    #         transactions.remove((fr, to, value))

    # print(balances)


def main():
    print("Starting")

    G = makeGraph(data)

    solve(G, "USDT", 1000)

    print(G)

    # print(G)


if __name__ == "__main__":
    main()
