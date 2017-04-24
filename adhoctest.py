

import dwave_sapi2.local as local
import dwave_sapi2.remote as remote

import settings

import social

import os

import networkx as nx


enemyTypes = {'riv'}
friendTypes = {'all', 'aff'}


# Create network instance by importing a NetworkX graph from GraphML.
def make_network_from_graph(g):
    edges = g.edges(data=True)
    net = social.Network()
    for edge in edges:
        source = edge[0]
        n1 = int(source)
        target = edge[1]
        n2 = int(target)
        relation = edge[2]['type']
        if relation in enemyTypes:
            net.enemy(n1, n2)
        elif relation in friendTypes:
            net.friend(n1, n2)
    return net


if __name__=='__main__':
    input = 'syria_graph_2011-11-00.graphml'

    use_dwave = True

    # Use the D Wave machine or local solver.
    if not use_dwave:
        conn = local.local_connection
        solver = conn.get_solver("c4-sw_sample")
    else:
        # token = os.environ['DWAVE_TOKEN']
        token = settings.DWAVE_TOKEN
        print token
        os.environ['no_proxy'] = 'localhost'
        # print os.environ
        conn = remote.RemoteConnection('https://localhost:10443/sapi', token)
        solver = conn.get_solver("DW2X")


    # Create a network from the GraphML file.
    g = nx.read_graphml(input)
    net = make_network_from_graph(g)

    print(input+' initial problem read in.')

    # Create an embedding.
    embedding = social.Embedding(solver, net, verbose=1)

    # Perform the initial solve.
    solution = net.solve(solver, embedding, s=.25, num_reads=1000)

    # Examine results.
    results = solution.results()
    results_not_broken = [x for x in results if not x['broken']]
    delta = results_not_broken[0]['delta']
    print('delta = '+str(delta))