import json

_allowedTypes = {'all','riv','aff'}

def getData(file):
    with open(file) as data_file:
        data = json.load(data_file)
    return data


def _simpleGroup(g):
    return {'id': g['id'], 'name': g['name'], 'shortname': g['shortname']}


def _simpleLink(l):
    return {'group1': l['group1'], 'group2': l['group2'], 'date': l['date'], 'type': l['type']}


def extract(data):
    groups = [ _simpleGroup(g['Group']) for g in data['groups']]
    links = []
    for l in data['links']:
        if l['Link']['type'] in _allowedTypes:
            links.append(_simpleLink(l['Link']))
    return groups, links


if __name__ == "__main__":

    data = getData('syria.json')
    groups, links = extract(data)

    def sort(links):
        links = sorted(links, key=lambda l: l['date'])
        return links

    links = sort(links)

    print links
    print [l['date'] for l in links]


