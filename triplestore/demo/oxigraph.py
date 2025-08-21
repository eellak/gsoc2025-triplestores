# Copyright (C) 2025
# SPDX-License-Identifier: Apache-2.0

from triplestore import TriplestoreFactory

config = {
    "graph": "http://example.org/test"
}

store = TriplestoreFactory("oxigraph", config=config)
print(" Loading data…")
store.load("triplestore/data.ttl")

num_of_triples_query = "SELECT (COUNT(*) AS ?count) WHERE { GRAPH <http://example.org/test> { ?s ?p ?o } }"
result = store.execute(num_of_triples_query)
num_of_triples = result[0]["count"].value
print(f" Loaded. Triple count in <http://example.org/test>: {int(num_of_triples):,}")

print("\n Clearing graph…")
store.clear()
num_of_triples_query = "SELECT (COUNT(*) AS ?count) WHERE { GRAPH <http://example.org/test> { ?s ?p ?o } }"
result = store.execute(num_of_triples_query)
num_of_triples = result[0]["count"].value
print(f" Cleared. Triple count in <http://example.org/test>: {int(num_of_triples):,}")
