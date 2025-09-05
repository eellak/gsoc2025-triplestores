# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

# Dynamic backend discovery for the `triplestore` package.
# This module discovers those entry points at runtime and exposes:
#   - available_backends(): returns the names that can actually be imported now
#   - Triplestore(name, config): a factory returning a backend instance

from importlib import import_module, metadata
from typing import Any

from triplestore.base import TriplestoreBackend
from triplestore.exceptions import BackendNotFoundError, BackendNotInstalledError

REGISTRY: dict[str, str] = {}
DISCOVERED = False

# Optional mapping used to suggest the correct extra in error messages.
EXTRA_HINT = {
    "allegrograph": "allegrograph",
    "blazegraph": "blazegraph",
    "graphdb": "graphdb",
    "jena": "jena",
    "oxigraph": "oxigraph",
}


def discover_backends() -> None:
    """
    Populate the in-memory backend registry from installed entry points (one-time).
    """
    global DISCOVERED
    if DISCOVERED:
        return

    try:
        eps = metadata.entry_points(group="triplestore.backends")
    except TypeError:
        eps = metadata.entry_points().get("triplestore.backends", [])

    REGISTRY.clear()
    for ep in eps:
        REGISTRY[ep.name.lower()] = ep.value

    DISCOVERED = True


def is_importable(cls_path: str) -> bool:
    """
    Check whether the target "package.module:Class" can be imported and the
    backend's declared requirements (if any) are present.

    Returns
    -------
    bool
        True if importable, False otherwise.
    """
    try:
        module_path, class_name = cls_path.split(":")
        mod = import_module(module_path)
        getattr(mod, class_name)
    except (ValueError, ModuleNotFoundError, ImportError, AttributeError):
        return False
    else:
        return True


def available_backends() -> list[str]:
    """
    Compute the list of backend names that are importable right now.

    Returns
    -------
    list[str]
        Sorted list of importable backend names.
    """
    discover_backends()
    names: list[str] = []
    for name, cls_path in REGISTRY.items():
        if is_importable(cls_path):
            names.append(name)
    return sorted(names)


def Triplestore(backend: str, config: dict[str, Any]) -> TriplestoreBackend:
    """
    Factory that returns an instance of the requested triplestore backend.

    Parameters
    ----------
    backend : str
        The public backend name (e.g., "oxigraph").
    config : dict[str, Any]
        Backend-specific configuration.

    Returns
    -------
    TriplestoreBackend
        A concrete backend instance.

    Raises
    ------
    BackendNotFoundError
        No entry point is registered under this name in the installed distribution.
    BackendNotInstalledError
        An entry point exists, but the backend is not importable (missing optional deps).
    TypeError
        The loaded class does not implement `TriplestoreBackend`.
    """
    discover_backends()
    name = backend.lower()
    cls_path = REGISTRY.get(name)

    supported = ", ".join(sorted(REGISTRY.keys())) or "none"
    available = ", ".join(available_backends()) or "none"

    # Unsupported in the installed distribution
    if not cls_path:
        msg = (
            f"Backend '{name}' is not recognized by this installation of 'triplestore'.\n\n"
            f"Supported backends in this package: {supported}.\n"
            f"Currently available backends: {available}.\n"
        )
        raise BackendNotFoundError(msg)

    # Supported but not importable
    if not is_importable(cls_path):
        extra = EXTRA_HINT.get(name, name)
        msg = (
            f"Backend '{name}' is not installed.\n"
            f"To install it, run: pip install triplestore[{extra}].\n\n"
            f"Supported backends: {supported}.\n"
            f"Currently available backends: {available}\n"
        )
        raise BackendNotInstalledError(msg)

    module_path, class_name = cls_path.split(":")
    cls = getattr(import_module(module_path), class_name)
    obj = cls(config)

    if not isinstance(obj, TriplestoreBackend):
        msg = f"{cls_path} does not implement TriplestoreBackend"
        raise TypeError(msg)

    return obj


__all__: list[str] = []
