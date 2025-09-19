# `triplestore` (package internals)

## Overview
This document describes the **internal layout and design** of the `src/triplestore/` package.
It is aimed at contributors who want to understand how the library is organized internally—how backends are discovered, registered, and instantiated, and how they interact through the unified API surface.

## Directory Structure
```text
src/triplestore/
├── backends/             # Individual backend implementations
│   ├── __init__.py
│   ├── allegrograph.py
│   ├── blazegraph.py
│   ├── graphdb.py
│   ├── jena.py
│   ├── jena_utils.py
│   └── oxigraph.py
├── __init__.py           # Public API surface
├── base.py               # Abstract base class defining the backend interface
├── exceptions.py         # Custom exception hierarchy for consistent error handling
├── registration.py       # Backend discovery and availability via entry points
├── triplestore.py        # Factory function
└── utils.py              # Shared utilities

```


## Public API Surface (`__init__.py`)
The `__init__.py` file defines the library’s public API surface.
- It re-exports the core classes (`Triplestore`, `TriplestoreBackend`) used to construct and manage backend connections.
- It exposes the key exceptions (`BackendNotFoundError`, `BackendNotInstalledError`, `TriplestoreError`, `TriplestoreMissingConfigValue`) so they can be imported directly from triplestore without referencing internal modules.
- It makes available the utility function `available_backends`, which lists the backends currently usable in the environment.

## Base Interface (`base.py`)
All concrete backends inherit from `TriplestoreBackend` and must implement a common set of operations:
- `load(filename: str) -> None`:
Load RDF data from a Turtle (`.ttl`) file into the store.

- `add(subject: str, predicate: str, object: str) -> None`: 
Insert a single triple.

- `delete(subject: str, predicate: str, object: str) -> None`:
Remove a single triple.

- `query(sparql: str) -> Any`: 
Execute a SPARQL `SELECT` query. Returns a list of dictionaries, one per result binding.

- `execute(sparql: str) -> Any`:
Execute any SPARQL query form:
  - `ASK` → returns a `bool`
  - `CONSTRUCT` / `DESCRIBE` → returns a Turtle string
  - `UPDATE` operations → return `None`

- `clear() -> None`:
Remove all data from the store.

---

Each backend handle its own details (connections, authentication, graph namespaces), but the public interface exposed to users remains uniform across implementations.


## Exceptions (`exceptions.py`)
The package defines a small hierarchy of custom exceptions to provide consistent error handling:
- `TriplestoreError`:
Base class for all library-specific exceptions.

- `BackendNotFoundError`:
Raised when the requested backend name is not implemented in the current installation.

- `BackendNotInstalledError`:
Raised when the backend is implemented in the library but cannot be imported, typically due to missing optional dependencies or extras.

- `TriplestoreMissingConfigValue`:
Raised by `validate_config()` when required configuration keys are absent.


## Backend Discovery & Registration (`registration.py`)

Backends are discovered dynamically through the entry point group [`triplestore.backends`](/triplestore/pyproject.toml). At runtime, a registry is built from installed entry points, and `available_backends()` returns only those that can actually be imported. This mechanism supports optional extras: unused backends can ship with the package but remain inactive unless their dependencies are installed.

## Constructor (`triplestore.py`)
The Triplestore() function is the main entry point for creating backend instances: 
```python
Triplestore(backend: str, config: dict[str, Any]) -> TriplestoreBackend
```

It performs the following steps:
- **Validates inputs**: ensures `backend` is a non-empty string and `config` is a dictionary.
- **Resolves the backend class** from the internal registry of discovered entry points.
- **Checks for errors** like `BackendNotFoundError` and `BackendNotInstalledError`.
- **Instantiates and returns** the backend as a ready-to-use `TriplestoreBackend` object.

## Shared Utilities (`utils.py`)
This module provides helper functions for backend configuration and environment detection:
- `validate_config(user_config, *, required_keys, optional_defaults, alias_map, backend_name)`:
Normalizes a backend configuration dictionary by:
  - Resolving key aliases,
  - Filling in optional defaults,
  - Verifying all required keys are present,
  - Preserving unknown keys (with a warning).
  - Raises `TriplestoreMissingConfigValue` if required keys are missing.
- `detect_graphdb_url()`: Returns a best-effort base URL for a local GraphDB instance, including WSL host detection. This makes quick-start examples work out of the box.

## Minimal Example
**Pick a backend & count triples**
```python
from triplestore import Triplestore, available_backends

print("Available backends:", available_backends())

# Jena (auto‑runs local Fuseki)
store = Triplestore("jena", config={"name": "ds"})
store.load("data.ttl")
print(store.query("SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }"))
store.clear()
```