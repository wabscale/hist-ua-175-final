import csv
import json

from utils.dgraph import get_client, initialize_dgraph

# Create DGraph client
client, stub = get_client()


class State(object):
    def __init__(self):
        self.countries = set()
        self.port_of_entries = set()

        # UIDS
        self.country_uids = dict()
        self.port_of_entry_uids = dict()

        self.root_uid = None


def parse_file(state: State):
    with open('alien.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')

        with open('people.json', 'w') as f:

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
                    'country': country,
                    'port_of_entry': port_of_entry,
                }

                f.write(json.dumps(person) + '\n')
                state.countries.add(country)
                state.port_of_entries.add(port_of_entry)
        csvfile.close()


def create_people(state: State):
    txn = client.txn()
    index = 0

    for person_line in open('people.json', 'r'):
        person = json.loads(person_line)
        country = person['country']
        port_of_entry = person['port_of_entry']
        del person['country']
        del person['port_of_entry']
        response = txn.mutate(set_obj=person)
        person_uid = response.uids[person['naid']]
        create_edges(state, person_uid, country, port_of_entry)

        del person
        del person_line

        if index % 500 == 0:
            txn.commit()
            del txn
            txn = client.txn()

    txn.commit()


def create_set_v(state: State):
    txn = client.txn()

    for country in state.countries:
        response = txn.mutate(set_obj={
            'uid': '_:' + str(hash(country)),
            'dgraph.type': 'Country',
            'country': country,
        })
        state.country_uids[country] = response.uids[str(hash(country))]

    for port_of_entry in state.port_of_entries:
        response = txn.mutate(set_obj={
            'uid': '_:' + str(hash(port_of_entry)),
            'dgraph.type': 'PortOfEntry',
            'port_of_entry': port_of_entry,
        })
        state.port_of_entry_uids[port_of_entry] = response.uids[str(hash(port_of_entry))]

    txn.mutate(set_obj={
        'uid': state.root_uid,
        'countries': [
            {'uid': country_uid}
            for country_uid in state.country_uids.values()
        ],
    })
    txn.mutate(set_obj={
        'uid': state.root_uid,
        'ports_of_entry': [
            {'uid': port_of_entry_uid}
            for port_of_entry_uid in state.port_of_entry_uids.values()
        ],
    })

    txn.commit()


def create_edges(state: State, person_uid: str, country: str, port_of_entry: str):
    txn = client.txn()

    txn.mutate(set_obj={
        'uid': state.country_uids[country],
        'people': [{'uid': person_uid}],
    })

    txn.mutate(set_obj={
        'uid': state.port_of_entry_uids[port_of_entry],
        'people': [{'uid': person_uid}],
    })

    txn.commit()


def create_root(state: State):
    txn = client.txn()

    root = {
        "uid": "_:root",
        "dgraph.type": "Root",
    }
    response = txn.mutate(set_obj=root)
    root_uid = response.uids['root']
    state.root_uid = root_uid

    txn.commit()


def main():
    initialize_dgraph()
    state = State()

    print('Creating root')
    create_root(state)

    print('Parsing file')
    parse_file(state)

    print('Creating set v')
    create_set_v(state)

    print('Create people v')
    create_people(state)


if __name__ == '__main__':
    main()


