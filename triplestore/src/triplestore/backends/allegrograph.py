# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

import logging
from pathlib import Path
from typing import Any

import requests

from triplestore.base import TriplestoreBackend

logger = logging.getLogger(__name__)


class AllegroGraph(TriplestoreBackend):
    """
    AllegroGraph backend using the SPARQL HTTP interface.
    """
    def __init__(self, config: dict[str, Any]) -> None:
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
        rdf_data = Path(filename).read_bytes()

        response = requests.post(self.update_url, headers=self.headers_load, data=rdf_data, auth=self.auth, timeout=60)
        if response.status_code not in {200, 204, 201}:
            msg = f"[AllegroGraph] Load failed: {response.status_code}\n{response.text}"
            raise RuntimeError(msg)

    def add(self, s: str, p: str, o: str) -> None:
        triple = f"<{s}> <{p}> <{o}> ."
        sparql = (
            f"INSERT DATA {{ GRAPH <{self.graph_uri}> {{ {triple} }} }}"
            if self.graph_uri else
            f"INSERT DATA {{ {triple} }}"
        )
        self._run_update(sparql)

    def delete(self, s: str, p: str, o: str) -> None:
        triple = f"<{s}> <{p}> <{o}> ."
        sparql = f"DELETE DATA {{ {triple} }}"
        self._run_update(sparql)

    def query(self, sparql: str) -> list[dict[str, str]]:
        response = requests.post(self.query_url, headers=self.headers_query, data={"query": sparql}, auth=self.auth, timeout=60)

        if response.status_code != 200:
            msg = f"[AllegroGraph] SPARQL query failed: {response.status_code}\n{response.text}"
            raise RuntimeError(msg)

        data = response.json()
        bindings = data.get("results", {}).get("bindings", [])
        return [{k: v["value"] for k, v in row.items()} for row in bindings]

    def clear(self) -> None:
        sparql = (
            f"CLEAR GRAPH <{self.graph_uri}>"
            if self.graph_uri else
            "DELETE WHERE { ?s ?p ?o }"
        )
        self._run_update(sparql)

    def _run_update(self, sparql: str) -> None:
        response = requests.post(self.update_url, headers=self.headers_update, data={"update": sparql}, auth=self.auth, timeout=60)
        if response.status_code not in {200, 204, 201}:
            msg = f"[AllegroGraph] SPARQL update failed: {response.status_code}\n{response.text}"
            raise RuntimeError(msg)
