import dwave_sapi2.local as local
import dwave_sapi2.remote as remote
import os
import networkx as nx

import social
import terrorGraphs as tg
import plotTerrorGraphs as ptg

use_dwave = True
save_plot = True

def solve(net, emb, verbose=0, print_res=False):
    print
    print 'net.j:', net.j()

    res = net.solve(solver, emb, s=.25, num_reads=1000, verbose=verbose)
    results = res.results()
    results_not_broken = [x for x in results if not x['broken']]
    print 'total: ', len(results), 'not broken: ', len(results_not_broken)

    if print_res:
        print 'results_not_broken:'
        for r in results_not_broken:
            print ' ', r
    else:
        print results_not_broken[0]
    return results_not_broken[0]

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
        #print 'add_link:', n1, n2, type, edge[0], edge[1]
    return net, nodes_to_indices


def solve_graph(grph, date, print_res=False, pos=None, emb=None, nodes_to_indices=None, save_plot=False):
    net, nodes_to_indices = create_network(grph, nodes_to_indices=nodes_to_indices)
    if emb is None:
        emb = social.Embedding(solver, net, verbose=0)
    res = solve(net, emb, print_res=print_res)

    def set_node_weight(grph, res):
        local_nodes = grph.nodes(data=True)
        local_nodes_to_indices = {n[0]: i for (i, n) in enumerate(local_nodes)}
        spins = res['spins']
        #print 'spins: ', len(spins)

        def set_weight(n, s):
            #print 'set_weight:', n, s
            if s == 3:
                n[1]['weight'] = 0
            else:
                n[1]['weight'] = s

        for (n1, n2) in grph.edges():
            i1 = nodes_to_indices[n1]
            i2 = nodes_to_indices[n2]
            li1 = local_nodes_to_indices[n1]
            li2 = local_nodes_to_indices[n2]
            #print 'i1,i2:', i1, i2, n1, n2, local_nodes[li1], local_nodes[li2]
            s1 = spins[i1]
            s2 = spins[i2]
            set_weight(local_nodes[li1], s1)
            set_weight(local_nodes[li2], s2)

    set_node_weight(grph, res)
    delta = res['delta']
    pos = ptg.plot(date, grph, pos=pos, title='{} (delta = {})'.format(date, delta), save=save_plot)
    return pos, emb, nodes_to_indices

if not use_dwave:
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

date, grph = graphs[-1]
#print 'edges:', grph.edges()
pos, emb, nodes_to_indices = solve_graph(grph, date, print_res=True)
#print nodes_to_indices

grph = nx.Graph()
for (date, g) in graphs:
    grph = nx.compose(grph, g)
    #print
    #print 'edges:', g.edges();
    #print 'edges:', grph.edges()
    solve_graph(grph, date, pos=pos, emb=emb, nodes_to_indices=nodes_to_indices, print_res=False, save_plot=save_plot)