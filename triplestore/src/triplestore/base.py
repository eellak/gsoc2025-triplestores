# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0


from abc import ABC, abstractmethod
from typing import Any


class TriplestoreBackend(ABC):
    """
    Abstract base class for all triplestore backends.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @abstractmethod
    def load(self, filename: str) -> None:
        """
        Load RDF triples from a file into the triplestore.
        """
        pass

    @abstractmethod
    def add(self, subject: str, predicate: str, obj: str) -> None:
        """
        Add a single RDF triple to the store.
        """
        pass

    @abstractmethod
    def query(self, sparql: str) -> Any:
        """
        Execute a SPARQL query and return results.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Remove all triples from the triplestore.
        """
        pass
