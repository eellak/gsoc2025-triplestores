# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
from contextlib import suppress
from typing import Any

from triplestore import Triplestore

GRAPH_IRI = "http://example.org/test"

# Minimal configs per backend (extend with base_url/credentials if needed)
CONFIGS: dict[str, dict[str, Any]] = {
    "allegrograph": {"repository": "test2025", "graph": GRAPH_IRI},
    "blazegraph": {"namespace": "test2025", "graph": GRAPH_IRI},
    "graphdb": {"repository": "test2025", "graph": GRAPH_IRI},
    "jena": {"dataset": "test2025", "graph": GRAPH_IRI},
    "oxigraph": {"graph": GRAPH_IRI},
}


def main() -> None:

    parser = argparse.ArgumentParser(
        description="Unified triplestore demo showcasing the abstraction layer."
    )
    parser.add_argument(
        "-b",
        choices=["allegrograph", "graphdb", "blazegraph", "jena", "oxigraph"],
        required=True,
        help="Which backend to run the demo for.",
    )
    args = parser.parse_args()
    backend = args.b

    if backend not in CONFIGS:
        print(f"Unknown backend: {backend}. Available: {', '.join(CONFIGS)}")
        return 2

    config = CONFIGS[backend]

    store = Triplestore(backend, config=config)

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

    if backend == "jena":
        with suppress(Exception):
            store.stop_server()


if __name__ == "__main__":
    main()
