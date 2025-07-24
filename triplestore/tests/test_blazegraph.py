# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

from triplestore import TriplestoreFactory

from network_utils import detect_blazegraph_url

SUBJECT = "http://example.org/s"
PREDICATE = "http://example.org/p"
OBJECT = "http://example.org/o"
SPARQL_QUERY = "SELECT ?s ?p ?o WHERE { ?s ?p ?o }"

config = {
    "base_url": detect_blazegraph_url(),
    "namespace": "kb",
    "graph": "http://example.org/test"
}


def test_add_and_query_triple():
    store = TriplestoreFactory("blazegraph", config=config)
    store.clear()

    store.add(SUBJECT, PREDICATE, OBJECT)
    results = store.query(SPARQL_QUERY)

    bindings = [str(binding) for binding in results]
    assert any(SUBJECT in b and PREDICATE in b and OBJECT in b for b in bindings)


def test_clear():
    store = TriplestoreFactory("blazegraph", config=config)
    store.add(SUBJECT, PREDICATE, OBJECT)

    store.clear()
    results = store.query(SPARQL_QUERY)

    assert len(results) == 0
