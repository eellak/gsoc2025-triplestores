# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

from triplestore import Triplestore

config = {
    "repository": "test2025",
    "graph": "http://example.org/test",
}


def main() -> None:
    store = Triplestore("graphdb", config=config)

    print(" Loading data…")
    store.load("triplestore/data.ttl")

    num_of_triples_query = "SELECT (COUNT(*) AS ?count) WHERE { GRAPH <http://example.org/test> { ?s ?p ?o } }"
    result = store.execute(num_of_triples_query)
    num_of_triples = result[0]["count"]
    print(f" Loaded. Triple count in <http://example.org/test>: {int(num_of_triples):,}")

    print("\n Clearing graph…")
    store.clear()
    result = store.execute(num_of_triples_query)
    num_of_triples = result[0]["count"]
    print(f" Cleared. Triple count in <http://example.org/test>: {int(num_of_triples):,}")


if __name__ == "__main__":
    main()
