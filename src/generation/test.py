import networkx as nx
import gurobipy as gp
from gurobipy import GRB

from algorithms import load_graph, get_best_sol, augment_graph


def callback(model, where):
    if where == GRB.Callback.MIPSOL:

        G2 = nx.DiGraph()

        x, offsets, G = model._vars

        vals = model.cbGetSolution(x)

        for fr, to in x.keys():
            if vals[fr, to] > 0.5:
                G2.add_edge(fr, to, weight=G[fr][to]["weight"])

        neg_cycle = nx.negative_edge_cycle(G2)

        print(neg_cycle)


def augment_graph_lp(G):

    m = gp.Model("augment")

    x = m.addVars(G.edges(), vtype=GRB.BINARY, name="x")
    offsets = m.addVars(G.edges(), vtype=GRB.CONTINUOUS,
                        name="offsets", lb=-GRB.INFINITY, ub=0)

    for fr, to in G.edges():
        m.addConstr(offsets[fr, to] <= 0)

    # add deg 2 constraints

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
                      for fr, to in G.edges())

    obj += gp.quicksum(offsets[fr, to] for fr, to in G.edges())

    m.setObjective(obj, GRB.MAXIMIZE)

    m._vars = x, offsets, G
    m.params.LazyConstraints = 1
    m.params.OutputFlag = 0
    m.optimize(callback)

    print("Optimal value:", m.objVal)

    for offset in offsets.values():
        print(offset.x)


def main():
    # G = nx.DiGraph()

    G = load_graph()

    G, delta = augment_graph(G)

    for fr, to in G.edges():

        G[fr][to]["weight"] = - G[fr][to]["weight"]

    # offset = 100

    # G.add_edge("USDT", "ETH", weight=1+100)
    # G.add_edge("ETH", "BNB", weight=1+100)
    # G.add_edge("BNB", "BTC", weight=-1+100)
    # G.add_edge("BTC", "EUR", weight=1+100)
    # G.add_edge("EUR", "ETH", weight=-2+100)

    m = gp.Model("bellman_ford")

    offsets = m.addVars(G.edges(), vtype=GRB.CONTINUOUS,
                        name="x", lb=-10, ub=0)

    # bellman ford

    dist = {
        node: GRB.INFINITY if node != "USDT" else 0
        for node in G.nodes()
    }

    for _ in range(len(G.nodes()) - 1):
        for fr, to in G.edges():

            if dist[to] > dist[fr] + G[fr][to]["weight"]:
                dist[to] = dist[fr] + G[fr][to]["weight"]

                m.addConstr(dist[to] >= dist[fr] + G[fr][to]
                            ["weight"] + offsets[fr, to])
            else:
                m.addConstr(dist[to] <= dist[fr] + G[fr][to]
                            ["weight"] + offsets[fr, to])

    for fr, to in G.edges():
        m.addConstr(dist[to] <= dist[fr] + G[fr][to]
                    ["weight"] + offsets[fr, to])

    m.setObjective(gp.quicksum(offsets[fr, to]
                   for fr, to in G.edges()), GRB.MINIMIZE)

    m.optimize()

    for offset in offsets:
        print(offsets[offset].x + G[offset[0]][offset[1]]["weight"])


if __name__ == "__main__":
    main()
