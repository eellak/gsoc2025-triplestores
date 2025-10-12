# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

"""
Tests for the Apache Jena backend of the triplestore abstraction layer.

All operations are scoped within the named graph 'http://example.org/test',
and use a local Jena Fuseki instance with REST API access.
"""

import tempfile
import time
from pathlib import Path

import requests

from triplestore import Triplestore

SUBJECT = "http://example.org/s"
PREDICATE = "http://example.org/p"
OBJECT = "http://example.org/o"
SPARQL_QUERY = "SELECT ?s ?p ?o WHERE { GRAPH <http://example.org/test> { ?s ?p ?o } }"


config = {
    "base_url": "http://localhost:3030",
    "name": f"testns-{int(time.time())}",
    "auth": None,
    "graph": "http://example.org/test"
}


def test_add_and_query_triple():
    """Test adding a triple and retrieving it via SPARQL."""
    store = Triplestore("jena", config=config)
    store.clear()

    store.add(SUBJECT, PREDICATE, OBJECT)
    results = store.query(SPARQL_QUERY)

    bindings = [str(binding) for binding in results]
    assert any(SUBJECT in b and PREDICATE in b and OBJECT in b for b in bindings)


def test_multiple_triples_query():
    """Test querying multiple triples with the same predicate-object pair."""
    store = Triplestore("jena", config=config)
    store.clear()

    store.add("http://example.org/s1", PREDICATE, OBJECT)
    store.add("http://example.org/s2", PREDICATE, OBJECT)

    results = store.query("""
        SELECT ?s WHERE {
            GRAPH <http://example.org/test> {
                ?s <http://example.org/p> <http://example.org/o>
            }
        }
    """)
    subjects = [str(row["s"]).strip("<>") for row in results]

    assert "http://example.org/s1" in subjects
    assert "http://example.org/s2" in subjects
    assert len(subjects) == 2


def test_delete_triple():
    """Test that deleting a triple removes it from the store."""
    store = Triplestore("jena", config=config)
    store.clear()

    store.add(SUBJECT, PREDICATE, OBJECT)
    assert len(store.query(SPARQL_QUERY)) == 1

    store.delete(SUBJECT, PREDICATE, OBJECT)
    results = store.query(SPARQL_QUERY)
    assert len(results) == 0


def test_query_roundtrip_add():
    """Test add-delete-add cycle to ensure consistent state after re-adding a triple."""
    store = Triplestore("jena", config=config)
    store.clear()

    store.add(SUBJECT, PREDICATE, OBJECT)

    initial_results = store.query(SPARQL_QUERY)
    row = next(iter(initial_results))
    s = str(row["s"]).strip("<>")
    p = str(row["p"]).strip("<>")
    o = str(row["o"]).strip("<>")

    store.delete(s, p, o)

    after_delete = store.query(SPARQL_QUERY)
    assert not any(
        str(r["s"]).strip("<>") == s and
        str(r["p"]).strip("<>") == p and
        str(r["o"]).strip("<>") == o
        for r in after_delete
    )

    store.add(s, p, o)

    final_results = store.query(SPARQL_QUERY)
    count = sum(
        1 for r in final_results
        if str(r["s"]).strip("<>") == s and
           str(r["p"]).strip("<>") == p and
           str(r["o"]).strip("<>") == o
    )
    assert count == 1


def test_query_returns_empty_when_no_match():
    """Test that a SPARQL query returns no results when no match exists."""
    store = Triplestore("jena", config=config)
    store.clear()

    store.add(SUBJECT, PREDICATE, OBJECT)
    results = store.query("SELECT ?s WHERE { <http://example.org/unknown> ?p ?o }")
    assert len(results) == 0


def test_load_from_turtle_file():
    """Test loading triples from a .ttl file into the store."""
    turtle_data = "<http://example.org/s> <http://example.org/p> <http://example.org/o> ."

    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".ttl", encoding="utf-8") as f:
        f.write(turtle_data)
        tmp_path = f.name

    store = Triplestore("jena", config=config)
    store.clear()
    store.load(tmp_path)

    results = store.query(SPARQL_QUERY)
    Path(tmp_path).unlink()  # Clean up

    bindings = [str(binding) for binding in results]
    assert any(SUBJECT in b and PREDICATE in b and OBJECT in b for b in bindings)


