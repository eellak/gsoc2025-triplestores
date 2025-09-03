# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from triplestore import Triplestore

config = {
    "namespace": "test2025",
    "graph": "http://example.org/test"
}


def main() -> None:
    store = Triplestore("blazegraph", config=config)

    print(" Loading data…")
    store.load("triplestore/data.ttl")

    num_of_triples_query = f"""SELECT (COUNT(*) AS ?count) WHERE {{ GRAPH <{config["graph"]}> {{ ?s ?p ?o }}}}"""
    result = store.execute(num_of_triples_query)
    num_of_triples = int(result[0]["count"]) if result else 0
    print(f" Loaded. Triple count in <{config['graph']}>: {num_of_triples:,}")

    print("\n Clearing graph…")
    store.clear()
    result = store.execute(num_of_triples_query)
    num_of_triples = int(result[0]["count"]) if result else 0
    print(f" Cleared. Triple count in <{config['graph']}>: {num_of_triples:,}")


if __name__ == "__main__":
    main()
