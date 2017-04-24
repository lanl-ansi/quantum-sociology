import glob

import networkx as nx

if __name__=='__main__':

    path = 'results/results-iraq/*.graphml'

    files = glob.glob(path)

    for f in files:
        head = f[0:f.index('.graphml')]
        gexfout = head + '.gexf'

        g = nx.read_graphml(f)
        nx.write_gexf(g,gexfout)

