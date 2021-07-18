import csv
import json

from utils.dgraph import get_client, initialize_dgraph

vertices = [{'uid': '_:root', 'dgraph.type': 'Root'}]
edges = []

# Create DGraph client
client, stub = get_client()

txn = client.txn()

root = {
    "uid": "_:root",
    "dgraph.type": "Root",
}
response = txn.mutate(set_obj=root)
root_uid = response.uids['root']

people = []
countries = set()
port_of_entries = set()

# EDGES
country_people_edges = dict()
port_of_entry_people_edges = dict()
# UIDS
person_uids = dict()
country_uids = dict()
port_of_entry_uids = dict()

with open('alien.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')

    for row in reader:
        naid = row['naid']
        name = row['name']
        alias = row['alias']
        country = row['country'].strip()
        port_of_entry = row['port of entry'].strip()

        person = {
            'uid': '_:' + naid,
            'dgraph.type': 'Person',
            'name': name,
            'naid': naid,
            'alias': alias,
        }

        response = txn.mutate(set_obj=person)
        person_uids[naid] = response.uids[naid]

        people.append(people)
        countries.add(country)
        port_of_entries.add(port_of_entry)

        if country not in country_people_edges:
            country_people_edges[country] = []
        if port_of_entry not in port_of_entry_people_edges:
            port_of_entry_people_edges[port_of_entry] = []

        country_people_edges[country].append(naid)
        port_of_entry_people_edges[port_of_entry].append(naid)

    csvfile.close()

for person in people:
    response = txn.mutate(set_obj=person)
    person_uids[person['naid']] = response.uids[person['naid']]
txn.commit()

for country in countries:
    response = txn.mutate(set_obj={
        'uid': '_:' + hash(country),
        'dgraph.type': 'Country',
        'country': country,
    })
    country_uids[country] = response.uids[hash(country)]
txn.commit()

for port_of_entry in port_of_entries:
    response = txn.mutate(set_obj={
        'uid': '_:' + hash(port_of_entry),
        'dgraph.type': 'PortOfEntry',
        'port_of_entry': port_of_entry,
    })
    port_of_entry_uids[port_of_entry] = response.uids[hash(port_of_entry)]
txn.commit()

for country, persons in country_people_edges.items():
    txn.mutate(set_obj={
        'uid': country_uids[country],
        'people': [
            {'uid': person_uids[person]}
            for person in persons
        ],
    })
txn.commit()

for country, persons in country_people_edges.items():
    txn.mutate(set_obj={
        'uid': country_uids[country],
        'people': [
            {'uid': person_uids[person]}
            for person in persons
        ],
    })
    txn.commit()

for port_of_entry, persons in port_of_entry_people_edges.items():
    txn.mutate(set_obj={
        'uid': port_of_entry_uids[port_of_entry],
        'people': [
            {'uid': person_uids[person]}
            for person in persons
        ],
    })
    txn.commit()




