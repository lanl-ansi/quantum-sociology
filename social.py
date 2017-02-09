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
        self.maxNode = 0
        # j is the dictionary of edge weights, with (node1, node2) being the key to the dictionary
        self.j = {}

    def friend(self, n1, n2):
        """ Set the edge from nodes n1 to n2 to be a friend. """
        # using opposite sign convention from Facchetti, et.al. since they minimize -s^Js instead of s^Js
        self.__setEdgeWeight(n1, n2, -1)

    def enemy(self, n1, n2):
        """ Set the edge from nodes n1 to n2 to be an enemy. """
        # using opposite sign convention from Facchetti, et.al. since they minimize -s^Js instead of s^Js
        self.__setEdgeWeight(n1, n2, 1)

    def J(self):
        """ Return the edge weights of the social network. """
        return self.j

    def solve(self, solver, s=0.5, discard=True, verbose=0, **kws):
        """ solve the social network as an Ising model

        Args:
            solver: D-Wave solver object.
            s: scale the network weights by s before adding chain weights.
            discard: True to ignore solutions that violate chain constraints
            verbose: 0 or 1
            **kws: the other keywords are passed to the find_embedding method
        """

        kws['verbose'] = verbose

        # have D-Wave find an embedding of our network into the Chimera
        A = util.get_hardware_adjacency(solver)
        emb = embedding.find_embedding(self.j, A, **kws)
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
        ans = core.solve_ising(solver, h0, j_emb, num_reads=1000)
        if verbose:
            print ans

        # convert the solution back into the original, un-embedded, problem
        if discard:
            res = embedding.unembed_answer(ans['solutions'], new_emb, 'discard', h, self.j)
        else:
            res = embedding.unembed_answer(ans['solutions'], new_emb, 'minimize_energy', h, self.j)

        # pack it up into a solution object that does a bit of post-processing on the solution
        return Solution(ans, res, self.j)

    def __setEdgeWeight(self, n1, n2, w):
        self.maxNode = max(self.maxNode, n1, n2)
        edg = (min(n1,n2), max(n1,n2))
        self.j[edg] = w

class Solution(object):
    """ Solution is used to package up and post-process the results from the Ising model calculation.

    It separates the results into a list of solutions, ordered by energy.
    Each solution is a dictionary with keys 'energy', 'sJs', 'spins', 'num_occ', and 'delta'.
    The 'delta' term is the global balance of the network as calculated in [2] of Fracchetti, et.al.

    """
    def __init__(self, ans, res, j):
        self.ans = ans
        self.j = j
        self.res = [ {'energy': e, 'sJs:': self.__sJs(s, j), 'spins': s, 'num_occ': n, 'delta': self.__delta(s, j)}
                     for (e,s,n) in zip(ans['energies'], res, ans['num_occurrences']) ]

    def results(self):
        return self.res

    def rawResults(self):
        return self.ans

    def __delta(self, s, j):
        sjs = self.__sJs(s, j)
        m = len(j)
        # the plus sign is due to Fracchetti et.al. minimizing -s^Js, while we change the sign of J and minimize s^Js
        # also, I think m is defined incorrectly in Fracchetti et.al.
        return .5 * (m + sjs)

    def __sJs(self, s, j):
        sum = 0
        for nodes in j:
            sum += j[nodes] * s[nodes[0]] * s[nodes[1]]
        return sum

