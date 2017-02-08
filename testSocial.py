import social
import dwave_sapi2.local as local
import dwave_sapi2.remote as remote

net = social.Network()
net.enemy(0,1)
net.friend(0,2)
net.enemy(1,2)

#print net.__dict__

if True:
    conn = local.local_connection
    solver = conn.get_solver("c4-sw_sample")
else:
    conn = remote.RemoteConnection('https://localhost:10443/sapi', 'LANL-2690b414a0be9fc9af1d82d00bfe1ef23936c99e')
    solver = conn.get_solver("DW2X")

res = net.solve(solver, discard=True, verbose=0)

print
print 'J:', net.J()
print
print 'results:'
for r in res.results():
    print r
