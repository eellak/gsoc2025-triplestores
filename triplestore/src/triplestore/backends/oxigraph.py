# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0


from pathlib import Path
from typing import Any

from pyoxigraph import DefaultGraph, NamedNode, Quad, RdfFormat, Store

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
            A configuration dictionary. Currently unused but required for interface compatibility.
        """
        super().__init__(config)
        self.store = Store()

    def load(self, filename: str) -> None:
        """
        Load RDF triples from a Turtle (.ttl) file into the Oxigraph store.

        Parameters:
        filename : str
            Path to the Turtle (.ttl) file to be loaded.
        """
        with Path(filename).open("rb") as f:
            self.store.bulk_load(f, RdfFormat.TURTLE)
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
        quad = Quad(NamedNode(subject), NamedNode(predicate), NamedNode(obj), DefaultGraph())
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
        quad = Quad(NamedNode(subject), NamedNode(predicate), NamedNode(obj), DefaultGraph())
        self.store.remove(quad)

    def query(self, sparql: str) -> Any:
        """
        Execute a SPARQL query against the Oxigraph store.

        Parameters:
        sparql : str
            The SPARQL query string.

        Returns:
        Any
            The list of results returned by the query engine.
        """
        return list(self.store.query(sparql))

    def clear(self) -> None:
        """
        Remove all data from the Oxigraph store.
        """
        self.store.clear()
