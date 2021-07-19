import csv
import json
import os
from typing import Any
from datetime import datetime
from argparse import ArgumentParser

import humps
import tqdm

from dateutil.parser import parse as _date_parse, ParserError
from utils.dgraph import get_client, initialize_dgraph

# Create DGraph client
client, stub = get_client()


class State(object):
    def __init__(self):
        self.field_keys = ['country', 'port_of_entry', 'age', 'age_of_entry', 'age_of_naturalization']

        self.field_sets = dict()
        self.field_uids = dict()

        self.root_uid = None
        self.root_edges = [('country', 'countries'), ('port_of_entry', 'ports_of_entry')]

    def add_field_set(self, field, value):
        if field not in self.field_sets:
            self.field_sets[field] = set()

        self.field_sets[field].add(value)

    def add_field_uid(self, field, key, uid):
        if field not in self.field_uids:
            self.field_uids[field] = dict()

        self.field_uids[field][key] = uid


def date_parse(date_str: str, default: Any = None) -> datetime:
    if date_str == '' or date_str is None:
        return default

    try:
        return _date_parse(date_str)
    except ParserError:
        return default


def parse_file(state: State, n: int = 0):
    os.makedirs('_people/', exist_ok=True)
    person_file_index = 0
    person_file_cap = 1000
    person_file = open(f'_people/people{person_file_index}.json', 'w')

    with open('alien.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')

        person_file_size = 0
        for index, row in enumerate(reader):
            naid = row['naid']
            name = row['name'].strip()
            alias = row['alias'].strip()
            birth_date = row['birth date'].strip()
            date_of_entry = row['date of entry'].strip()
            naturalization_date = row['naturalization date'].strip()
            country = row['country'].strip()
            port_of_entry = row['port of entry'].strip()

            now = datetime.today()
            dob = date_parse(birth_date, default=now)
            doe = date_parse(date_of_entry, default=dob)
            don = date_parse(naturalization_date, default=dob)

            age = (now - dob).days // 365
            aae = (doe - dob).days // 365
            aan = (don - dob).days // 365

            person = {
                'uid': '_:' + naid,
                'dgraph.type': 'Person',
                'name': name,
                'naid': naid,
                'alias': alias,
                'age': age,
                'age_of_entry': aae,
                'age_of_naturalization': aan,
                'country': country,
                'port_of_entry': port_of_entry,
            }

            person_file.write(json.dumps(person) + '\n')

            for field in state.field_keys:
                state.add_field_set(field, person[field])

            index += 1
            if n != 0 and index > n:
                break

            person_file_size += 1
            if person_file_size == person_file_cap:
                person_file.close()
                person_file_index += 1
                person_file = open(f'_people/people{person_file_index}.json', 'w')
        csvfile.close()

    return person_file_index


def create_people(state: State, index: int):
    txn = client.txn()

    for person_line in open(f'_people/people{index}.json', 'r'):
        person = json.loads(person_line)

        fields = {
            field: person[field]
            for field in state.field_keys
        }
        for field in fields:
            del person[field]

        response = txn.mutate(set_obj=person)
        person_uid = response.uids[person['naid']]
        create_edges(state, txn, person_uid, fields)

        del person
        del person_line

    txn.commit()


def create_set_v(state: State):
    txn = client.txn()

    for field, field_set in state.field_sets.items():
        for value in field_set:
            response = txn.mutate(set_obj={
                'uid': '_:' + str(hash(value)),
                'dgraph.type': humps.pascalize(field),
                field: value,
            })
            state.add_field_uid(field, value, response.uids[str(hash(value))])
        txn.commit()
        del txn
        txn = client.txn()

    for field, downname in state.root_edges:
        txn.mutate(set_obj={
            'uid': state.root_uid,
            downname: [
                {'uid': uid}
                for uid in state.field_uids[field].values()
            ],
        })

    txn.commit()


def create_edges(state: State, txn, person_uid: str, fields: dict):
    for field, value in fields.items():
        txn.mutate(set_obj={
            'uid': state.field_uids[field][value],
            'people': [{'uid': person_uid}],
        })


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


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('n', type=int, default=0, help='number of lines to parse')
    return parser.parse_args()


def main():
    args = parse_args()

    initialize_dgraph()

    state = State()

    print('Creating root')
    create_root(state)

    print('Parsing file')
    person_file_count = parse_file(state, args.n)

    print('Creating set v')
    create_set_v(state)

    print('Create people v')
    for index in tqdm.tqdm(range(person_file_count+1)):
        create_people(state, index)


if __name__ == '__main__':
    main()


