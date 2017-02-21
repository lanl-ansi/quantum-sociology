""" Module to solve social network problems.

Reference: Computing global structural balance in large-scale signed social networks, by Giuseppe Facchetti, et. al.
"""

import dwave_sapi2.util as util
import dwave_sapi2.embedding as embedding
import dwave_sapi2.core as core

class Network(object):
    """ Network is used to setup the social network as described in Facchetti, et. al.
    """
    def __init__(self):
        # maxNode is the highest referenced node number.  Nodes assumed to be numbered from 0 to maxNode.
        self._max_node = 0
        # j is the dictionary of edge weights, with (node1, node2) being the key to the dictionary
        self.j = {}

    def friend(self, n1, n2):
        """ Set the edge from nodes n1 to n2 to be a friend. """
        # using opposite sign convention from Facchetti, et.al. since they minimize -s^Js instead of s^Js
        self._set_edge_weight(n1, n2, -1)

    def enemy(self, n1, n2):
        """ Set the edge from nodes n1 to n2 to be an enemy. """
        # using opposite sign convention from Facchetti, et.al. since they minimize -s^Js instead of s^Js
        self._set_edge_weight(n1, n2, 1)

    def J(self):
        """ Return the edge weights of the social network. """
        return self.j

    def solve(self, solver, s=0.5, verbose=0, num_reads=1000):
        """ solve the social network as an Ising model

        Args:
            solver: D-Wave solver object.
            s: scale the network weights by s before adding chain weights.
            discard: True to ignore solutions that violate chain constraints
            verbose: 0 or 1
            **kws: the other keywords are passed to the find_embedding method
        """

        # have D-Wave find an embedding of our network into the Chimera
        A = util.get_hardware_adjacency(solver)
        emb = embedding.find_embedding(self.j, A, verbose=verbose)
        if verbose:
            print 'embedding:', emb

        # use the new embedding to set up a new Ising model that we will
        # actually send to the solver
        h = []
        (h0, j0, jc, new_emb) = embedding.embed_problem(h, self.j, emb, A)
        if verbose:
            print "h0:", h0
            print "j0:", j0
            print "jc:", jc
            print "new embedding:", new_emb

        # scale the network edge weights, j0,  by s before adding the chain weights, jc.
        j_emb = {t: s*j0[t] for t in j0}
        j_emb.update(jc)
        if verbose:
            print "new j (s scaled):", j_emb

        # solve the embedded Ising model
        ans = core.solve_ising(solver, h0, j_emb, num_reads=num_reads)
        if verbose:
            print ans

        # convert the solution back into the original, un-embedded, problem
        res, broken = self._unembed_solution(ans['solutions'], new_emb)

        # pack it up into a solution object that does a bit of post-processing on the solution
        return Solution(ans, res, broken, self.j)

    def _set_edge_weight(self, n1, n2, w):
        self._max_node = max(self._max_node, n1, n2)
        edg = (min(n1,n2), max(n1,n2))
        self.j[edg] = w

    def _unembed_solution(self, sols, emb):
        reses = []
        broken = []
        for sol in sols:
            res = []
            broke = False
            for chain in emb:
                # find all the mappings from physical nodes to this logical node
                res_vals = [sol[c] for c in chain]
                # Are any of the chains in this solution broken? (physical node values unequal?)
                broke |= res_vals.count(res_vals[0]) != len(res_vals)
                # append the value solution using the first element of the logical values
                res.append(res_vals[0])
            broken.append(broke)
            reses.append(res)
        return reses, broken

class Solution(object):
    """ Solution is used to package up and post-process the results from the Ising model calculation.

    It separates the results into a list of solutions, ordered by energy.
    Each solution is a dictionary with keys 'energy', 'sJs', 'spins', 'num_occ', and 'delta'.
    The 'delta' term is the global balance of the network as calculated in [2] of Fracchetti, et.al.

    """
    def __init__(self, ans, res, broken, j):
        self._ans = ans
        self._j = j
        self._res = [{'energy': e, 'sJs:': self._sJs(s, j), 'spins': s, 'num_occ': n, 'delta': self._delta(s, j),
                      'broken': b}
                     for e, s, n, b in zip(ans['energies'], res, ans['num_occurrences'], broken)]

    def results(self):
        return self._res

    def raw_results(self):
        return self._ans

    def _delta(self, s, j):
        sjs = self._sJs(s, j)
        m = len(j)
        # the plus sign is due to Fracchetti et.al. minimizing -s^Js, while we change the sign of J and minimize s^Js
        # also, I think m is defined incorrectly in Fracchetti et.al.
        return .5 * (m + sjs)

    def _sJs(self, s, j):
        sum = 0
        for nodes in j:
            sum += j[nodes] * s[nodes[0]] * s[nodes[1]]
        return sum

