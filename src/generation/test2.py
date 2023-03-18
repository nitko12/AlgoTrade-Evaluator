import networkx as nx
import gurobipy as gp
from gurobipy import GRB
from pprint import pprint

from algorithms import get_best_sol


def main():
    G = nx.DiGraph()

    G.add_edge("USD", "ETH", weight=-1, volume=1)
    G.add_edge("ETH", "BNB", weight=-1, volume=2)
    G.add_edge("BNB", "BTC", weight=1, volume=3)
    G.add_edge("BTC", "EUR", weight=-1, volume=4)
    G.add_edge("EUR", "ETH", weight=2, volume=5)

    # print(nx.negative_edge_cycle(G))

    # print(get_best_sol(G))

    # G2, offset = augment_graph(G)

    # print(offset)

    print(get_best_sol(G))


if __name__ == "__main__":
    main()
