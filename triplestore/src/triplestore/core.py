# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from .backends import get_backend
from .base import TriplestoreBackend
from .exceptions import BackendNotFoundError


class Triplestore:
    def __init__(self, backend: str, config: dict[str, Any]) -> None:
        try:
            self._backend: TriplestoreBackend = get_backend(backend)(config)
        except KeyError:
            msg = f"Backend '{backend}' is not supported."
            raise BackendNotFoundError(msg)

    def load(self, filename: str) -> None:
        self._backend.load(filename)

    def add(self, s: str, p: str, o: str) -> None:
        self._backend.add(s, p, o)

    def delete(self, s: str, p: str, o: str) -> None:
        self._backend.delete(s, p, o)

    def query(self, sparql: str) -> list[dict[str, str]]:
        return self._backend.query(sparql)
