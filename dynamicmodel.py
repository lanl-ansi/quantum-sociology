"""
Use D Wave solutions to explore the dynamics of an imbalanced social network
"""
import dwave_sapi2.local as local
import dwave_sapi2.remote as remote

import settings

import social

import os
import sys

import networkx as nx

enemyTypes = {'riv'}
friendTypes = {'all', 'aff'}
enemyValue = 1
friendValue = -1

class SocialNetSolver:

    def __init__(self,solver,input):
        self.solver = solver
        self.input  = input
        self.graph = nx.read_graphml(input)
        self._make_groups_to_dwave_nodes()
        self.network = self.make_network_from_graph()
        self.embedding = social.Embedding(self.solver,self.network)

    # Create network instance by importing a NetworkX graph from GraphML.
    def make_network_from_graph(self):
        edges = self.graph.edges(data=True)
        net = social.Network()
        for edge in edges:
            source = edge[0]
            n1 = int(source)
            target = edge[1]
            n2 = int(target)
            relation = edge[2]['type']
            if relation in enemyTypes:
                edge[2]['weight'] = enemyValue
                net.enemy(n1,n2)
            elif relation in friendTypes:
                net.friend(n1,n2)
                edge[2]['weight'] = friendValue
        return net

    def _make_groups_to_dwave_nodes(self):
        # use the fully connected total graph to set the mapping
        # from groups to dwave nodes
        nodes = self.graph.nodes(data=False)
        self.groups_to_dwave_nodes = {n: i for (i, n) in enumerate(nodes)}

    # Solve the social network problem on the given graph.
    def solve_graph(self):
        self.solution = self.network.solve(self.solver, self.embedding, s=0.5, verbose=1, num_reads=1000)
        results = self.solution.results()
        results_not_broken = [x for x in results if not x['broken']]

        #res = results.results()[0]
        if results_not_broken:
            res = results_not_broken[0]
        else:
            print('Error: solution has no results where "broken"==False')
            sys.exit(1)

        self.set_node_weights(res)

        self.delta = res['delta']
        self.graph.graph['delta'] = self.delta

    def set_node_weights(self, res):
        # for n in self.graph.nodes(data=True):
        #     n[1]['weight'] = 0
        spins = res['spins']

        def set_weight(n, s):
            # print 'set_weight:', n, s
            if s == 3:
                n['weight'] = 0
            else:
                n['weight'] = s

        for (n1, n2) in self.graph.edges():
            i1 = self.groups_to_dwave_nodes[n1]
            i2 = self.groups_to_dwave_nodes[n2]
            s1 = spins[i1]
            s2 = spins[i2]
            set_weight(self.graph.node[n1], s1)
            set_weight(self.graph.node[n2], s2)


    # Evaluate a network edge and determine whether it violates the rule.
    def evaluate_edge_rule_compliance(self):
        ndict = dict(self.graph.nodes(data=True))
        for e in self.graph.edges(data=True):
            weight = e[2]['weight']
            n1 = e[0]
            n2 = e[1]
            w1 = ndict[n1]['weight']
            w2 = ndict[n2]['weight']
            # #fudge
            # if w1==0:
            #     w1=1
            # if w2==0:
            #     w2=1
            same = w1==w2
            viol1 = same&(weight==1)
            viol2 = not(same)&(weight==(-1))
            viol = viol1 | viol2
            print(n1+','+n2+','+str(weight)+','+str(w1)+','+str(w2)+','+str(viol))




if __name__=='__main__':

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

    # Create a SocialNetSolver and obtain an initial solution.
    input = 'syria_graph_2016-10-00.graphml'
    social_solver = SocialNetSolver(solver,input)
    social_solver.solve_graph()

    print(input+' initial problem solved, delta = '+str(social_solver.delta))

    # Evaluate edge rule violations.
    social_solver.evaluate_edge_rule_compliance()






