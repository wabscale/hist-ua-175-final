import json
import os

import requests

queries = {
    'full_graph.json': {
        'root': True,
        'next': False,
        'clean': False,
        'query': """
{
	root(func: type(Root)) {
		nat_loc {
			name
      people {
				name
        anum
        nat_date
        next @filter(eq(nat_location, "new york")) { 
          anum
        }
      }
    }
  }
}
    """
    },

    'new_york_graph_branch.json': {
        'root': False,
        'next': False,
        'clean': False,
        'query': """
{
	root(func: type(Root)) {
		nat_loc @filter(eq(name, "new york")) {
			name
      people {
				name
        anum
        nat_date
        next @filter(eq(nat_location, "new york")) { 
          anum
        }
      }
    }
  }
}
    """,
    },

    'new_york_graph_branch_link.json': {
        'root': False,
        'next': True,
        'clean': False,
        'query': """
{
	root(func: type(Root)) {
		nat_loc @filter(eq(name, "new york")) {
			name
      people {
				name
        anum
        nat_date
        next @filter(eq(nat_location, "new york")) { 
          anum
        }
      }
    }
  }
}
    """,
    },
    'new_york_graph_branch_link_clean.json': {
        'root': False,
        'next': True,
        'clean': True,
        'query': """
{
	root(func: type(Root)) {
		nat_loc @filter(eq(name, "new york")) {
			name
      people {
				name
        anum
        nat_date
        next @filter(eq(nat_location, "new york")) { 
          anum
        }
      }
    }
  }
}
    """,
    },
}

for filename, o in queries.items():
    query, root, link, clean = o['query'], o['root'], o['next'], o['clean']

    r = requests.post("http://localhost:8080/query?timeout=20s", json={'query': query, 'variables': {}})

    graph = {'nodes': [], 'links': []}
    include_anums = set()
    people_location = dict()
    if root:
        graph['nodes'].append({'id': 'root', 'type': 'root'})
    for _loc in r.json()['data']['root'][0]['nat_loc']:
        loc = _loc['name']
        people = _loc['people']
        graph['nodes'].append({'id': loc, 'name': loc, 'type': 'location'})
        if root:
            graph['links'].append({'source': 'root', 'target': loc})
        for person in people:
            people_location[person['anum']] = loc
            if link:
                if 'next' not in person:
                    continue
                for n in person['next']:
                    include_anums.add(person['anum'])
                    include_anums.add(n['anum'])
                    graph['links'].append({'source': person['anum'], 'target': n['anum']})
            else:
                include_anums.add(person['anum'])
        for person in people:
            if person['anum'] not in include_anums: continue
            graph['nodes'].append({'id': person['anum'], 'anumber': person['anum'], 'type': 'person'})
            if not clean:
                graph['links'].append({'source': loc, 'target': person['anum']})

        if clean:
            all_ids = set(node['id'] for node in graph['nodes'] if isinstance(node['id'], int))
            targets = set(link['target'] for link in graph['links'])

            for source in all_ids.difference(targets):
                graph['links'].append({
                    'source': people_location[source],
                    'target': source,
                })

    with open(os.path.join('src', filename), 'w') as f:
        json.dump(graph, f)
    del graph
