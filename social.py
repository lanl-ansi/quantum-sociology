""" Module to solve social network problems.

Reference: Computing global structural balance in large-scale signed social networks, by Giuseppe Facchetti, et. al.
"""

import dwave_sapi2.util as dw_util
import dwave_sapi2.embedding as dw_embedding
import dwave_sapi2.core as dw_core
import settings

def _all_equal(vals):
    """ Returns True if all values are equal """
    return vals.count(vals[0]) == len(vals)

def _sJs(s, j):
    sum = 0
    for nodes in j:
        sum += j[nodes] * s[nodes[0]] * s[nodes[1]]
    return sum

def _delta(s, j):
    sjs = _sJs(s, j)
    m = len(j)
    # the plus sign is due to Fracchetti et.al. minimizing -s^Js, while we change the sign of j and minimize s^Js
    # also, I think m is defined incorrectly in Fracchetti et.al.
    return .5 * (m + sjs)

class Ising(object):
    def __init__(self, h0, j_emb, new_emb, j):
        self._h0 = h0
        self._j_emb = j_emb
        self._new_emb = new_emb
        self._j = j

    def new_emb(self):
        return self._new_emb

    def j(self):
        return self._j

    def solve(self, solver, num_reads):
        # solve the embedded Ising model
        embedded_results = dw_core.solve_ising(solver, self._h0, self._j_emb, num_reads=num_reads)
        return embedded_results

class Embedding(object):
    def __init__(self, solver, network, verbose=0):
        self._verbose = verbose
        # have D-Wave find an embedding of our network into the Chimera
        self._A = dw_util.get_hardware_adjacency(solver)
        self._emb = dw_embedding.find_embedding(network.j(), self._A, \
                                                verbose=verbose, timeout=settings.EMBEDDING_TIMEOUT)
        if verbose:
            print 'embedding:', self._emb

    def embed_problem(self, s, j):
        """ Use the new embedding to set up a new Ising model that we will
            actually send to the solver
        """
        h = []
        (h0, j0, jc, new_emb) = dw_embedding.embed_problem(h, j, self._emb, self._A)
        if self._verbose:
            print "h0:", h0
            print "j0:", j0
            print "jc:", jc
            print "new embedding:", new_emb

        # scale the network edge weights, j0,  by s before adding the chain weights, jc.
        j_emb = {t: s*j0[t] for t in j0}
        j_emb.update(jc)
        if self._verbose:
            print "new j (s scaled):", j_emb

        return Ising(h0, j_emb, new_emb, j)

    def unembed_solution(self, embedded_results, ising):
        unembedded_results = []
        broken = []
        for sol in embedded_results['solutions']:
            unemb_sol = []
            broke = False
            for chain in ising.new_emb():
                # find all the mappings from physical nodes to this logical node
                chain_vals = [sol[c] for c in chain]
                # Are any of the chains in this solution broken? (All chain values should be the same.)
                _chain_all_equals = _all_equal(chain_vals)
                broke |= not _chain_all_equals
                # append the value solution using the first element of the logical values
                unemb_sol.append(chain_vals[0] if _chain_all_equals else 0)
            broken.append(broke)
            unembedded_results.append(unemb_sol)

         # pack it up into a solution object that does a bit of post-processing on the solution
        return Solution(embedded_results, unembedded_results, broken, ising)


class Network(object):
    """ Network is used to setup the social network as described in Facchetti, et. al.
    """
    def __init__(self):
        # maxNode is the highest referenced node number.  Nodes assumed to be numbered from 0 to maxNode.
        self._max_node = 0
        # j is the dictionary of edge weights, with (node1, node2) being the key to the dictionary
        self._j = {}

    def friend(self, n1, n2):
        """ Set the edge from nodes n1 to n2 to be a friend. """
        # using opposite sign convention from Facchetti, et.al. since they minimize -s^Js instead of s^Js
        self._set_edge_weight(n1, n2, -1)

    def enemy(self, n1, n2):
        """ Set the edge from nodes n1 to n2 to be an enemy. """
        # using opposite sign convention from Facchetti, et.al. since they minimize -s^Js instead of s^Js
        self._set_edge_weight(n1, n2, 1)

    def j(self):
        """ Return the edge weights of the social network. """
        return self._j

    def solve(self, solver, emb, s=0.5, verbose=0, num_reads=1000):
        """ solve the social network as an Ising model

        Args:
            solver: D-Wave solver object.
            s: scale the network weights by s before adding chain weights.
            discard: True to ignore solutions that violate chain constraints
            verbose: 0 or 1
        """

        # embed the problem into the D-Wave architecture
        ising = emb.embed_problem(s, self._j)

        # solve the embedded Ising model
        embedded_results = ising.solve(solver, num_reads=num_reads)
        if verbose:
            print embedded_results

        # convert the solution back into the original, un-embedded, problem
        return emb.unembed_solution(embedded_results, ising)


    def _set_edge_weight(self, n1, n2, w):
        self._max_node = max(self._max_node, n1, n2)
        edg = (min(n1,n2), max(n1,n2))
        self._j[edg] = w

class Solution(object):
    """ Solution is used to package up and post-process the results from the Ising model calculation.

    It separates the results into a list of solutions, ordered by energy.
    Each solution is a dictionary with keys 'energy', 'sJs', 'spins', 'num_occ', and 'delta'.
    The 'delta' term is the global balance of the network as calculated in [2] of Fracchetti, et.al.

    """
    def __init__(self, orig_results, unembedded_results, broken, ising):
        self._orig_results = orig_results
        j = ising.j()
        self._results = [{'energy': e, 'sJs:': _sJs(s, j), 'spins': s, 'num_occ': n,
                          'delta': _delta(s, j), 'broken': b}
                         for e, s, n, b in zip(orig_results['energies'], unembedded_results,
                                               orig_results['num_occurrences'], broken)]

    def results(self):
        return self._results

    def raw_results(self):
        return self._orig_results
