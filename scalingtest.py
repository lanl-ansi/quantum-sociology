import dwave_sapi2.local as local
import dwave_sapi2.remote as remote

import os
import sys

import networkx as nx

import terrorGraphs as tg
import scaling as sc
import social as soc
import settings

import cProfile, pstats, io

import time

if __name__=='__main__':

    use_dwave = True
    nmin = 5
    nmax = 50
    gtype = 'erdos'

    ctype = 'classical'
    if use_dwave:
        ctype = 'dwave'
    output = ctype+'-scaling-'+gtype+'.csv'

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

    # Don't use the profiler for timing. Too fine-grained, misleading.
    # Set up the profiler and enable.
    # pr = cProfile.Profile()
    # pr.enable()

    fout = open(output, 'wb')
    fout.write('nnodes,tembedding,tsolve,tqpu\n')
    try:
        for nn in range(nmin,nmax+1):
            # Make a random graph of  nodes.
            g = sc.make_random_graph(nn,gtype)
            ne = len(g.edges())

            # Create a social network from the graph.
            socnet = sc.make_social_network(g)

            # Get an embedding for the graph.
            start_time = time.time()
            embedding = soc.Embedding(solver,socnet)
            end_time = time.time()
            tembedding = end_time-start_time
            print('Total embedding time = '+str(tembedding)+' seconds.')

            # Solve the embedded problem.
            start_time = time.time()
            solution = socnet.solve(solver,embedding)
            end_time = time.time()
            tsolve = end_time-start_time
            print('Total solution time = '+str(tsolve) + ' seconds.')
            qpuval = 'n/a'
            if use_dwave==True:
                qpu_access_time = solution._orig_results['timing']['qpu_access_time']
                qpuval = str(qpu_access_time*1.e-6)
                print('qpu_access_time = '+qpuval+' seconds.')
            fout.write(str(nn)+','+str(tembedding)+','+str(tsolve)+','+qpuval+'\n')

            # Stop the profiler and collect results.
            # pr.disable()
            # s = io.StringIO()
            # sortby = 'cumulative'
            # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            # ps.print_stats()
            # print(s.getvalue())
            # ps = pstats.Stats(pr).strip_dirs().sort_stats('name')
            # stats = ps.stats
            # for k in stats.keys():
            #     if ('embed_problem' in k)&('social.py' in k):
            #         embeddingcpu = stats[k][3]
            #     if ('solve' in k)&('social.py' in k):
            #         solvecpu = stats[k][3]
            # pr.create_stats()
            # pr.print_stats()
            # print('Problem embedding cpu = '+str(embeddingcpu))
            # print('Problem solve cpu = '+ str(solvecpu))


            # sJs = solution.results()[0]['sJs:']
            # delta = 0.5*(float(ne) + sJs)
            #
            # print('Solution found. Delta = '+str(delta))
    except:
        fout.close()
        sys.exit(1)
    fout.close()
    sys.exit(0)


