# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

"""
Tests for the AllegroGraph backend of the triplestore abstraction layer.

All operations are scoped within the named graph 'http://example.org/test',
and use a local AllegroGraph instance with SPARQL HTTP API access.
"""

import os
import tempfile
import time
from pathlib import Path

import pytest
import requests
from triplestore import TriplestoreFactory

from network_utils import init_allegrograph_repo

# SPARQL Test Data
SUBJECT = "http://example.org/s"
PREDICATE = "http://example.org/p"
OBJECT = "http://example.org/o"
SPARQL_QUERY = "SELECT ?s ?p ?o WHERE { GRAPH <http://example.org/test> { ?s ?p ?o } }"

# Repository configuration
REPO_NAME = f"testns-{int(time.time())}"
USERNAME = os.getenv("AG_USERNAME", "testuser")
PASSWORD = os.getenv("AG_PASSWORD", "testpass")


# Connection configuration
config = {
    "base_url": "http://localhost:10035",
    "repository": REPO_NAME,
    "auth": (USERNAME, PASSWORD),
    "graph": "http://example.org/test"
}


def is_allegrograph_available():
    try:
        url = config["base_url"]
        response = requests.get(url, timeout=2)
        return response.status_code in {200, 401, 403}
    except requests.RequestException:
        return False


pytestmark = pytest.mark.skipif(
    not is_allegrograph_available(),
    reason=f"AllegroGraph instance is not reachable at {config['base_url']}"
)


@pytest.fixture(scope="module", autouse=True)
def setup_repo():
    init_allegrograph_repo(REPO_NAME)


def test_add_and_query_triple():
    """Test adding a triple and retrieving it via SPARQL."""
    store = TriplestoreFactory("allegrograph", config=config)
    store.clear()
    store.add(SUBJECT, PREDICATE, OBJECT)
    results = store.query(SPARQL_QUERY)
    bindings = [str(binding) for binding in results]
    assert any(SUBJECT in b and PREDICATE in b and OBJECT in b for b in bindings)


def test_multiple_triples_query():
    """Test querying multiple triples with the same predicate-object pair."""
    store = TriplestoreFactory("allegrograph", config=config)
    store.clear()
    store.add("http://example.org/s1", PREDICATE, OBJECT)
    store.add("http://example.org/s2", PREDICATE, OBJECT)
    results = store.query("SELECT ?s WHERE { ?s <http://example.org/p> <http://example.org/o> }")
    subjects = [str(row["s"]).strip("<>") for row in results]
    assert "http://example.org/s1" in subjects
    assert "http://example.org/s2" in subjects
    assert len(subjects) == 2


def test_delete_triple():
    """Test that deleting a triple removes it from the store."""
    store = TriplestoreFactory("allegrograph", config=config)
    store.clear()
    store.add(SUBJECT, PREDICATE, OBJECT)
    assert len(store.query(SPARQL_QUERY)) == 1
    store.delete(SUBJECT, PREDICATE, OBJECT)
    results = store.query(SPARQL_QUERY)
    assert len(results) == 0


def test_query_roundtrip_add():
    """Test add-delete-add cycle to ensure consistent state after re-adding a triple."""
    store = TriplestoreFactory("allegrograph", config=config)
    store.clear()
    store.add(SUBJECT, PREDICATE, OBJECT)
    initial_results = store.query(SPARQL_QUERY)
    row = next(iter(initial_results))
    s = str(row["s"]).strip("<>")
    p = str(row["p"]).strip("<>")
    o = str(row["o"]).strip("<>")
    store.delete(s, p, o)
    after_delete = store.query(SPARQL_QUERY)
    assert not any(str(r["s"]).strip("<>") == s and str(r["p"]).strip("<>") == p and str(r["o"]).strip("<>") == o for r in after_delete)
    store.add(s, p, o)
    final_results = store.query(SPARQL_QUERY)
    count = sum(1 for r in final_results if str(r["s"]).strip("<>") == s and str(r["p"]).strip("<>") == p and str(r["o"]).strip("<>") == o)
    assert count == 1


def test_query_returns_empty_when_no_match():
    """Test that a SPARQL query returns no results when no match exists."""
    store = TriplestoreFactory("allegrograph", config=config)
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
    store = TriplestoreFactory("allegrograph", config=config)
    store.clear()
    store.load(tmp_path)
    results = store.query(SPARQL_QUERY)
    Path(tmp_path).unlink()
    bindings = [str(binding) for binding in results]
    assert any(SUBJECT in b and PREDICATE in b and OBJECT in b for b in bindings)


def test_clear():
    """Test that clear() removes all triples from the store."""
    store = TriplestoreFactory("allegrograph", config=config)
    store.add(SUBJECT, PREDICATE, OBJECT)
    store.clear()
    results = store.query(SPARQL_QUERY)
    assert len(results) == 0


def test_clear_twice_is_safe():
    """Test that calling clear() multiple times doesn't raise or fail."""
    store = TriplestoreFactory("allegrograph", config=config)
    store.clear()
    store.clear()
    store.add(SUBJECT, PREDICATE, OBJECT)
    store.clear()
    results = store.query(SPARQL_QUERY)
    assert len(results) == 0
