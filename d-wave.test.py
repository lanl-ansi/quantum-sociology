import dwave_sapi2.remote as remote
import dwave_sapi2.local as local
import dwave_sapi2.core as core
import dwave_sapi2.util as util
import dwave_sapi2.embedding as embedding
import numpy as np

#conn = remote.RemoteConnection('https://localhost:10443/sapi', 'LANL-2690b414a0be9fc9af1d82d00bfe1ef23936c99e')
#solver = conn.get_solver("DW2X")

conn = local.local_connection
solver = conn.get_solver("c4-sw_sample")

#A = util.get_hardware_adjacency(solver)
A = util.get_chimera_adjacency(1,1,4)

S_size = 3
S = {}

for i in range(S_size):
    for j in range(S_size):
        S[(i,j)] = 1

print S

emb = embedding.find_embedding(S, A, verbose=1)
print emb

Q = {(0,0): 1, (1,1): 1, (2,2): 1, (0,1): 1, (0,2): -2, (1,2): -2}

(h, j, ising_offset) = util.qubo_to_ising(Q)

print "h:", h
print "j:", j
print "ising_offset:", ising_offset

(h0, j0, jc, new_emb) = embedding.embed_problem(h, j, emb, A)

print "h0:", h0
print "j0:", j0
print "jc:", jc
print "new_emb:", new_emb

emb_j = j0.copy()
emb_j.update(jc)
print "emb_j:",emb_j

ans = core.solve_ising(solver, h0, emb_j, num_reads=1000)
print ans
# for x in ans['solutions']:
#     for y in new_emb:
#         print (x[y[0]]+1)/2
#     print '----'
res = embedding.unembed_answer(ans['solutions'], new_emb, 'discard', h, j)
print (np.array(res)+1)/2