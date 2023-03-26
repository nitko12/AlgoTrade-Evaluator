from collections import defaultdict
from random import shuffle
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


_data = requests.get("http://localhost:3000/getAllPairs").json()

data = {}
for k, v in _data.items():
    if "close" in k or "volume" in k:
        data[k] = (v / 10 ** 8)

    if "volume" in k:
        data[k] = 0.1 * data[k]


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

    all_nodes = list(G.nodes)
    shuffle(all_nodes)
    random_30_nodes = all_nodes

    G = G.subgraph(
        [startingCurr] + random_30_nodes)

    G = G.copy()

    outbound = G.out_edges(startingCurr, data=True)
    inbound = G.in_edges(startingCurr, data=True)

    G.add_node("START")
    G.add_node("END")

    for fr, to, data in outbound:
        G.add_edge("START", to, weight=data["weight"], volume=data["volume"])

    for fr, to, data in inbound:
        G.add_edge(fr, "END", weight=data["weight"], volume=data["volume"])

    G.remove_node(startingCurr)

    m = gp.Model("flow")
    m.params.NumericFocus = 2

    # fix  trickle flows
    m.params.FeasibilityTol = 1e-9

    eqs = defaultdict(gp.LinExpr)

    for fr, to, data in G.edges(data=True):
        flow = m.addVar(vtype=gp.GRB.CONTINUOUS, name=f"{fr}->{to}")

        eqs[fr] -= flow
        eqs[to] += flow * data["weight"]

        m.addConstr(flow * data["weight"] <= data["volume"])

        m.addConstr(flow <= 1e20)
        m.addConstr(flow * data["weight"] <= 1e20)

        temp1 = m.addVar(vtype=gp.GRB.BINARY, name=f"{fr}->{to}_zero")

        m.addConstr((temp1 == 0) >> (flow == 0))
        m.addConstr((temp1 == 1) >> (flow >= 1e-7))

        temp2 = m.addVar(vtype=gp.GRB.BINARY, name=f"{fr}->{to}_zero")

        m.addConstr((temp2 == 0) >> (flow * data["weight"] == 0))
        m.addConstr((temp2 == 1) >> (flow * data["weight"] >= 1e-7))

        G[fr][to]["var"] = flow
        G[fr][to]["var_bin"] = temp1

    for node in G.nodes:
        # add deg 2 constraint for all nodes

        if node == "START" or node == "END":
            continue

        m.addConstr(
            gp.quicksum(G[fr][node]["var_bin"]
                        for fr, _, _ in G.in_edges(node, data=True)) ==
            gp.quicksum(G[node][to]["var_bin"]
                        for _, to, _ in G.out_edges(node, data=True))
        )

        m.addConstr(
            gp.quicksum(G[fr][node]["var_bin"]
                        for fr, _, _ in G.in_edges(node, data=True)) <=
            1
        )

        m.addConstr(
            gp.quicksum(G[node][to]["var_bin"]
                        for _, to, _ in G.out_edges(node, data=True)) <=
            1
        )

    starting_amount = m.addVar(vtype=gp.GRB.CONTINUOUS, name="starting_amount")
    eqs["START"] += starting_amount

    m.addConstr(starting_amount <= amount)

    ending_amount = m.addVar(vtype=gp.GRB.CONTINUOUS, name="ending_amount")
    eqs["END"] -= ending_amount

    for node in G.nodes:
        m.addConstr(eqs[node] == 0)

    m.setObjective(ending_amount, gp.GRB.MAXIMIZE)
    m.optimize()

    print("Optimal value: ", m.objVal)

    G2 = nx.DiGraph()

    for fr, to, data in G.edges(data=True):
        if data["var"].x > 0:
            G2.add_edge(fr, to, var=data["var"], weight=data["weight"])

            # print(f"{fr} -> {to} : {data['var'].x * data['weight']}")

    # for cycle in nx.simple_cycles(G2):
    #     print(cycle)

    # do bfs on G2
    q = ["START"]
    vis = set()

    s = ""

    while len(q) > 0:
        curr = q.pop(0)

        if curr in vis:
            continue

        vis.add(curr)

        for to, data in G2.adj[curr].items():

            print(f"{curr} -> {to} : {data['var'].x}")

            _curr = curr
            if curr == "START":
                _curr = startingCurr

            _to = to
            if to == "END":
                _to = startingCurr

            s += f"{_curr},{_to},{int(data['var'].x * 10 ** 8)}|"

            q.append(to)

    with open("solution.txt", "w") as f:
        f.write(s[:-1])


def main():
    print("Starting")

    G = makeGraph(data)

    solve(G, "USDT", 10)

    # print(G)


if __name__ == "__main__":
    main()
