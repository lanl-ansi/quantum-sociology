"""
Use D Wave solutions to explore the dynamics of an imbalanced social network
"""
import dwave_sapi2.local as local
import dwave_sapi2.remote as remote

import settings

import social

import os
import sys
import glob

import json

import plotTerrorGraphs as ptg

import networkx as nx

enemyTypes = {'riv'}
friendTypes = {'all', 'aff'}
enemyValue = 1
friendValue = -1

class BrokenError(Exception):
    def __str__(self):
        return 'Solution has no results where "broken"==False'

class SocialNetSolver:

    @classmethod
    def from_input(cls, solver, input):
        obj = cls()
        obj.solver = solver
        obj.input  = input
        obj.graph = nx.read_graphml(input)
        obj._make_groups_to_dwave_nodes()
        obj.network = obj.make_network_from_graph()
        obj.embedding = social.Embedding(obj.solver,obj.network)
        return obj;

    def copy(self):
        new = SocialNetSolver()
        new.solver = self.solver
        new.input = self.input
        new.graph = self.graph.copy()
        new.groups_to_dwave_nodes = self.groups_to_dwave_nodes
        new.network = self.network.copy()
        new.embedding = self.embedding
        return new

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
            else:
                edge[2]['weight'] = 0
        return net

    def get_nodes(self):
        return self.graph.nodes()

    def remove_node(self, n):

        def node_in_edge(n, e):
            return e[0] == n or e[1] == nrm

        edges_containing_n = [e for e in self.graph.edges(data=True) if node_in_edge(n, e)]
        for e in edges_containing_n:
            e[2]['weight'] = 0
            n0 = self.groups_to_dwave_nodes[e[0]]
            n1 = self.groups_to_dwave_nodes[e[1]]
            self.network.remove_edge(n0, n1)
            self.graph.remove_edge(e[0], e[1])

    def _make_groups_to_dwave_nodes(self):
        # use the fully connected total graph to set the mapping
        # from groups to dwave nodes
        nodes = self.graph.nodes(data=False)
        self.groups_to_dwave_nodes = {n: i for (i, n) in enumerate(nodes)}

    # Solve the social network problem on the given graph.
    def solve_graph(self):
        self.solution = self.network.solve(self.solver, self.embedding, s=0.25, verbose=0, num_reads=1000)
        results = self.solution.results()
        results_not_broken = [x for x in results if not x['broken']]

        #res = results.results()[0]
        if results_not_broken:
            res = results_not_broken[0]
        else:
            #print('Error: solution has no results where "broken"==False')
            #sys.exit(1)
            raise BrokenError()

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

    def get_name(self, n):
        node_data = self.graph.nodes(data=True)
        dwave_node = self.groups_to_dwave_nodes[n]
        name = node_data[dwave_node][1]['name']
        return name

def plot(solver, **kwargs):
    return ptg.plot('xxx', solver.graph, 'yyy', **kwargs)


def sensitivity(social_solver, input, plot_it=False, verbose=False, pos=None):
    results = {}
    nodes = social_solver.get_nodes()
    for n in nodes:
        # social_solver_copy = social_solver
        social_solver_copy = social_solver.copy()
        name = social_solver_copy.get_name(n)
        if verbose:
            print('solving without ' + name)
        social_solver_copy.remove_node(n)
        try:
            social_solver_copy.solve_graph()
            delta = social_solver_copy.delta
            if verbose:
                print(input + ' node ' + name + ' removed: problem solved, delta = ' + str(delta))
            if plot_it:
                plot(social_solver_copy, pos=pos)
        except BrokenError as be:
            delta = -999
            print(input + ' node ' + name + ' removed: ' + str(be))
        results[name] = delta
    return results

def do_runs(inputs, plot_it=False, verbose=False):
    results = {}

    for input in inputs:

        results_input = results[input] = {}

        # Create a SocialNetSolver and obtain an initial solution.
        social_solver = SocialNetSolver.from_input(solver, input)
        social_solver.solve_graph()
        delta = social_solver.delta

        results_input['__initial__'] = delta

        print(input + ' initial problem solved, delta = ' + str(delta))

        if plot_it:
            pos = plot(social_solver)

        results_sensitivity = sensitivity(social_solver, input, plot_it=plot_it, verbose=verbose)
        results_input.update(results_sensitivity)

    return results


if __name__=='__main__':

    use_dwave = True

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

    #input = 'syria_graph_2016-10-00.graphml'
    input_globs = 'syria_graph_20*.graphml'
    inputs = glob.glob(input_globs)

    outputdir = 'results/results-sensitivity'

    results = do_runs(inputs,verbose=True)

    with open(outputdir+'/results.json', 'w') as f:
        json.dump(results, f, sort_keys=True, indent=4)













