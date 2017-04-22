import dwave_sapi2.local as local
import dwave_sapi2.remote as remote

import os

import networkx as nx

import terrorGraphs as tg
import scaling as sc
import social as soc
import settings

import cProfile, pstats, io

import time

if __name__=='__main__':

    use_dwave = True
    nn = 50

    gtype = 'erdos'

    # Use the D Wave machine or local solver.
    if not use_dwave:
        conn = local.local_connection
        solver = conn.get_solver("c4-sw_sample")
    else:
        #token = os.environ['DWAVE_TOKEN']
        token = settings.DWAVE_TOKEN
        print token
        os.environ['no_proxy'] = 'localhost'
        # print os.environ
        conn = remote.RemoteConnection('https://localhost:10443/sapi', token)
        solver = conn.get_solver("DW2X")

    # Set up the profiler and enable.
    #pr = cProfile.Profile()
    #pr.enable()

    # Make a random graph of 10 nodes.
    g = sc.make_random_graph(nn,gtype)
    ne = len(g.edges())

    # Create a social network from the graph.
    socnet = sc.make_social_network(g)

    # Get an embedding for the graph.
    start_time = time.time()
    embedding = soc.Embedding(solver,socnet)
    end_time = time.time()
    print('Total embedding time = '+str(end_time-start_time)+' seconds.')

    # Solve the embedded problem.
    start_time = time.time()
    solution = socnet.solve(solver,embedding)
    end_time = time.time()
    print('Total solution time = '+str(end_time-start_time) + ' seconds.')
    if use_dwave==True:
        qpu_access_time = solution._orig_results['timing']['qpu_access_time']
        print('qpu_access_time = '+str(qpu_access_time*1.e-6)+' seconds.')

    # Stop the profiler and collect results.
    #pr.disable()
    # s = io.StringIO()
    # sortby = 'cumulative'
    # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    # ps.print_stats()
    # print(s.getvalue())
    # ps = pstats.Stats(pr).strip_dirs().sort_stats('time')
    # pr.create_stats()
    # pr.print_stats()



    sJs = solution.results()[0]['sJs:']
    delta = 0.5*(float(ne) + sJs)

    print('Solution found. Delta = '+str(delta))


