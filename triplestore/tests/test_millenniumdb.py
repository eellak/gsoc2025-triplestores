# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

from triplestore import TriplestoreFactory

SUBJECT = "http://example.org/s"
PREDICATE = "http://example.org/p"
OBJECT = "http://example.org/o"
SPARQL_QUERY = "SELECT ?s ?p ?o WHERE { ?s ?p ?o }"

config = {
    "mdb_home": "~/projects/MillenniumDB",
    "graph": "http://example.org/test"
}

def test_add_and_query_triple():
    store = TriplestoreFactory("millenniumdb", config=config)
    store.clear()

    store.add(SUBJECT, PREDICATE, OBJECT)
    results = store.query(SPARQL_QUERY)

    bindings = [str(binding) for binding in results]
    assert any(SUBJECT in b and PREDICATE in b and OBJECT in b for b in bindings)


def test_load_and_query_triple(tmp_path):
    ttl_file = tmp_path / "data.ttl"
    ttl_file.write_text(f"<{SUBJECT}> <{PREDICATE}> <{OBJECT}> .")

    store = TriplestoreFactory("millenniumdb", config=config)
    store.load(str(ttl_file))

    results = store.query(SPARQL_QUERY)
    bindings = [str(binding) for binding in results]

    assert any(SUBJECT in b and PREDICATE in b and OBJECT in b for b in bindings)


def test_clear(tmp_path):
    ttl_file = tmp_path / "data.ttl"
    ttl_file.write_text(f"<{SUBJECT}> <{PREDICATE}> <{OBJECT}> .")

    store = TriplestoreFactory("millenniumdb", config=config)
    store.load(str(ttl_file))
    store.clear()

    results = store.query(SPARQL_QUERY)
    assert len(results) == 0

def test_delete():
    store = TriplestoreFactory("millenniumdb", config=config)
    store.clear()

    store.add(SUBJECT, PREDICATE, OBJECT)
    results = store.query(SPARQL_QUERY)
    assert any(SUBJECT in str(binding) for binding in results)

    store.delete(SUBJECT, PREDICATE, OBJECT)
    results = store.query(SPARQL_QUERY)

    assert all(SUBJECT not in str(binding) for binding in results)

