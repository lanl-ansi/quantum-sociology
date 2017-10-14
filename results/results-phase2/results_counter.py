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
        count = 0
        for key in indata.keys():
            d = key.split('_')[2].split('.')[0]
            y = d.split('-')[0]
            print(y)
            count += 1
            if int(y)>int(year):
                year = y
                #print(year)
    print(count)



