import social
import dwave_sapi2.local as local
import dwave_sapi2.remote as remote
import os

A = 0
B = 1
C = 2
D = 3
E = 4

def fig1A4():
    net = social.Network()
    net.enemy(A,B)
    net.friend(A,C)
    net.enemy(B,C)
    return net

def fig1B():
    net = social.Network()
    net.enemy(A,B)
    net.enemy(B,C)
    net.friend(C,D)
    net.friend(D,E)
    net.enemy(E,A)
    net.enemy(A,D)
    net.friend(B,E)
    return net

def fig1C():
    net = social.Network()
    net.friend(A,B)
    net.enemy(B,C)
    net.friend(C,D)
    net.friend(D,E)
    net.friend(E,A)
    net.friend(A,D)
    net.friend(B,E)
    return net

def solve(net):
    res = net.solve(solver, discard=True, verbose=0)

    print
    print 'net.J:', net.J()
    print 'res.results:'
    for r in res.results():
        print ' ', r


if True:
    conn = local.local_connection
    solver = conn.get_solver("c4-sw_sample")
else:
    token = os.environ['DWAVE_TOKEN']
    conn = remote.RemoteConnection('https://localhost:10443/sapi', token)
    solver = conn.get_solver("DW2X")

net = fig1A4()
solve(net)

net = fig1B()
solve(net)

net = fig1C()
solve(net)