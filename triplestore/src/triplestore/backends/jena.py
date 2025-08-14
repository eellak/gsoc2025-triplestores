# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0


import gzip
import shutil
import tempfile
from pathlib import Path
from typing import Any

import requests

from triplestore.backends.jena_utils import add_graph_clause_if_needed, create_config_and_run_fuseki, stop_fuseki_server
from triplestore.base import TriplestoreBackend


class Jena(TriplestoreBackend):
    """
    A triplestore backend implementation for Apache Jena Fuseki using its HTTP REST API.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize the Jena backend with the given configuration.

        Parameters:
        config : dict
            A configuration dictionary containing connection parameters:
            - base_url (optional): The base URL of the Jena Fuseki server.
            - dataset : The name of the dataset to connect to.
            - auth (optional): Tuple (username, password) for HTTP Basic Auth.
            - graph (optional): Named graph URI for scoped operations.
        """
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:3030")
        self.dataset = config.get("dataset", "test_dataset")
        create_config_and_run_fuseki(self.dataset)
        self.auth = config.get("auth")
        self.graph_uri = config.get("graph")
        if self.graph_uri:
            self._effective_graph = self.graph_uri
        else:
            self._effective_graph = "urn:app:default"

        self.load_url = f"{self.base_url}/{self.dataset}/data"
        self.query_url = f"{self.base_url}/{self.dataset}/query"
        self.update_url = f"{self.base_url}/{self.dataset}/update"

        self.headers_load = {"Content-Type": "text/turtle"}
        self.headers_query = {"Accept": "application/sparql-results+json"}
        self.headers_update = {"Content-Type": "application/sparql-update"}

        self._ensure_dataset_exists()

    def load(self, filename: str) -> None:
        """
        Load RDF triples from a Turtle (.ttl) file into the Jena dataset.

        If a named graph URI is provided in the configuration, data is loaded into that graph.

        Parameters:
        filename : str
            Path to the Turtle (.ttl) file to be loaded.

        Raises:
        RuntimeError
            If the server returns an error status during data loading.
        """
        path = Path(filename)
        if not path.exists():
            msg = f"[APACHE JENA] File not found: {filename}"
            raise FileNotFoundError(msg)

        params = {"graph": self._effective_graph}

        tmp_gz = tempfile.NamedTemporaryFile(prefix="ttl-", suffix=".ttl.gz", delete=False)
        tmp_gz_path = Path(tmp_gz.name)
        try:
            with path.open("rb") as fin, gzip.open(tmp_gz, "wb", compresslevel=9) as fout:
                shutil.copyfileobj(fin, fout)
            tmp_gz.close()

            headers = {
                "Content-Type": "text/turtle",
                "Content-Encoding": "gzip",
                "Connection": "keep-alive",
            }
            with tmp_gz_path.open("rb") as fz:
                response = requests.post(self.load_url, params=params, data=fz, headers=headers,
                                         auth=self.auth, timeout=(60, None))

            if response.status_code not in {200, 201, 204}:
                msg = f"[APACHE JENA] Import failed with status {response.status_code}:\n{response.text}"
                raise RuntimeError(msg)
        finally:
            try:
                tmp_gz_path.unlink(missing_ok=True)
            except Exception:
                pass

    def add(self, s: str, p: str, o: str) -> None:
        """
        Add a triple to the Jena store.

        Uses the named graph if specified in the config.
        """
        triple = f"<{s}> <{p}> <{o}> ."
        sparql = (
            f"INSERT DATA {{ GRAPH <{self._effective_graph}> {{ {triple} }} }}"
        )
        self._run_update(sparql)

    def delete(self, s: str, p: str, o: str) -> None:
        """
        Delete a triple from the Jena store.

        Uses the named graph if specified in the config.
        """
        triple = f"<{s}> <{p}> <{o}> ."
        sparql = (
            f"DELETE DATA {{ GRAPH <{self._effective_graph}> {{ {triple} }} }}"
        )
        self._run_update(sparql)

    def query(self, sparql: str) -> list[dict[str, str]]:
        """
        Execute a SPARQL query against the Jena dataset.

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
        final_query = (
            add_graph_clause_if_needed(sparql, self._effective_graph)
            if getattr(self, "_effective_graph", None) == "urn:app:default"
            else sparql
        )

        response = requests.post(self.query_url, headers=self.headers_query, data={"query": final_query}, auth=self.auth, timeout=None)

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
        """
        Remove all triples from the dataset.

        If a named graph is specified, it is dropped silently (no error if it doesn't exist).
        Otherwise, the default graph is cleared.
        """
        sparql = f"DROP SILENT GRAPH <{self._effective_graph}>"

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
        response = requests.post(self.update_url, headers=self.headers_update, data=sparql, auth=self.auth, timeout=None)

        if response.status_code not in {200, 204}:
            msg = f"[APACHE JENA] Update failed with status {response.status_code}:\n{response.text}"
            raise RuntimeError(msg)

    def _ensure_dataset_exists(self) -> None:
        """
        Ensure that the configured dataset exists in Apache Jena Fuseki.
        If it does not, attempt to create it using the Admin REST API.

        Raises:
        RuntimeError
            If unable to connect to the server or if dataset creation fails.
        """
        admin_url = f"{self.base_url}/$/datasets"

        try:
            response = requests.get(admin_url, auth=self.auth, timeout=60)
            if response.status_code not in {200, 401, 403}:
                msg = f"[APACHE JENA] Admin responded with unexpected status: {response.status_code}\n{response.text}"
                raise RuntimeError(msg)
        except requests.RequestException as e:
            msg = f"[APACHE JENA] Could not connect to Fuseki admin at {admin_url}: {e}"
            raise RuntimeError(msg) from e

        try:
            datasets = response.json().get("datasets", [])
        except ValueError:
            datasets = []

        existing_names = [ds.get("ds.name", "").lstrip("/") for ds in datasets]
        if self.dataset in existing_names:
            return

        db_type = "tdb2"
        db_path = getattr(self, "db_path", None)

        data = {"dbName": self.dataset, "dbType": db_type}
        if db_path:
            data["dbPath"] = db_path

        try:
            response = requests.post(admin_url, data=data, auth=self.auth, timeout=60)
        except requests.RequestException as err:
            msg = f"[APACHE JENA] Could not create dataset '{self.dataset}': {err}"
            raise RuntimeError(msg) from err

        if response.status_code != 200:
            if response.status_code in {401, 403}:
                msg = f"[APACHE JENA] Permission denied creating dataset '{self.dataset}'.\nAdmin credentials required.\nResponse: {response.text}"
                raise RuntimeError(msg)
            msg = f"[APACHE JENA] Failed to create dataset '{self.dataset}': {response.status_code}\n{response.text}"
            raise RuntimeError(msg)

    def stop_server(self) -> bool:
        return stop_fuseki_server()
