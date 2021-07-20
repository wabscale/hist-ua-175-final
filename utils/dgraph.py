import random

import pydgraph
from utils.checkpoint import checkpoint

schema = """
naid: int .
name: string @index(term) .
alias: string .

aoe: [uid] @reverse .
aon: [uid] @reverse .
poe: [uid] @reverse .
yoe: [uid] @reverse .
a: [uid] @reverse .
c: [uid] @reverse .
s: [uid] @reverse .

type Person {
    name
    naid
    alias
    
    aoe
    aon
    poe
    yoe
    a
    c
    s
}

age: int @index(int)  .
type Age {
    age
}

age_of_entry: int @index(int) .
type AgeOfEntry {
    age_of_entry
}

age_of_naturalization: int @index(int) .
type AgeOfNaturalization {
    age_of_naturalization
}

port_of_entry: string @index(exact, term) .
type PortOfEntry {
    port_of_entry
}

country: string @index(exact, term) .
type Country {
    country
}

sex: string @index(exact) .
type Sex {
    sex
}

year_of_entry: dateTime @index(year) .
type YearOfEntry {
    year_of_entry
}

people: [uid] @reverse .
countries: [uid] @reverse .
ports_of_entry: [uid] @reverse .
sexes: [uid] @reverse .
years_of_entry: [uid] @reverse .
type Root {
    countries
    ports_of_entry
    people
    sexes
    years_of_entry
}

"""


class StubWrapper:
    """
    Very simple class for initializing and tracking DGraph connection stubs
    """

    def __init__(self, n: int):
        """
        Initialize random stubs to ensure relatively balanced load on dgraph
        alpha nodes.

        :param n:
        """

        i = random.randint(0, n)

        # Pick 2 random stubs from those available
        self.stubs = [
            pydgraph.DgraphClientStub(f"localhost:{9080 + (i % n)}"),
            pydgraph.DgraphClientStub(f"localhost:{9080 + ((i + 1) % n)}"),
            pydgraph.DgraphClientStub(f"localhost:{9080 + ((i + 2) % n)}"),
        ]

    def close(self):
        """
        Close each stub connection.

        :return:
        """

        for stub in self.stubs:
            stub.close()


def get_client():
    """
    Get a new dgraph client and stub wrapper

    :return: client, stubs
    """

    # Initialize stub wrapper
    client_stub = StubWrapper(6)

    # Pass back client and stubs
    return pydgraph.DgraphClient(*client_stub.stubs), client_stub


def drop_all(client):
    """
    This function drops all dgraph nodes, edges and schemas.

    Essentially a reset on DGraph

    :param client:
    :return:
    """

    print("Dropping DGraph data")
    return client.alter(pydgraph.Operation(drop_all=True))


def set_schema(client):
    """
    Sets up schema for data we are about to ingest.

    :param client:
    :return:
    """

    print("Initializing DGraph Schema")
    return client.alter(pydgraph.Operation(schema=schema))


def initialize_dgraph():
    # Get DGraph client and stub
    client, stub = get_client()

    # Drop any and all data and schema
    drop_all(client)

    # Setup schema in DGraph
    set_schema(client)

    # Close outstanding connections
    stub.close()
