import json
import csv

input = 'results.json'
output = 'results.csv'
noname = 'None Removed'
if __name__=='__main__':
    with open(input,'r') as fin:
        indata = json.load(fin)
        # First pass normalizes names and builds a name dictionary and field list.
        year = 0;
        names = set()
        years = list()
        names.add(noname)
        for key in indata.keys():
            d = key.split('_')[2].split('.')[0]
            y = d.split('-')[0]
            if int(y)>int(year):
                year = y
                print(year)
                years.append(year)
                ydata = indata[key]
                for ykey in ydata:
                    label = ykey
                    if label=='__initial__':
                        label = noname
                    print('    '+label)
                    names.add(label)
        names.remove(noname)
        newnamedict = {}
        newnamedict[noname] = noname
        for name in names:
            newname = name
            if name.startswith('The'):
                newname = name.split('The')[1].strip()
            if '(' in name:
                newname = name.split('(')[0].strip()
            if 'of' in name:
                newname = name.split('of')[0].strip()
            names.remove(name)
            newnamedict[name] = newname
            names.add(newname)
        namelist = list(names)
        namelist.sort()
        newnames = [noname]
        for n in namelist:
            newnames.append(n)
        for item in newnames:
            print(item)
    # Second pass transposes the data writes the table in csv form.
    with open(output,'w') as fout:
        csvwriter = csv.writer(fout,lineterminator='\n')
        csvwriter.writerow(['Group']+years)
        year = 0;
        groupdict = {}
        for key in indata.keys():
            d = key.split('_')[2].split('.')[0]
            y = d.split('-')[0]
            if int(y)>int(year):
                year = y
                ydata = indata[key]
                for ykey in ydata:
                    label = ykey
                    if label=='__initial__':
                        label = noname
                    groupkey = newnamedict[label]
                    if not (groupkey in groupdict.keys()):
                       groupdict[groupkey] = {}
                    value = ydata[ykey]
                    if value==-999:
                        value = 0.0
                    groupdict[groupkey][year] = value
        for groupkey in newnames:
            row = []
            for year in years:
                row.append(groupdict[groupkey][year])
            csvwriter.writerow([groupkey]+row)




