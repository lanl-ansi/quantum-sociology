import dwave_sapi2.local as local
import dwave_sapi2.remote as remote
import os

import social
import terrorGraphs as tg
import networkx as nx

def solve(net, emb, verbose=0):
    print
    print 'net.j:', net.j()

    res = net.solve(solver, emb, s=.25, num_reads=1000, verbose=verbose)

    print 'res.results:'
    for r in res.results():
        print ' ', r

def add_link(net, n1, n2, type):
    enemyTypes = {'riv'}
    if type in enemyTypes:
        net.enemy(n1, n2)
    else:
        net.friend(n1, n2)

def create_network(graph, nodes_to_indices=None):

    nodes = graph.nodes(data=True)
    if nodes_to_indices is None:
        nodes_to_indices = {n[0]: i for (i,n) in enumerate(nodes)}
    net = social.Network()
    for edge in graph.edges(data=True):
        n1 = nodes_to_indices[edge[0]]
        n2 = nodes_to_indices[edge[1]]
        type = edge[2]['type']
        add_link(net, n1, n2, type)
        #print 'add_link:', n1, n2, type
    return net, nodes_to_indices

if False:
    conn = local.local_connection
    solver = conn.get_solver("c4-sw_sample")
else:
    token = os.environ['DWAVE_TOKEN']
    print token
    os.environ['no_proxy'] = 'localhost'
    #print os.environ
    conn = remote.RemoteConnection('https://localhost:10443/sapi', token)
    solver = conn.get_solver("DW2X")

terrorFile = "syria.json"

groups, links = tg.extract_data_json(terrorFile)
graphs = tg.create_graphs_by_date(groups, links)

full_net, nodes_to_indices = create_network(graphs[-1][1])
emb = social.Embedding(solver, full_net, verbose=1)
solve(full_net, emb)
