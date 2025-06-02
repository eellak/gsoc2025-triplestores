# Triplestore Abstraction Library

This library provides a unified interface for interacting
with various triplestore backends.
It allows developers to write code that is agnostic
to the underlying triplestore implementation.

## Features

- Common API for multiple triplestore backends
- Easy integration and backend switching
- Support for basic CRUD operations on triples
- Extensible for new triplestore implementations

## Supported Backends

- TODO: *list supported triplestores here, e.g., Apache Jena, Virtuoso, Blazegraph*

## Installation

```bash
pip install triplestore
```

## Usage

```python
from triplestore import Triplestore

# Initialize with desired backend
store = Triplestore(backend="jena", config={...})

# Load triples
store.load(data_filename)

# Add a triple
store.add(subject, predicate, obj)

# Query triples
results = store.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
```
