# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0


from pathlib import Path
from typing import Any, Optional

from pyoxigraph import DefaultGraph, NamedNode, Quad, QueryBoolean, QueryTriples, RdfFormat, Store

from triplestore.base import TriplestoreBackend


class Oxigraph(TriplestoreBackend):
    """
    A triplestore backend implementation for Oxigraph using the pyoxigraph API.

    """
    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize the Oxigraph backend with the given configuration.

        Parameters:
        config : dict
            Expected keys (optional):
              - "graph": str -> default named graph to use (if provided).
        """
        super().__init__(config)
        self.store = Store()
        self.graph_uri: Optional[str] = config.get("graph")
        if self.graph_uri:
            self.store.add_graph(NamedNode(self.graph_uri))

    def load(self, filename: str) -> None:
        """
        Load RDF triples from a Turtle (.ttl) file into the Oxigraph store.

        Parameters:
        filename : str
            Path to the Turtle (.ttl) file to be loaded.
        """
        path = Path(filename)
        if not path.exists():
            msg = f"[Oxigraph] File not found: {filename}"
            raise FileNotFoundError(msg)

        with Path(filename).open("rb") as f:
            if self.graph_uri:
                self.store.bulk_load(f, RdfFormat.TURTLE, to_graph=NamedNode(self.graph_uri))
            else:
                self.store.bulk_load(f, RdfFormat.TURTLE, to_graph=DefaultGraph())
        self.store.optimize()

    def add(self, subject: str, predicate: str, obj: str) -> None:
        """
        Add a triple to the Oxigraph store.

        Parameters:
        subject : str
            The subject URI of the triple.
        predicate : str
            The predicate URI of the triple.
        obj : str
            The object URI of the triple.
        """
        gterm = NamedNode(self.graph_uri) if self.graph_uri else DefaultGraph()
        quad = Quad(NamedNode(subject), NamedNode(predicate), NamedNode(obj), gterm)
        self.store.add(quad)

    def delete(self, subject: str, predicate: str, obj: str) -> None:
        """
        Delete a triple from the Oxigraph store.

        Parameters:
        subject : str
            The subject URI of the triple to remove.
        predicate : str
            The predicate URI of the triple to remove.
        obj : str
            The object URI of the triple to remove.
        """
        gterm = NamedNode(self.graph_uri) if self.graph_uri else DefaultGraph()
        quad = Quad(NamedNode(subject), NamedNode(predicate), NamedNode(obj), gterm)
        self.store.remove(quad)

    def query(self, sparql: str) -> Any:
        """
        Execute a SPARQL query (SELECT / ASK / CONSTRUCT / DESCRIBE).

        Parameters
        ----------
        sparql : str
            A valid SPARQL query string.

        Returns
        -------
        bool
            If the query is an ASK, returns True or False.
        str
            If the query is a CONSTRUCT or DESCRIBE, returns an RDF graph
            serialized in Turtle format.
        list
            If the query is a SELECT, returns a list of bindings (dictionaries).
        Any
            Raw result object if the type cannot be determined.
        """
        res = self.store.query(sparql)

        # ASK
        if isinstance(res, QueryBoolean):
            return bool(res)

        # CONSTRUCT / DESCRIBE
        if isinstance(res, QueryTriples):
            return res.serialize(format=RdfFormat.TURTLE).decode("utf-8")

        # SELECT
        try:
            iter(res)
        except TypeError:
            return res
        else:
            return list(res)

    def execute(self, sparql: str) -> Any:
        """
        Execute any SPARQL operation.

        Parameters
        ----------
        sparql : str
            A valid SPARQL query or update string.

        Returns
        -------
        None
            For SPARQL Update operations (INSERT, DELETE, CLEAR, etc.).
        bool
            For ASK queries.
        list
            For SELECT queries, a list of solution mappings.
        str
            For CONSTRUCT or DESCRIBE queries, an RDF graph serialized in Turtle.
        """
        qstrip = sparql.lstrip()
        head = qstrip.split(None, 1)[0].lower() if qstrip else ""

        update_heads = {
            "insert", "delete", "clear", "load", "create",
            "drop", "with", "modify", "add", "move", "copy"
        }
        if head in update_heads:
            self.store.update(sparql)
            return None

        return self.query(sparql)

    def clear(self) -> None:
        """
        Remove all triples from the store.

        Notes
        -----
        - If a named graph URI is configured, only that graph is cleared.
        - Otherwise, the default graph is cleared.
        """
        if self.graph_uri:
            self.store.clear_graph(NamedNode(self.graph_uri))
        else:
            self.store.clear_graph(DefaultGraph())
