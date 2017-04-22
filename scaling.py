"""Package for performin scaling study."""
import networkx as nx
import social as soc
import random as ran


def make_random_graph(nnodes,type):
    if type=='complete':
        print('Complete random graph of '+str(nnodes)+' nodes.')
        return nx.complete_graph(nnodes)
    elif type=='erdos':
        print('Erdos-Renyi random graph of '+str(nnodes)+' nodes, p=0.3.')
        return nx.erdos_renyi_graph(nnodes,0.3)
    else:
        return None

def make_social_network(g):
    net = soc.Network()
    for e in g.edges():
        n1 = e[0]
        n2 = e[1]
        r = ran.random()
        if r<=0.5:
            net.friend(n1,n2)
        else:
            net.enemy(n1, n2)
    return net

