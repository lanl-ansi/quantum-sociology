import dwave_sapi2.util as util
import dwave_sapi2.embedding as embedding
import dwave_sapi2.core as core

class Network(object):
    def __init__(self):
        self.maxNode = 0
        self.j = {}

    def friend(self, n1, n2):
        self.maxNode = max(self.maxNode, n1, n2)
        self.j[(n1,n2)] = -1

    def enemy(self, n1, n2):
        self.maxNode = max(self.maxNode, n1, n2)
        self.j[(n1,n2)] = 1

    def J(self):
        return self.j

    def solve(self, solver, s=0.5, discard=True, **kws):
        A = util.get_hardware_adjacency(solver)
        emb = embedding.find_embedding(self.j, A, **kws)
        print 'embedding:', emb

        h = []
        (h0, j0, jc, new_emb) = embedding.embed_problem(h, self.j, emb, A)
        #print "h0:", h0
        print "j0:", j0
        print "jc:", jc
        print "new embedding:", new_emb

        emb_j = {t: s*j0[t] for t in j0}
        emb_j.update(jc)
        print "new j (s scaled):", emb_j

        ans = core.solve_ising(solver, h0, emb_j, num_reads=1000)
        #print ans

        if discard:
            res = embedding.unembed_answer(ans['solutions'], new_emb, 'discard', h, self.j)
        else:
            res = embedding.unembed_answer(ans['solutions'], new_emb, 'minimize_energy', h, self.j)

        return Solution(ans, res, self.j)

class Solution(object):
    def __init__(self, ans, res, j):
        self.ans = ans
        self.res = [ {'energy': e, 'sJs:': self.__sJs__(s, j), 'spins': s, 'num_occ': n}
                     for (e,s,n) in zip(ans['energies'],res, ans['num_occurrences']) ]

    def __sJs__(self, s, j):
        sum = 0
        for nodes in j:
            sum += j[nodes]*s[nodes[0]]*s[nodes[1]]
        return sum

    def results(self):
        return self.res

    def rawResults(self):
        return self.ans
