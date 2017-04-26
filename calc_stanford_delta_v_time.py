# Calculated delta vs time from stored graphml files of solutions.

import glob

import networkx as nx

if __name__=='__main__':

    label = 'results-syria'
    path = 'results/'+label+'/*.graphml'
    output = 'results/'+label+'/'+label+'delta-vs-time.csv'

    files = glob.glob(path)
    fout = open(output,'wb')
    fout.write('date,delta,delta_per_edge\n')

    for f in files:
        g = nx.read_graphml(f)
        date = g.graph['date']
        delta = g.graph['delta']
        nedges = len(g.edges())
        delta_per_edge = delta/float(nedges)
        fout.write(str(date)+','+str(delta)+','+str(delta_per_edge)+'\n')

    fout.close()
