import math
import bisect
import networkx as nx

import stanfordTerror as st

def create_graph(groups, links):
    grph = nx.Graph()
    grph.add_nodes_from([(g['id'], g) for g in groups])
    edges = [(l['group1'], l['group2'], l) for l in links if l['group2'] != l['group1']]
    grph.add_edges_from(edges)
    return grph


def create_graphs_by_date(groups, links):
    links = sorted(links, key=lambda l: l['date'])
    keys = [l['date'] for l in links]
    lo = 0
    graphs = []
    while lo < len(keys):
        to = bisect.bisect_right(keys, keys[lo], lo=lo)
        #print lo, to, keys[lo:to]
        graphs.append((keys[lo], create_graph(groups, links[lo:to])))
        lo = to
    graphs.append(('total', create_graph(groups, links)))
    return graphs

def extract_data_json(filename):
    data = st.getData(filename)
    groups, links = st.extract(data)
    return groups, links