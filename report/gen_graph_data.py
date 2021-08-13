import requests
import json
import os

queries = {
    'full_graph.json': {
        'root': True,
        'query': """
{
	root(func: type(Root)) {
		nat_loc {
			name
      people {
				name
        anum
        nat_date
      }
    }
  }
}
    """
    },

    'new_york_graph.json': {
        'root': False,
        'query': """
{
	root(func: type(Root)) {
		nat_loc @filter(eq(name, "new york")) {
			name
      people {
				name
        anum
        nat_date
      }
    }
  }
}
    """,
    }
}


for filename, o in queries.items():
    query, root = o['query'], o['root']

    r = requests.post("http://localhost:8080/query?timeout=20s", json={'query': query, 'variables': {}})

    graph = {'nodes': [], 'links': []}
    if root:
        graph['nodes'].append({'id':'root', 'type': 'root'})
    for _loc in r.json()['data']['root'][0]['nat_loc']:
        loc = _loc['name']
        people = _loc['people']
        graph['nodes'].append({'id': loc, 'name': loc, 'type': 'location'})
        if root:
            graph['links'].append({'source': 'root', 'target': loc})
        for person in people:
            graph['nodes'].append({'id': person['anum'], 'anumber': person['anum'], 'type': 'person'})
            graph['links'].append({'source': loc, 'target': person['anum']})

    with open(os.path.join('src', filename), 'w') as f:
        json.dump(graph, f)
    del graph
