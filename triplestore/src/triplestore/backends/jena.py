# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0


from pathlib import Path
from typing import Any

import requests

from ..base import TriplestoreBackend


class Jena(TriplestoreBackend):
    """
    Apache Jena Fuseki backend using the HTTP REST API.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:3030")
        self.dataset = config.get("dataset", "test_dataset")
        self.auth = config.get("auth")

        self.load_url = f"{self.base_url}/{self.dataset}/data"
        self.query_url = f"{self.base_url}/{self.dataset}/query"

        self.headers_query = {"Accept": "application/sparql-results+json"}
        self.headers_load = {"Content-Type": "text/turtle"}

    def load(self, filename: str) -> None:
        rdf_data = Path(filename).read_bytes()
        response = requests.post(self.load_url, headers=self.headers_load, data=rdf_data, auth=self.auth, timeout=60)

        if response.status_code not in {200, 204}:
            msg = f"[APACHE JENA] Import failed with status {response.status_code}:\n{response.text}"
            raise RuntimeError(msg)

    def add(self, s: str, p: str, o: str) -> None:
        triple = f"<{s}> <{p}> <{o}> ."
        sparql = f"INSERT DATA {{ {triple} }}"
        self._run_update(sparql)

    def delete(self, s: str, p: str, o: str) -> None:
        triple = f"<{s}> <{p}> <{o}> ."
        sparql = f"DELETE DATA {{ {triple} }}"
        self._run_update(sparql)

    def query(self, sparql: str) -> list[dict[str, str]]:
        response = requests.post(self.query_url, headers=self.headers_query, data={"query": sparql}, auth=self.auth, timeout=60)

        if response.status_code != 200:
            msg = f"[APACHE JENA] Query failed with status {response.status_code}:\n{response.text}"
            raise RuntimeError(msg)

        data = response.json()
        bindings = data.get("results", {}).get("bindings", [])
        return [
            {k: v["value"] for k, v in row.items()}
            for row in bindings
        ]

    def clear(self) -> None:
        sparql = "DELETE WHERE { ?s ?p ?o }"
        self._run_update(sparql)

    def _run_update(self, sparql: str) -> None:
        update_url = f"{self.base_url}/{self.dataset}/update"
        headers = {"Content-Type": "application/sparql-update"}

        response = requests.post(update_url, headers=headers, data=sparql, auth=self.auth, timeout=60)

        if response.status_code not in {200, 204}:
            msg = f"[APACHE JENA] Update failed with status {response.status_code}:\n{response.text}"
            raise RuntimeError(msg)
