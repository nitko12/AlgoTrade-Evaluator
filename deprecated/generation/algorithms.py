import random
import pandas as pd
import networkx as nx
import math
import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt
from tqdm import trange
import numpy as np
from tqdm import tqdm


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


def get_log_cycle_balance(G, cycle):
    balance = 0

    for i in range(len(cycle)):
        fr = cycle[i]
        to = cycle[(i+1) % len(cycle)]

        balance += G[fr][to]["weight"]

    return balance


def has_positive_cycle(G, offset=0):
    G2 = nx.DiGraph()

    for fr, to in G.edges():
        G2.add_edge(fr, to, weight=-G[fr][to]["weight"] + offset)

    return nx.negative_edge_cycle(G2)


def augment_graph(G):

    lo, hi = 0, 10

    for _ in range(50):

        mid = (lo + hi) / 2
        f = has_positive_cycle(G, offset=mid)

        # print(mid)

        if f:
            lo = mid + 0.0001
        else:
            hi = mid

        # print(lo, hi)

    G2 = nx.DiGraph()

    for fr, to in G.edges():
        G2.add_edge(fr, to, weight=G[fr][to]["weight"] - lo)

    return G2, lo

    # scores = []

    # for i in trange(1000):
    #     G2 = nx.DiGraph()

    #     for fr, to in G.edges():

    #         # normal distribution
    #         # edge = random.gauss(0, 0.01)
    #         edge = random.uniform(-0.01, 0.01)

    #         G2.add_edge(fr, to, weight=G[fr][to]["weight"] - lo + edge)

    #     score = math.exp(get_best_sol(G2))

    #     if score > 1:
    #         scores.append(score)

    # # plot hist

    # plt.hist(scores, bins=50)

    # plt.show()


def augment_graph_fw(G):

    dist_matrix = {(x, y): -math.inf for x in G.nodes() for y in G.nodes()}

    for fr, to in G.edges():
        dist_matrix[(fr, to)] = G[fr][to]["weight"]

    for k in G.nodes():
        for i in G.nodes():
            for j in G.nodes():
                dist_matrix[(i, j)] = max(
                    dist_matrix[(i, j)],
                    dist_matrix[(i, k)] + dist_matrix[(k, j)]
                )

    m = gp.Model("mip2")
    offsets = m.addVars(G.edges(), vtype=GRB.CONTINUOUS, name="offsets")

    for k in G.nodes():
        for i in G.nodes():
            for j in G.nodes():

                o1 = 0

                if (i, k) in G.edges():
                    o1 = offsets[(i, k)]

                o2 = 0

                if (k, j) in G.edges():
                    o2 = offsets[(k, j)]

                if dist_matrix[(i, j)] != -math.inf and \
                        dist_matrix[(i, k)] != -math.inf and \
                        dist_matrix[(k, j)] != -math.inf:
                    m.addConstr(
                        dist_matrix[(i, j)] <= dist_matrix[(i, k)] +
                        dist_matrix[(k, j)] + o1 + o2
                    )

    m.setObjective(
        gp.quicksum(offsets[fr, to] for fr, to in G.edges()),
        GRB.MINIMIZE)

    m.optimize()


def augment_graph_bf(G):
    pass

    # components = list(nx.strongly_connected_components(G))

    # for component in components:

    #     m = gp.Model("mip2")

    #     # bellman ford

    #     offsets = m.addVars(G.edges(), vtype=GRB.CONTINUOUS, name="offsets")

    #     dist_to_source = {node: -math.inf for node in component}
    #     source = list(component)[0]

    #     dist_to_source[source] = 0

    #     for _ in range(len(component) - 1):
    #         for fr, to in G.edges():
    #             if fr in component and to in component:
    #                 dist_to_source[to] = max(
    #                     dist_to_source[to],
    #                     dist_to_source[fr] + G[fr][to]["weight"]
    #                 )

    #     for _ in range(len(component) - 1):
    #         for fr, to in G.edges():
    #             if fr in component and to in component:
    #                 if dist_to_source[to] < dist_to_source[fr] + G[fr][to]["weight"]:
    #                     m.addConstr(
    #                         dist_to_source[to] <= dist_to_source[fr] +
    #                         G[fr][to]["weight"]
    #                     )


def callback(model, where):
    if where == GRB.Callback.MIPSOL:
        # make solution integer
        x, offsets = model._vars

        G = model._G
        vals = model.cbGetSolution(x)

        G2 = nx.DiGraph()

        for fr, to in x.keys():
            if vals[fr, to] > 0.5:
                G2.add_edge(fr, to, weight=G[fr][to]["weight"])

        # print(len(list(nx.simple_cycles(G2))))

        for cycle in nx.simple_cycles(G2):
            weight = sum(G2[fr][to]["weight"]
                         for fr, to in zip(cycle, cycle[1:] + [cycle[0]]))

            weight_single = weight / len(cycle)

            print(weight)

            for fr, to in zip(cycle, cycle[1:] + [cycle[0]]):
                model.cbLazy(
                    offsets[fr, to] <= -weight_single
                )
                print((fr, to), weight_single)


