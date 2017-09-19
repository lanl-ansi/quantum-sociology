"""
Use D Wave solutions to explore the dynamics of an imbalanced social network
"""
import dwave_sapi2.local as local
import dwave_sapi2.remote as remote

import settings

import social

import os
import sys
import random

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
            n1 = self.groups_to_dwave_nodes[source]
            target = edge[1]
            n2 = self.groups_to_dwave_nodes[target]
            relation = edge[2]['type']
            if relation in enemyTypes:
                edge[2]['weight'] = enemyValue
                net.enemy(n1,n2)
            elif relation in friendTypes:
                net.friend(n1,n2)
                edge[2]['weight'] = friendValue
        return net

    def update_network_edges(self):
        edges = self.graph.edges(data=True)
        for edge in edges:
            source = edge[0]
            n1 = self.groups_to_dwave_nodes[source]
            target = edge[1]
            n2 = self.groups_to_dwave_nodes[target]
            ew = edge[2]['weight']

            self.network.set_edge_weight(n1, n2, ew)

    def _make_groups_to_dwave_nodes(self):
        # use the fully connected total graph to set the mapping
        # from groups to dwave nodes
        nodes = self.graph.nodes(data=False)
        self.groups_to_dwave_nodes = {n: i for (i, n) in enumerate(nodes)}

    # Solve the social network problem on the given graph.
    def solve_graph(self):
        self.solution = self.network.solve(self.solver, self.embedding, s=0.5, verbose=0, num_reads=1000)
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
        nviol = 0
        eviols = []
        for e in self.graph.edges(data=True):
            # RMR The following line is suspect, ignored edges (e.g. 'spl') seem to have no 'weight' attribute
            ew = e[2]['weight']
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
            viol1 = same and (ew==1)
            viol2 = not(same) and (ew==(-1))
            viol = viol1 or viol2
            if viol:
                eviols.append((n1,n2))
                nviol = nviol+1
            #print(n1+','+n2+','+str(ew)+','+str(w1)+','+str(w2)+','+str(viol))
        #print('nviol = '+str(nviol))
        return eviols

# Change models:
# Probability that an edge with change on a give step, given the number of edges,
#  and the number of violations:

# Proportional (with boost factor) to the relative level of imbalance in the network.
def imbalance_change_prob(pfactor,nedges,nviolations):
    return min(pfactor*float(nviolations)/float(nedges),1)

# Equal probability (with boost factor) that a violation instance will change.
def violation_change_prob(pfactor,nviolations):
    if nviolations>0:
        return min(pfactor/float(nviolations),1)
    else:
        return 0

# Constant a priori probability with boost factor.
def const_prob(pfactor,pconstant):
    return min(pfactor*pconstant,1)


if __name__=='__main__':

    use_dwave = True
    input = 'syria_graph_2016-10-00.graphml'
    pfactor = 1
    nsteps = 40
    pmodel = 'imbalance' # from {imbalance,violation,constant'}
    pconst = 0.5
    write_graphs = True
    outputdir = 'results/results-dynamic'

    # Use the D Wave machine or local solver.
    if not use_dwave:
        conn = local.local_connection
        solver = conn.get_solver("c4-sw_sample")
    else:
        # token = os.environ['DWAVE_TOKEN']
        token = settings.DWAVE_TOKEN_RMR
        print token
        os.environ['no_proxy'] = 'localhost'
        # print os.environ
        conn = remote.RemoteConnection('https://localhost:10443/sapi', token)
        solver = conn.get_solver("DW2X")

    # Create a SocialNetSolver and obtain an initial solution.
    social_solver = SocialNetSolver(solver,input)
    social_solver.solve_graph()
    delta = social_solver.delta
    print(input+' initial problem solved, delta = '+str(delta))

    # Make an edge dictionary for addressing edge data.
    graph = social_solver.graph
    edges = graph.edges(data=True)
    nedges = len(edges)
    edict = dict(zip([(e[0],e[1]) for e in edges],edges))

    # Open a file for results.

    caseid = input[0:input.index('.graphml')]
    output = outputdir+'/'+'dynamicModel_'+caseid+'p_'+pmodel+'.csv'
    fout = open(output,'wb')
    fout.write('step,nviols,p,nchanged,delta\n')

    for i in range(0,nsteps):

        # Evaluate edge rule violations.
        eviols = social_solver.evaluate_edge_rule_compliance()
        neviols = len(eviols)
        print('number of edge violations = '+str(neviols))

        # Calculate a proobability of fliping the sign of an edge that violates
        #  the edge rule.
        if pmodel == 'imbalance':
            p = imbalance_change_prob(pfactor,nedges,neviols)
        elif pmodel == 'violation':
            p = violation_change_prob(pfactor,neviols)
        elif pmodel == 'constant':
            p = const_prob(pfactor,pconst)
        else:
            p = pconst
        print('probability of edge change = '+str(p))

        # For each rule violation on edge e switch edge sign
        #  if random number in [0,1] exceeds p.
        nchanged = 0
        for e in eviols:
            r = random.random()
            if r<=p:
                edge = edict[e]
                ew = edge[2]['weight']
                edge[2]['weight'] = -ew
                nchanged = nchanged + 1
                print('Edge '+str(e)+' changed.')
        print(str(nchanged)+' edges changed of '+str(neviols)+' violations.')
        print('Iteration '+str(i)+' problem solved, delta = ' + str(delta))
        fout.write(str(i)+',' + str(neviols) + ',' + str(p) + ',' + str(nchanged) + ',' + str(delta) + '\n')

        # Write results to gefx and graphml
        if write_graphs:
            g = social_solver.graph
            gfile_prefix = outputdir+'/'+'dynamicModel_'+caseid+'p_'+pmodel+'_'+str(i)
            gexfout = gfile_prefix+'.gexf'
            nx.write_gexf(g,gexfout)
            graphmlout = gfile_prefix+'.graphml'
            nx.write_graphml(g,graphmlout)

        # Recompute the node solutions and delta.
        social_solver.update_network_edges()
        social_solver.solve_graph()
        delta = social_solver.delta


    fout.close()













