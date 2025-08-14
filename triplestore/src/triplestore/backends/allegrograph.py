# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

import logging
from pathlib import Path
from typing import Any

import requests
from rdflib import Graph

from triplestore.base import TriplestoreBackend

logger = logging.getLogger(__name__)


class AllegroGraph(TriplestoreBackend):
    """
    A triplestore backend implementation for AllegroGraph using its SPARQL HTTP interface.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize the AllegroGraph backend with the given configuration.

        Parameters:
        config : dict
            A configuration dictionary containing connection parameters:
            - base_url (optional): Base URL of the AllegroGraph instance (default: http://localhost:10035).
            - repository : Name of the target repository (required).
            - auth (optional): Tuple (username, password) for HTTP Basic Auth.
            - graph (optional): Named graph URI for scoped operations.

        Raises:
        ValueError
            If the 'repository' key is missing from the configuration.
        """

        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:10035")
        self.repository = config.get("repository")
        self.auth = config.get("auth")
        self.graph_uri = config.get("graph")

        if not self.repository:
            msg = "[AllegroGraph] Missing required 'repository' in config."
            raise ValueError(msg)

        self.query_url = f"{self.base_url}/repositories/{self.repository}"
        self.update_url = self.query_url
        self.headers_query = {"Accept": "application/sparql-results+json"}
        self.headers_update = {"Content-Type": "application/x-www-form-urlencoded"}
        self.headers_load = {"Content-Type": "text/turtle"}

    def load(self, filename: str) -> None:
        """
        Load RDF triples from a Turtle (.ttl) file into the AllegroGraph repository.
        This implementation parses the file and serializes it to N-Triples before loading.

        Parameters:
        filename : str
            Path to the Turtle (.ttl) file to be loaded.

        Raises:
        RuntimeError
            If the server returns an error status during data loading.
        """
        if not Path(filename).exists():
            msg = f"[AllegroGraph] File not found: {filename}"
            raise FileNotFoundError(msg)

        g = Graph()
        g.parse(filename, format="turtle")
        triples = g.serialize(format="nt").strip()

        sparql = (
            f"INSERT DATA {{ GRAPH <{self.graph_uri}> {{ {triples} }} }}"
            if self.graph_uri else
            f"INSERT DATA {{ {triples} }}"
        )
        self._run_update(sparql)

    def add(self, s: str, p: str, o: str) -> None:
        """
        Add a triple to the AllegroGraph store.

        Parameters:
        s : str
            The subject URI of the triple.
        p : str
            The predicate URI of the triple.
        o : str
            The object URI of the triple.
        """
        triple = f"<{s}> <{p}> <{o}> ."
        sparql = (
            f"INSERT DATA {{ GRAPH <{self.graph_uri}> {{ {triple} }} }}"
            if self.graph_uri else
            f"INSERT DATA {{ {triple} }}"
        )
        self._run_update(sparql)

    def delete(self, s: str, p: str, o: str) -> None:
        """
        Delete a triple from the AllegroGraph store.

        Parameters:
        s : str
            The subject URI of the triple to remove.
        p : str
            The predicate URI of the triple to remove.
        o : str
            The object URI of the triple to remove.
        """
        triple = f"<{s}> <{p}> <{o}> ."
        sparql = (
            f"DELETE DATA {{ GRAPH <{self.graph_uri}> {{ {triple} }} }}"
            if self.graph_uri else
            f"DELETE DATA {{ {triple} }}"
        )
        self._run_update(sparql)

    def query(self, sparql: str) -> list[dict[str, str]]:
        """
        Execute a SPARQL query against the AllegroGraph repository.

        Parameters:
        sparql : str
            The SPARQL query string.

        Returns:
        list of dict
            The list of query result bindings.

        Raises:
        RuntimeError
            If the query fails or the server returns an error response.
        """
        response = requests.post(self.query_url, headers=self.headers_query, data={"query": sparql}, auth=self.auth, timeout=60)

        if response.status_code != 200:
            msg = f"[AllegroGraph] SPARQL query failed: {response.status_code}\n{response.text}"
            raise RuntimeError(msg)

        data = response.json()
        bindings = data.get("results", {}).get("bindings", [])
        return [{k: v["value"] for k, v in row.items()} for row in bindings]

    def clear(self) -> None:
        """
        Remove all data from the AllegroGraph repository.
        Clears the named graph if specified, otherwise clears the default graph.
        """
        sparql = (
            f"CLEAR GRAPH <{self.graph_uri}>"
            if self.graph_uri else
            "DELETE WHERE { ?s ?p ?o }"
        )
        self._run_update(sparql)

    def _run_update(self, sparql: str) -> None:
        """
        Execute a SPARQL update operation.

        Parameters:
        sparql : str
            The SPARQL update string to be sent to the server.

        Raises:
        RuntimeError
            If the update operation fails with a non-success status code.
        """
        response = requests.post(self.update_url, headers=self.headers_update, data={"update": sparql}, auth=self.auth, timeout=60)
        if response.status_code not in {200, 204, 201}:
            msg = f"[AllegroGraph] SPARQL update failed: {response.status_code}\n{response.text}"
            raise RuntimeError(msg)