def test_clear():
    """Test that clear() removes all triples from the store."""
    store = Triplestore("jena", config=config)
    store.add(SUBJECT, PREDICATE, OBJECT)

    store.clear()
    results = store.query(SPARQL_QUERY)

    assert len(results) == 0


def test_clear_twice_is_safe():
    """Test that calling clear() multiple times doesn't raise or fail."""
    store = Triplestore("jena", config=config)
    store.clear()
    store.clear()

    store.add(SUBJECT, PREDICATE, OBJECT)
    store.clear()
    results = store.query(SPARQL_QUERY)

    assert len(results) == 0


def test_execute():
    """End-to-end test for execute(): INSERT/DELETE/CLEAR + ASK/SELECT/DESCRIBE/CONSTRUCT."""
    store = Triplestore("jena", config=config)
    store.clear()

    graph = config["graph"]

    # --- INSERT DATA (UPDATE)
    insert_q = f"INSERT DATA {{ GRAPH <{graph}> {{ <{SUBJECT}> <{PREDICATE}> <{OBJECT}> }} }}"
    out = store.execute(insert_q)
    assert out is None  # updates should return None

    # --- ASK (boolean)
    ask_q = f"ASK WHERE {{ GRAPH <{graph}> {{ <{SUBJECT}> <{PREDICATE}> <{OBJECT}> }} }}"
    ask_res = store.execute(ask_q)
    assert isinstance(ask_res, bool)
    assert ask_res is True

    # --- SELECT (bindings -> list[dict])
    select_q = f"""
        SELECT ?s WHERE {{
            GRAPH <{graph}> {{
                ?s <{PREDICATE}> <{OBJECT}>
            }}
        }}
    """
    sel = store.execute(select_q)
    assert isinstance(sel, list)
    assert len(sel) == 1
    subjects = [str(r["s"]).strip("<>") for r in sel]
    assert SUBJECT in subjects

    # --- DESCRIBE (RDF text)
    describe_q = f"DESCRIBE <{SUBJECT}>"
    desc = store.execute(describe_q)
    assert isinstance(desc, str)
    # At least verify URIs appear in the serialization
    assert SUBJECT in desc

    # --- CONSTRUCT (RDF text)
    construct_q = f"""
        CONSTRUCT {{ ?s ?p ?o }}
        WHERE {{ GRAPH <{graph}> {{ ?s ?p ?o }} }}
    """
    cons = store.execute(construct_q)
    assert isinstance(cons, str)
    assert SUBJECT in cons
    assert PREDICATE in cons
    assert OBJECT in cons

    # --- DELETE DATA (UPDATE) and verify removal
    delete_q = f"DELETE DATA {{ GRAPH <{graph}> {{ <{SUBJECT}> <{PREDICATE}> <{OBJECT}> }} }}"
    del_out = store.execute(delete_q)
    assert del_out is None
    assert store.execute(ask_q) is False

    # --- Re-insert and CLEAR GRAPH (UPDATE)
    store.execute(f"""
        INSERT DATA {{
            GRAPH <{graph}> {{
                <{SUBJECT}> <{PREDICATE}> <{OBJECT}> .
                <{SUBJECT}> <{PREDICATE}> <{OBJECT}> .
            }}
        }}
    """)
    clear_q = f"CLEAR GRAPH <{graph}>"
    clr_out = store.execute(clear_q)
    assert clr_out is None
    assert store.execute(f"ASK WHERE {{ GRAPH <{graph}> {{ ?s ?p ?o }} }}") is False


def test_stop_server():
    """Test that stop_server() terminates a running Fuseki instance."""
    store = Triplestore("jena", config=config)
    store.clear()

    result = store.stop_server()

    assert result is True

    try:
        r = requests.get(f"{config['base_url']}/$/ping", timeout=2)
        assert r.status_code != 200
    except requests.RequestException:
        pass
