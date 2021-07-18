import json
import requests
from bs4 import BeautifulSoup as BS

r = requests.get('https://thefactfile.org/u-s-states-and-their-border-states/')

soup = BS(r.text, "html.parser")

states = set()
edges = set()
for s, a in zip(soup.find_all('td', {'class': 'column-2'}),
                soup.find_all('td', {'class': 'column-3'})):
    sn = s.a.text
    states.add(sn)
    for san in a.text.split(','):
        san = san.strip()
        san = san.removesuffix(' (water border)')
        if san == 'None' or san == '':
            continue
        if (san, sn) not in edges:
            edges.add((sn, san))

print({
    'states': list(states),
    'edges': list(map(list, edges))
})

json.dump({
    'states': list(states),
    'edges': list(map(list, edges))
}, open('states.json', 'w'))