def augment_graph_lp(G):

    m = gp.Model("mip2")

    x = m.addVars(G.edges(), vtype=GRB.BINARY, name="x")
    offsets = m.addVars(G.edges(), vtype=GRB.CONTINUOUS,
                        name="offsets", lb=-10, ub=0)

    # silent
    m.Params.OutputFlag = 0

    # add degree constraints

    m.addConstrs(
        x.sum(fr, "*") == x.sum("*", fr)
        for fr in G.nodes()
    )

    m.addConstrs(
        x.sum(fr, "*") <= 1 for fr in G.nodes()
    )

    m.addConstrs(
        x.sum("*", to) <= 1 for to in G.nodes()
    )

    obj = gp.quicksum(x[fr, to] * G[fr][to]["weight"] + offsets[fr, to] * x[fr, to]
                      for fr, to in G.edges()) + \
        gp.quicksum(offsets[fr, to] for fr, to in G.edges())

    m.setObjective(obj, GRB.MAXIMIZE)

    m._vars = (x, offsets)
    m._G = G

    m.Params.LazyConstraints = 1
    m.optimize(callback)

    for offset in offsets.keys():
        print(offset, offsets[offset].x)

    # print("Optimal objective: %g" % m.objVal)


def edge_offset_for_cycle(G, fr_to_change, to_to_change):
    lo, hi = -10, 10

    print("finding offset for", fr_to_change, to_to_change)

    # for x in np.linspace(lo, hi, 20):
    #     G[fr_to_change][to_to_change]["weight"] -= x

    #     f = False

    #     try:
    #         nx.find_negative_cycle(
    #             G, fr_to_change, weight=lambda u, v, e: -e["weight"])
    #         f = True

    #     except:
    #         pass

    #     G[fr_to_change][to_to_change]["weight"] += x

    #     print(x, f)

    # exit()

    for _ in range(10):

        mid = (lo + hi) / 2
        f = True

        before = G[fr_to_change][to_to_change]["weight"]
        G[fr_to_change][to_to_change]["weight"] -= mid

        try:

            nx.find_negative_cycle(
                G, fr_to_change, weight=lambda u, v, e: -e["weight"])
            f = False

        except:
            pass

        G[fr_to_change][to_to_change]["weight"] = before

        # print(mid)

        if f:
            hi = mid
        else:
            lo = mid

    # print(lo, hi)

    return lo

    # scores = []

    # for i in trange(1000):
    #     G2 = nx.DiGraph()

    #     for fr, to in G.edges():

    #         # normal distribution
    #         # edge = random.gauss(0, 0.01)
    #         edge = random.uniform(-0.01, 0.01)

    #         G2.add_edge(fr, to, weight=G[fr][to]["weight"] - lo + edge)

    #     score = math.exp(get_best_sol(G2))

    #     if score > 1:
    #         scores.append(score)

    # # plot hist

    # plt.hist(scores, bins=50)

    # plt.show()


def load_graph():

    df = pd.read_parquet("data/rounds/round_1.parquet")

    for _row in df.iterrows():

        G = nx.DiGraph()

        row = {
            key: value
            for key, value in _row[1].items()
        }

        # # print(row["close_time"])

        # # continue

        for key, value in row.items():
            if key.startswith("close_") and not key.startswith("close_time"):

                fr, to = key.split("_")[-1].split(",")

                if value < 0.001 or 1/value < 0.001:
                    continue

                if (fr, to) not in G.edges():
                    G.add_edge(fr, to)
                    G.add_edge(to, fr)

                G[fr][to]["weight"] = math.log(value)
                G[to][fr]["weight"] = math.log(1/value)

        return G


def main():
    df = pd.read_parquet("data/rounds/round_1.parquet")

    for _row in df.iterrows():

        G = nx.DiGraph()

        row = {
            key: value
            for key, value in _row[1].items()
        }

        # # print(row["close_time"])

        # # continue

        for key, value in row.items():
            if key.startswith("close_") and not key.startswith("close_time"):

                fr, to = key.split("_")[-1].split(",")

                if value < 0.001 or 1/value < 0.001:
                    continue

                if (fr, to) not in G.edges():
                    G.add_edge(fr, to)
                    G.add_edge(to, fr)

                G[fr][to]["weight"] = value
                G[to][fr]["weight"] = 1/value

            if key.startswith("volume_"):

                fr, to = key.split("_")[-1].split(",")

                if (fr, to) not in G.edges():
                    G.add_edge(fr, to)
                    G.add_edge(to, fr)

                G[fr][to]["volume"] = value
                G[to][fr]["volume"] = value

        exit()


if __name__ == "__main__":
    main()
