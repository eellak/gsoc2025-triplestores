# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

import getpass

import pytest
from triplestore import TriplestoreFactory

from network_utils import init_allegrograph_repo

# SPARQL Test Data
SUBJECT = "http://example.org/s"
PREDICATE = "http://example.org/p"
OBJECT = "http://example.org/o"
SPARQL_QUERY = "SELECT ?s ?p ?o WHERE { ?s ?p ?o }"

# Repository configuration
REPO_NAME = "test-repo"
USERNAME = input("Enter AllegroGraph username: ")
PASSWORD = getpass.getpass("Enter AllegroGraph password: ")

# Connection configuration
config = {
    "base_url": "http://localhost:10035",
    "repository": REPO_NAME,
    "auth": (USERNAME, PASSWORD),
    "graph": "http://example.org/test"
}


@pytest.fixture(scope="module", autouse=True)
def setup_repo():
    init_allegrograph_repo(REPO_NAME)


def test_add_and_query_triple():
    store = TriplestoreFactory("allegrograph", config=config)
    store.clear()
    store.add(SUBJECT, PREDICATE, OBJECT)
    results = store.query(SPARQL_QUERY)

    bindings = [str(binding) for binding in results]
    assert any(SUBJECT in b and PREDICATE in b and OBJECT in b for b in bindings)


def test_clear():
    store = TriplestoreFactory("allegrograph", config=config)
    store.add(SUBJECT, PREDICATE, OBJECT)
    store.clear()
    results = store.query(SPARQL_QUERY)

    assert len(results) == 0
