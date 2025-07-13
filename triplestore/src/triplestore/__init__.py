# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0


from typing import Any

from .backends.jena import Jena
from .backends.oxigraph import Oxigraph
from .base import TriplestoreBackend


def hello() -> str:
    return "Hello from triplestore!"


_BACKENDS: dict[str, type[TriplestoreBackend]] = {
    "oxigraph": Oxigraph,
    "jena": Jena,
}


def TriplestoreFactory(backend: str, config: dict[str, Any]) -> TriplestoreBackend:
    """
    Create an instance of the appropriate triplestore backend.
    """
    backend = backend.lower()
    if backend not in _BACKENDS:
        msg = f"Unsupported triplestore backend: '{backend}'"
        raise ValueError(msg)
    return _BACKENDS[backend](config)
