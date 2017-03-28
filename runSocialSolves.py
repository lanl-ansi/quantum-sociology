import matplotlib.pyplot as plt

import dwave_sapi2.local as local
import dwave_sapi2.remote as remote
import os
import networkx as nx

import social
import terrorGraphs as tg
import plotTerrorGraphs as ptg

use_dwave = False
save_plot = False

class StanfordDwave(object):

    def __init__(self, solver, groups, links):
        self._enemyTypes = {'riv'}
        self.solver = solver
        self.graphs = tg.create_graphs_by_date(groups, links)
        self._compose_graphs()
        self._make_groups_to_dwave_nodes()
        self._make_embedding()

    def _compose_graphs(self):
        # also strips off the date from the self.graphs tuples
        comp_graph = nx.Graph()
        graphs = []
        for (date, grph) in self.graphs:
            comp_graph = nx.compose(comp_graph, grph)
            comp_graph.graph['date'] = date
            graphs.append(comp_graph)
        self.graphs = graphs

    def _make_embedding(self):
        # use the fully connected total graph to set the embedding
        # from groups to dwave nodes
        grph = self.graphs[-1]
        net = self._create_network(grph)
        self.embedding = social.Embedding(self.solver, net, verbose=0)

    def _add_link(self, net, n1, n2, type):
        if type in self._enemyTypes:
            net.enemy(n1, n2)
        else:
            net.friend(n1, n2)

    def _make_groups_to_dwave_nodes(self):
        # use the fully connected total graph to set the mapping
        # from groups to dwave nodes
        grph = self.graphs[-1]
        nodes = grph.nodes(data=False)
        self.groups_to_dwave_nodes = {n: i for (i, n) in enumerate(nodes)}

    def _create_network(self, graph):
        nodes = graph.nodes(data=True)
        net = social.Network()
        for edge in graph.edges(data=True):
            n1 = self.groups_to_dwave_nodes[edge[0]]
            n2 = self.groups_to_dwave_nodes[edge[1]]
            type = edge[2]['type']
            self._add_link(net, n1, n2, type)
            #print 'add_link:', n1, n2, type, edge[0], edge[1]
        return net


    def _solve(self, net, verbose=0, print_res=False):
        print
        print 'net.j:', net.j()

        res = net.solve(self.solver, self.embedding, s=.25, num_reads=1000, verbose=verbose)
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

    def _set_node_weights(self, grph, res):
        spins = res['spins']

        # print 'spins: ', len(spins)

        def set_weight(n, s):
            # print 'set_weight:', n, s
            if s == 3:
                n['weight'] = 0
            else:
                n['weight'] = s

        for (n1, n2) in grph.edges():
            i1 = self.groups_to_dwave_nodes[n1]
            i2 = self.groups_to_dwave_nodes[n2]
            s1 = spins[i1]
            s2 = spins[i2]
            set_weight(grph.node[n1], s1)
            set_weight(grph.node[n2], s2)


    def solve_graphs(self, verbose=0, print_res=False, save_plot=False):

        for grph in self.graphs:
            net = self._create_network(grph)
            res = self._solve(net, verbose=verbose, print_res=print_res)

            self._set_node_weights(grph, res)

            delta = res['delta']
            grph.graph['delta'] = delta

if __name__ == '__main__':

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

    def plot_deltas(graphs):
        deltas = []
        dates = []
        for grph in graphs[:-1]:
            delta = grph.graph['delta']
            date = grph.graph['date']
            deltas.append(delta)
            dates.append(date)

        # make the x axis just the indices
        dn = range(len(dates))

        plt.figure()
        plt.plot(dn, deltas)
        xtickVals = dn[::10] + dn[-1:]
        xtickLabels = dates[::10] + dates[-1:]
        plt.xticks(xtickVals, xtickLabels, rotation='vertical')
        plt.grid()
        #plt.margins(0.2)
        plt.subplots_adjust(bottom=0.2)
        plt.show()

    def plot(graphs):
        # use the fully connected total graph to set the embedding
        # from groups to dwave nodes
        grph = graphs[-1]
        pos = nx.spring_layout(grph, iterations=1000)

        for grph in graphs:
            delta = grph.graph['delta']
            date = grph.graph['date']
            pos = ptg.plot(date, grph, pos=pos, title='{} (delta = {})'.format(date, delta), save=save_plot)

    terrorFile = "syria.json"

    groups, links = tg.extract_data_json(terrorFile)

    stanford_dwave = StanfordDwave(solver, groups, links)

    stanford_dwave.solve_graphs()

    plot_deltas(stanford_dwave.graphs)
    plot(stanford_dwave.graphs)
