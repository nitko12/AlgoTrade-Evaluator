import random
import pandas as pd
from pprint import pprint
import networkx as nx
import math
import gurobipy as gp
from gurobipy import GRB
from tqdm import tqdm


def augment_sample(sample):

    all_pairs = set()

    closes = {}
    volumes = {}

    for k, v in sample.items():
        pair = k.split('_')[-1]

        all_pairs.add(pair)

        if k.startswith('close_') and not k.startswith('close_time'):
            closes[pair] = v
        if k.startswith('volume_'):
            volumes[pair] = v

    all_pairs = all_pairs & set(closes.keys()) & set(volumes.keys())
    all_currency = set(
        [pair.split(',')[0] for pair in all_pairs]
    ) | set(
        [pair.split(',')[1] for pair in all_pairs])

    G = nx.DiGraph()

    for pair in all_pairs:
        fr, to = pair.split(',')

        G.add_edge(fr, to, weight=-math.log(closes[pair]),
                   volume=volumes[pair], original_weight=closes[pair])
        G.add_edge(to, fr, weight=-math.log(
            1 / closes[pair]), volume=volumes[pair], original_weight=1 / closes[pair])

    # remove everything not connected to USDT

    for node in list(G.nodes):
        if node != 'USDT':
            if not nx.has_path(G, 'USDT', node):
                G.remove_node(node)

    # print(G)

    lo, hi = -10, 10

    for _ in range(30):
        mid = (lo + hi) / 2

        f = False
        # for currency in all_currency:
        try:
            nx.find_negative_cycle(
                G, "USDT", weight=lambda u, v, e: e['weight'] + mid)
            f = True
        except:
            pass

        if f:
            lo = mid
        else:
            hi = mid

    offset = (lo + hi) / 2 + 0.0001

    for u, v, e in G.edges.data():
        e['weight'] += offset

    try:
        nx.find_negative_cycle(
            G, "USDT")
        raise Exception('Negative cycle found')
    except nx.NetworkXException:
        pass

    m = gp.Model()

    # m.params.OutputFlag = 0

    offsets = m.addVars(G.edges, lb=-10*offset, ub=0)

    dist = {
        node: 1e9
        for node in G.nodes
    }
    dist['USDT'] = 0

    # bellman ford

    for _ in range(len(G.nodes) - 1):
        for u, v, e in G.edges.data():
            if dist[v] > dist[u] + e['weight']:

                m.addConstr(
                    dist[v] >= dist[u] + e['weight'] + offsets[(u, v)]
                )

                dist[v] = dist[u] + e['weight']
            else:
                m.addConstr(
                    dist[v] <= dist[u] + e['weight'] + offsets[(u, v)]
                )

    for u, v, e in G.edges.data():
        if dist[v] > dist[u] + e['weight']:
            raise Exception('Negative cycle found')
        else:
            m.addConstr(
                dist[v] <= dist[u] + e['weight'] + offsets[(u, v)]
            )

    for fr, to in G.edges:
        m.addConstr(
            offsets[(fr, to)] + G[fr][to]['weight'] +
            offsets[(to, fr)] + G[to][fr]['weight'] <= -math.log(0.9)
        )

        # m.addConstr(
        #     offsets[(fr, to)] + G[fr][to]['weight'] +
        #     offsets[(to, fr)] + G[to][fr]['weight'] <= 0.999
        # )

    m.setObjective(
        gp.quicksum(
            offsets[edge]
            for edge in G.edges
        ),
        GRB.MINIMIZE
    )

    m.optimize()

    # for edge in G.edges:
    #     print(edge, offsets[edge].x)

    for u, v, e in G.edges.data():
        e['weight'] += offsets[(u, v)].x + 0.0001

    try:
        nx.find_negative_cycle(
            G, "USDT")
        raise Exception('Negative cycle found')
    except nx.NetworkXException:
        pass

    for u, v, e in G.edges.data():
        e['weight'] = math.exp(-e['weight'])

    row_out = {}

    for u, v, e in G.edges.data():
        offset = random.gauss(0, 0.0001)

        row_out[f'close_{u},{v}'] = e['weight'] * (1 + offset)
        row_out[f'volume_{u},{v}'] = e['volume']
        row_out[f'original_close_{u},{v}'] = e['original_weight']

    return row_out

    # for u, v, e in G.edges.data():
    #     print(u, v,
    #           abs(e['weight'] - e['original_weight']))


def main():
    df = pd.read_parquet('data/rounds/round_3.parquet')

    # take first 100 samples

    # sort by time

    # df["time"] = df["time_SUSHI,BIDR"]

    # for column in df.columns:
    #     print(column)

    df = df.sort_values('time')

    df = df.iloc[:1800]

    l = []

    for data_sample in tqdm(df.iloc, total=len(df)):
        out = augment_sample(data_sample.to_dict())

        print(out)

        exit()

        out["time"] = data_sample["time"]

        l.append(out)

    data_sample = pd.DataFrame(l)

    data_sample.to_parquet('data/rounds/round_3_augmented.parquet')

    # pprint(data_sample.to_dict())


if __name__ == '__main__':
    main()
