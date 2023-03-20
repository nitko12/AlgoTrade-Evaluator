import networkx as nx
import json
import gurobipy as gp
from gurobipy import GRB
import math
from pprint import pprint
from tqdm import tqdm


def get_best_sol(G):
    m = gp.Model("mip2")

    # Create variables

    # silent

    m.setParam("OutputFlag", 0)

    # set numerical focus

    m.setParam("NumericFocus", 3)

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
        # print(cycle)

        balance = 1

        print(cycle)

        mn_scale = 1

        for i in range(len(cycle)):
            fr = cycle[i]
            to = cycle[(i+1) % len(cycle)]

            balance *= G[fr][to]["original_weight"]

            # balance = min(balance, 100_000_000_000)

            mn_scale = float(
                f"{min(mn_scale, G[fr][to]['volume'] / balance):.10f}")

            # print(balance)

            print(fr, to, G[fr][to]["volume"])

        best += balance

        print(balance * mn_scale)

    return best


def main():
    d = json.load(open("snapshot.json", "r"))

    G = nx.DiGraph()

    pairs = set()

    for k, v in d.items():
        pairs.add(k.split("_")[1])

    for pair in pairs:
        fr, to = pair.split(",")

        if d[f"close_{fr},{to}"] < 0.0001 or d[f"close_{fr},{to}"] > 1000000:
            continue

        if 1 / d[f"close_{fr},{to}"] < 0.0001 or 1 / d[f"close_{fr},{to}"] > 1000000:
            continue

        if d[f"close_{to},{fr}"] < 0.0001 or d[f"close_{to},{fr}"] > 1000000:
            continue

        if 1 / d[f"close_{to},{fr}"] < 0.0001 or 1 / d[f"close_{to},{fr}"] > 1000000:
            continue

        if d[f"volume_{fr},{to}"] < 10:
            continue

        if d[f"volume_{to},{fr}"] < 10:
            continue

        G.add_edge(
            fr, to, weight=math.log(d[f"close_{fr},{to}"]), original_weight=d[f"close_{fr},{to}"], volume=d[f"volume_{fr},{to}"])

    banned = ["LUN", "AE"]
    for node in banned:
        G.remove_node(node)

    # find components

    components = list(nx.weakly_connected_components(G))

    # for component in components:
    #     print(component)

    sol = get_best_sol(G)

    print(sol)


if __name__ == '__main__':
    main()
