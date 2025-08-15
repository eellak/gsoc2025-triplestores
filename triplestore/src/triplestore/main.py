# Copyright (C) 2025
# SPDX-License-Identifier: Apache-2.0

# Currently works only for Oxigraph and Apache Jena


import argparse
import os
import sys
import time
from pathlib import Path

from triplestore import TriplestoreFactory

from .network_utils import detect_graphdb_url, init_allegrograph_repo


def build_config(backend: str) -> dict:
    """Return config dict with the same defaults used in the tests."""
    if backend == "oxigraph":
        return {}

    if backend == "jena":
        return {
            "base_url": "http://127.0.0.1:3030",
            "dataset": f"testns-{int(time.time())}",
            "auth": None,
            "graph": "http://example.org/test"
        }

    if backend == "graphdb":
        return {
            "base_url": detect_graphdb_url(),
            "repository": f"testns-{int(time.time())}",
            "auth": None,
            "graph": "http://example.org/test"
        }

    if backend == "blazegraph":
        return {
            "base_url": "http://localhost:9999/blazegraph",
            "namespace": f"testns-{int(time.time())}",
            "graph": "http://example.org/test"
        }

    if backend == "allegrograph":
        repo = f"testns-{int(time.time())}"
        init_allegrograph_repo(repo)
        return {
            "base_url": "http://localhost:10035",
            "repository": repo,
            "auth": (
                os.getenv("AG_USERNAME", "testuser"),
                os.getenv("AG_PASSWORD", "testpass")
            ),
            "graph": "http://example.org/test"
        }

    msg = f"Unknown backend: {backend}"
    raise ValueError(msg)


def main(argv=None) -> int:
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument(
        "-b", "--backend",
        required=True,
        choices=["oxigraph", "jena", "graphdb", "blazegraph", "allegrograph"],
        help="Backend to use"
    )

    pre_args, _ = pre.parse_known_args(argv)

    config = build_config(pre_args.backend)
    if config.get("graph"):
        default_query = f"SELECT ?s ?p ?o WHERE {{ GRAPH <{config['graph']}> {{ ?s ?p ?o }} }} LIMIT 2"
    else:
        default_query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 2"

    parser = argparse.ArgumentParser(
        description="Load a Turtle file and run a sample query on the chosen triplestore backend."
    )
    parser.add_argument(
        "-b", "--backend",
        required=True,
        choices=["oxigraph", "jena", "graphdb", "blazegraph", "allegrograph"],
        help="Backend to use"
    )
    parser.add_argument(
        "-f", "--file",
        help="Path to a .ttl file to load (optional). If omitted, only the query will run."
    )
    parser.add_argument(
        "-q", "--query",
        default=default_query,
        help="SPARQL query to run after loading (default: 2 triples)"
    )
    args = parser.parse_args(argv)

    print(f"Testing {args.backend}")
    try:
        store = TriplestoreFactory(args.backend, config)
    except Exception as e:
        print(f"[ERROR] Failed to initialize backend: {e}")
        return 2

    start = time.time()
    if args.file:
        ttl = Path(args.file)
        if not ttl.exists():
            print(f"[ERROR] File not found: {ttl}")
            return 2
        try:
            store.clear()
            store.load(str(ttl))
            end = time.time()
            print(f"[OK] Loaded data from '{ttl}' in {end - start} s.")
        except Exception as e:
            print(f"[ERROR] Load failed: {e}")
            return 1

    try:
        results = list(store.query(args.query))
        if not results:
            print("[OK] Query returned 0 results.")
        else:
            print(f"[OK] Query returned {len(results)} rows. Showing up to 2:")
            for i, row in enumerate(results[:2], start=1):
                print(f"  {i}. {row}")
            try:
                store.clear()
                store.stop_server()
            except Exception as e:
                    print(f"[ERROR] Clear failed: {e}")
                    return 1
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
