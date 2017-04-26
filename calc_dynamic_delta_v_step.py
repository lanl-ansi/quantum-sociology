# Calculated delta vs time from stored graphml files of solutions.

import glob

import networkx as nx

if __name__=='__main__':

    label = 'results-dynamic'
    path = 'results/'+label+'/*violation*.graphml'
    output = 'results/'+label+'/'+label+'-delta-vs-time-violation.csv'

    files = glob.glob(path)
    fout = open(output,'wb')
    fout.write('step,delta\n')

    for f in files:
        g = nx.read_graphml(f)
        delta = g.graph['delta']
        i1 = f.index('.graphml')
        tok = f[(i1-3):i1]
        i2 = tok.index('_')
        step = tok[(i2+1):len(tok)]
        #print(step+','+str(delta))
        fout.write(step+','+str(delta)+'\n')

    fout.close()
