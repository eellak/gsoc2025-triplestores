# Testing the Library
This directory contains integration and unit tests for all triplestore backends supported by the library.
The goal of these tests is to ensure that the abstraction layer behaves consistently across different RDF engines, verifying that core operations such as loading, querying, and modifying triples work in the same way regardless of the chosen backend.


## Prerequisites
- For all backends **except Jena**, you must have a running instance of the respective triplestore (e.g., AllegroGraph, Blazegraph, GraphDB, Oxigraph).
- The Jena backend can automatically start and stop a local Fuseki server, so no manual setup is required.

## Test Overview
- **`test_all_backends.py`**:

Runs the complete test suite across all implemented backends.
- **`test_<backend>.py`**:

Backend-specific test files (e.g., test_oxigraph.py, test_jena.py, etc.).
Each of these validates the same set of core operations.


## Covered Test Cases
Each backend is tested for:
- **test_add_and_query_triple**: Verifies that a triple can be added and retrieved via SPARQL.
- **test_multiple_triples_query**: Ensures querying multiple triples with the same predicate–object pair works correctly.
- **test_delete_triple**: Confirms that deleting a triple removes it from the store.
- **test_query_roundtrip_add**: Checks the add–delete–add cycle for consistent state.
- **test_load_from_turtle_file**: Validates loading triples from a `.ttl` file.
- **test_clear**: Confirms that `clear()` removes all triples from the store.
- **test_clear_twice_is_safe**: Ensures that calling `clear()` multiple times is safe.
- **test_execute**: End-to-end test of `execute()`, covering `INSERT`, `DELETE`, `CLEAR`, `ASK`, `SELECT`, `DESCRIBE`, and `CONSTRUCT`.



## How to Run the Tests
Run the complete suite across all backends:
```bash
python test_all_backends.py
```

Run tests for a specific backend:
```bash
pytest test_<backend>.py
# Example:
pytest test_oxigraph.py
```

