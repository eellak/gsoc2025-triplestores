# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0


from triplestore import TriplestoreFactory

# Sample data
SUBJECT = "http://example.org/s"
PREDICATE = "http://example.org/p"
OBJECT = "http://example.org/o"
SPARQL_QUERY = "SELECT ?s ?p ?o WHERE { ?s ?p ?o }"


def test_add_and_query_triple():
    store = TriplestoreFactory("oxigraph", config={})
    store.clear()

    store.add(SUBJECT, PREDICATE, OBJECT)
    results = store.query(SPARQL_QUERY)

    bindings = [str(binding) for binding in results]
    assert any(SUBJECT in b and PREDICATE in b and OBJECT in b for b in bindings)


def test_clear():
    store = TriplestoreFactory("oxigraph", config={})
    store.add(SUBJECT, PREDICATE, OBJECT)

    store.clear()
    results = store.query(SPARQL_QUERY)

    assert len(results) == 0
