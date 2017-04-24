import matplotlib.pyplot as plt

import terrorGraphs as tg

def break_name(name):
    return name.replace(' ', '\n')

def make_labels(grph):
    return {n: break_name(a['name']) for (n, a) in grph.nodes(data=True)}


def edge_color(e):
    negTypes = {'riv'}
    return 'r' if e['type'] in negTypes else 'b'

def edge_colors(grph):
    return [edge_color(d) for (n1,n2,d) in grph.edges(data=True)]

def node_color(n):
    if 'weight' in n:
        if n['weight'] < 0:
            return 'r'
        elif n['weight'] > 0:
            return 'b'
        else:
            return 'y'
    return 'g'

def node_colors(grph):
    return [node_color(d) for (n,d) in grph.nodes(data=True)]


def plot(date, grph, tag, title=None, pos=None, save=False):
    plt.figure(figsize=(12, 12))
    if pos is None:
        pos = tg.nx.spring_layout(grph, iterations=1000)

    tg.nx.draw_networkx(grph, pos=pos, node_size=2500, node_shape='o', alpha=0.6,
                        labels=make_labels(grph),
                        node_color=node_colors(grph),
                        edge_color=edge_colors(grph), width=2.0)
    plt.xlim(-0.05, 1.05)
    plt.ylim(-0.05, 1.05)
    plt.axis('off')
    if title is not None:
        plt.title(title)
    if save:
        plt.savefig(tag+'_graph_{}.png'.format(date))
    plt.show()
    plt.close()
    return pos


if __name__ == '__main__':
    terrorFile = "syria.json"

    data = tg.st.getData(terrorFile)
    groups, links = tg.st.extract(data)
    graphs = tg.create_graphs_by_date(groups, links)

    date, grph = graphs[-1]
    pos = tg.nx.spring_layout(grph, iterations=1000)

    grph = tg.nx.Graph()
    for (date, grphPartial) in graphs:
        grph = tg.nx.compose(grph, grphPartial)
        plot(date, grph, pos=pos, title=date)
