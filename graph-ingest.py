import pickle
import json
import csv
import sys
import os

from typing import Any
from datetime import datetime
from argparse import ArgumentParser

import humps
import tqdm
import parse
import multiprocessing as mp

from dateutil.parser import parse as _date_parse, ParserError
from utils.dgraph import get_client, initialize_dgraph


class State(object):
    def __init__(self):
        self.field_keys = [
            'country',
            'port_of_entry',
            'age',
            'age_of_entry',
            'age_of_naturalization',
            'sex',
            'year_of_entry',
        ]
        self.field_uid_map = {
            'country': 'c',
            'port_of_entry': 'poe',
            'age': 'a',
            'age_of_entry': 'aoe',
            'age_of_naturalization': 'aon',
            'sex': 's',
            'year_of_entry': 'yoe',
        }

        self.field_sets = dict()
        self.field_uids = {
            field: dict()
            for field in self.field_keys
        }
        self._field_uid_set = {field: set() for field in self.field_keys}

        self.root_uid = None
        self.root_edges = [
            ('country', 'countries'),
            ('port_of_entry', 'ports_of_entry'),
            ('sex', 'sexes'),
            ('year_of_entry', 'years_of_entry')
        ]

    def add_field_set(self, field, value):
        if field not in self.field_sets:
            self.field_sets[field] = set()

        self.field_sets[field].add(value)

    def add_field_uid(self, field, key, uid):
        self.field_uids[field][key] = uid
        self._field_uid_set[field].add(uid)

    def get_stored_field_uids(self, field: str) -> set:
        return self._field_uid_set[field]


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
    person_file_cap = 10_000
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
            sex = row['sex'].strip()

            now = datetime.today()
            dob = date_parse(birth_date, default=now)
            doe = date_parse(date_of_entry, default=dob)
            don = date_parse(naturalization_date, default=dob)
            yoe = parse.parse('{}-{}-{}', date_of_entry)
            yoe = yoe[0] if yoe else -1

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
                'year_of_entry': yoe,
                'sex': sex,
            }

            person_file.write(json.dumps(person) + '\n')

            for field in state.field_keys:
                state.add_field_set(field, person[field])

            index += 1
            if n != 0 and index > n:
                break

            person_file_size += 1
            if person_file_size % person_file_cap == 0:
                person_file.close()
                person_file_index += 1
                person_file = open(f'_people/people{person_file_index}.json', 'w')
        csvfile.close()

    return person_file_index


def create_people(state: State, _index: int):
    print(f'Starting _people/people{_index}.json')

    client, stub = get_client()
    txn = client.txn()

    for index, person_line in enumerate(open(f'_people/people{_index}.json', 'r')):
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

        if index % 300 == 0:
            txn.commit()
            del txn
            txn = client.txn()

    txn.commit()
    del txn

    print(f'Finishing _people/people{_index}.json')


def create_set_v(state: State):
    client, stub = get_client()
    txn = client.txn()

    for field, field_set in state.field_sets.items():
        for value in field_set:
            if value == '':
                value = 'unknown'
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
                for uid in state.get_stored_field_uids(field)
            ],
        })

    txn.commit()


def create_edges(state: State, txn, person_uid: str, fields: dict):
    for field, value in fields.items():
        if value == '':
            value = 'unknown'
        txn.mutate(set_obj={
            'uid': person_uid,
            state.field_uid_map[field]: [{'uid': state.field_uids[field][value]}],
        })
    txn.mutate(set_obj={
        'uid': state.root_uid,
        'people': [{'uid': person_uid}]
    })


def create_root(state: State):
    client, stub = get_client()
    txn = client.txn()

    root = {"uid": "_:root", "dgraph.type": "Root"}
    response = txn.mutate(set_obj=root)
    root_uid = response.uids['root']
    state.root_uid = root_uid

    txn.commit()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-n', type=int, default=0, help='number of lines to parse')
    parser.add_argument('-w', type=int, default=8, help='number of workers to use')
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

    pickle.dump(state, open('state.pickle', 'wb'))

    print('Create people v')
    with mp.Pool(args.w) as pool:
        args = [(state, index) for index in range(person_file_count+1)]
        pool.starmap(create_people, args)


if __name__ == '__main__':
    main()


