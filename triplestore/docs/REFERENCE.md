# Overview

The `Triplestore` class provides a unified Python interface to multiple RDF triplestore backends.  
It abstracts away backend-specific details and exposes a consistent API for common operations such as loading data, executing SPARQL queries, and modifying triples.

This abstraction layer allows developers to:
- Switch between different triplestore implementations (e.g., AllegroGraph, Apache Jena, GraphDB, Blazegraph, Oxigraph) without changing application code.
- Focus on querying and managing RDF data rather than handling low-level backend differences.

By using the `Triplestore`, you can write code that is portable across different RDF engines, simplifying experimentation and integration in projects that rely on linked data.

# Triplestore Objects

`class triplestore.Triplestore(backend: str, config: dict[str, Any])`

**Purpose**: Create a backend-specific client instance under a unified API.  
This constructor abstracts away the differences between triplestore implementations and ensures a consistent interface across all supported backends.

**Arguments**

- **backend** (`str`, required): The backend identifier, e.g., `"allegrograph"` | `"jena"` | `"graphdb"` | `"blazegraph"` | `"oxigraph"`. The backend must be both supported by the library and available in the current environment. 
- **config** (`dict[str, Any]`, required): A dictionary of configuration parameters for the selected backend. See [Configuration Parameters](#configuration-parameters) below for common and backend-specific keys.

**Returns**
A `Triplestore` instance bound to the chosen backend.

**Exceptions**
- `BackendNotFoundError`: Raised when the requested backend name is not registered in the current installation of `triplestore`.
This means that the backend is not supported by the installed package.
- `BackendNotInstalledError`: Raised when the backend is known to the package (registered) but cannot be imported because its optional dependencies are missing.  
Typically resolved by installing the backend extra with:
```bash
pip install triplestore[<backend>]
```
- `ValueError`: Raised when `backend` is a blank string.
- `TypeError`: 
Raised in two cases:
  - When the argument types are invalid (e.g., `backend` is not a `str`, or `config` is not a `dict`).  
  - When the resolved backend class does **not** implement the required `TriplestoreBackend` interface (developer/configuration error).

## Configuration Parameters

The `config` argument is a dictionary that specifies backend-specific options.  
Each backend supports different keys. Only the relevant keys for the selected backend need to be provided.

### Common keys
- `name` (str, required): **Unified identifier** for the dataset/repository/namespace, depending on the backend.
Replaces backend-specific keys such as `repository` (GraphDB, AllegroGraph), `namespace` (Blazegraph), or `dataset` (Jena).
Example: `config={"name": "test2025"}`

- `base_url` (str, optional): The SPARQL base URL for remote triplestores.  
  Example: `config={"base_url": "http://localhost:10035"}`

- `graph` (str, IRI/CURIE, optional): The target named graph for read/write operations. If omitted, defaults to the backend’s default graph.
  Example: `config={"graph": "http://example.org/test"}`

### Backend-specific keys

#### AllegroGraph

- `catalog` (str, optional): Name of the catalog inside the server.  
  Example: `config={"catalog": "root"}`

- `auth` (tuple[str, str], required): Authentication material when required.
  Example: `config={"auth": ("user", "password")}`

#### Apache Jena

- `auth`: (tuple[str, str], optional): Authentication material when required.
  Example: `config={"auth": ("user", "password")}`

#### GraphDB

- `auth`: (tuple[str, str], optional): Authentication material when required.
  Example: `config={"auth": ("user", "password")}`
---

**Exceptions**
- `ValueError`
  - When one or more required configuration keys are missing (e.g., `name` for GraphDB, Jena, Blazegraph, AllegroGraph).
  - When a configuration value is invalid (e.g., `auth` not provided as a `(username, password)` tuple).
  - When AllegroGraph credentials are missing both in `config` and environment variables (`AG_USERNAME`, `AG_PASSWORD`).  
- `RuntimeError`: 
  - When the server cannot be reached (e.g., GraphDB, Jena, Blazegraph, AllegroGraph).
  - When repository or dataset or namespace creation fails.

Example:
```python
store = Triplestore("oxigraph", config={"graph": "http://example.org/test"})
```

# Triplestore Functions
Each `Triplestore` objects exposes six methods:

## load(filename:str)
**Purpose**: Load RDF triples from a Turtle file (`.ttl`) into the triplestore.

**Arguments**: 

- `filename` (str, required): Absolute or relative path to the RDF file to be loaded (must be in Turtle `.ttl` format).  
  Other serializations are not supported.

**Returns**

- `None` — this method does not return a value.

**Behavior**

- If `config["graph"]` is set, triples are loaded into that named graph.
- Otherwise, triples are loaded into the backend’s default graph.

**Exceptions**
- `FileNotFoundError`: If the specified file does not exist.
- `RuntimeError`: If the backend server rejects the request or responds with an error status.

**Example**:
```python
store.load("data.ttl")
```

## add(subject: str, predicate: str, object: str)
**Purpose**: Insert a single RDF triple into the triplestore.

**Arguments**:
- `subject` (str, required): The subject IRI of the triple.  
- `predicate` (str, required): The predicate IRI of the triple.  
- `object` (str, required): The object IRI of the triple.  

**Returns**

- `None` — this method does not return a value.

**Behavior**

- If `config["graph"]` is set, the triple is inserted into that named graph.
- Otherwise, the triple is inserted into the backend’s default graph.

**Exceptions**
- `RuntimeError`: If the backend rejects the update or responds with a non-success HTTP status.  

```python
store.add("http://example.org/s", "http://example.org/p", "http://example.org/o")
```

## delete(subject: str, predicate: str, object: str)
**Purpose**: Remove a single RDF triple from the triplestore.

**Arguments**:
- `subject` (str, required): The subject IRI of the triple.  
- `predicate` (str, required): The predicate IRI of the triple.  
- `object` (str, required): The object IRI of the triple. 

**Returns**

- `None` — this method does not return a value.

**Behavior**

- If `config["graph"]` is set, the triple is removed from that named graph.
- Otherwise, the triple is removed from the backend’s default graph.

**Exceptions**
- `RuntimeError`: If the backend rejects the update or responds with a non-success HTTP status.
```python
store.delete("http://example.org/s", "http://example.org/p", "http://example.org/o")
```

## query(sparql: str) -> list[dict[str, str]]
**Purpose**: Execute a SPARQL **SELECT** query and return the results as a list of dictionaries.

**Arguments**:
- `sparql` (str, required): A valid SPARQL `SELECT` query string.

**Returns**:

`list[dict[str,str]]` - a list of result rows.  
  Each row is represented as a dictionary where the keys are variable names from the query and the values are their corresponding bindings.

**Exceptions**
- `RuntimeError`: Ιf the query execution fails or the backend responds with a non-success HTTP status.  

```python
results = store.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
```

## execute(sparql: str) -> Any
**Purpose**: Execute any SPARQL query, including **SELECT, ASK, CONSTRUCT, DESCRIBE, and UPDATE(INSERT, DELETE etc)** operations.
 
**Arguments**:
- `sparql` (str, required): A valid SPARQL query or update string.

**Returns**:
- `list[dict[str, str]]` — for `SELECT` queries, a list of result rows as variable bindings.  
- `bool` — for `ASK` queries.  
- `str` — for `CONSTRUCT` or `DESCRIBE` queries, typically an RDF graph serialized in Turtle (exact format may vary by backend).  
- `None` — for `UPDATE` operations (`INSERT`, `DELETE`, `CLEAR`, etc.).

**Behavior**

Although it can also execute SELECT queries, `query()` is the recommended method for that use case.

**Exceptions**
- `RuntimeError`: Ιf the operation fails or the backend responds with a non-success HTTP status.

```python
results = store.execute("CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }")
```

## clear()
**Purpose**:

Remove all triples from the triplestore.

**Arguments**:
- None

**Returns**:
- `None` — this method does not return a value.

**Behavior**:
- If a named graph is configured (`config["graph"]`), only that graph is cleared.  
- Otherwise, the default graph is cleared.  

**Exceptions**:
- `RuntimeError`: Ιf the operation fails or the backend responds with a non-success HTTP status.

```python
store.clear()
```
