import social
import dwave_sapi2.local as local
import dwave_sapi2.remote as remote

net = social.Network()

A = 0
B = 1
C = 2
D = 3
E = 4

if False:
    net.enemy(0,1)
    net.friend(0,2)
    net.enemy(1,2)
else:
    net.enemy(A,B)
    net.enemy(B,C)
    net.friend(C,D)
    net.friend(D,E)
    net.enemy(E,A)
    net.enemy(A,D)
    net.friend(B,E)

#print net.__dict__

if True:
    conn = local.local_connection
    solver = conn.get_solver("c4-sw_sample")
else:
    conn = remote.RemoteConnection('https://localhost:10443/sapi', 'LANL-2690b414a0be9fc9af1d82d00bfe1ef23936c99e')
    solver = conn.get_solver("DW2X")

res = net.solve(solver, discard=True, verbose=1)

print
print 'net.J:', net.J()
print
print 'res.results:'
for r in res.results():
    print r
