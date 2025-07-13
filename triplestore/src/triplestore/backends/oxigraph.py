# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0


from pathlib import Path
from typing import Any

from pyoxigraph import DefaultGraph, NamedNode, Quad, RdfFormat, Store

from ..base import TriplestoreBackend


class Oxigraph(TriplestoreBackend):
    """
    Oxigraph backend using the Python API (pyoxigraph).
    """

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.store = Store()

    def load(self, filename: str) -> None:
        with Path(filename).open("rb") as f:
            self.store.bulk_load(f, RdfFormat.TURTLE)
        self.store.optimize()

    def add(self, subject: str, predicate: str, obj: str) -> None:
        quad = Quad(
            NamedNode(subject),
            NamedNode(predicate),
            NamedNode(obj),
            DefaultGraph()
        )
        self.store.add(quad)

    def query(self, sparql: str) -> Any:
        return list(self.store.query(sparql))

    def clear(self) -> None:
        self.store.clear()
