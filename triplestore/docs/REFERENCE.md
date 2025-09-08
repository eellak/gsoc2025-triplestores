# Overview

The `Triplestore` class provides a unified Python interface to multiple RDF triplestore backends.  
It abstracts away backend-specific details and exposes a consistent API for common operations such as loading data, executing SPARQL queries, and modifying triples.

This abstraction layer allows developers to:
- Switch between different triplestore implementations (e.g., AllegroGraph, Apache Jena, GraphDB, Blazegraph, Oxigraph) without changing application code.
- Focus on querying and managing RDF data rather than handling low-level backend differences.

By using the `Triplestore`, you can write code that is portable across different RDF engines, simplifying experimentation and integration in projects that rely on linked data.

# Triplestore Objects

class triplestore.Triplestore(backend=None, config=None)

- backend: The name of the triplestore backend (default: None)
- config: A dictionary of configuration parameters for each backend

## Configuration Parameters

The `config` argument is a dictionary that specifies backend-specific options.  
Each backend supports different keys. Only the relevant keys for the selected backend need to be provided.

### Common keys
- **base_url**: The SPARQL base URL for remote triplestores.  
  Example: `config={"base_url": "http://localhost:10035"}`

- **graph**: The target named graph URI where triples will be stored. 
  Example: `config={"graph": "http://example.org/test"}`


### Backend-specific keys

#### AllegroGraph

- **repository**: Name of the target repository name.
  Example: `config={"repository": "repo2025"}`

- **catalog**: Name of the catalog inside the server.  
  Example: `config={"catalog": "root"}`

- **auth**: Authentication details when required (tuple of username, password).  
  Example: `config={"auth": ("user", "password")}`

#### Apache Jena

- **dataset**: Name of the dataset to connect to.
  Example: `config={"dataset": "dataset2025"}`

- **auth**: Authentication details when required (tuple of username, password).  
  Example: `config={"auth": ("user", "password")}`

#### Blazegraph

- **namespace**: Name of the target namespace.
  Example: `config={"namespace": "namespace2025"}`


#### GraphDB

- **repository**: Name of the target repository name.
  Example: `config={"repository": "repo2025"}`

- **auth**: Authentication details when required (tuple of username, password).  
  Example: `config={"auth": ("user", "password")}`
---


Example:
```python
store = Triplestore("oxigraph", config={"graph": "http://example.org/test"})
```

# Triplestore Functions
Each `Triplestore` objects exposes six methods:

## load(filename:str)
Load RDF triples from a Turtle file (.ttl) into the triplestore.
- If a graph is specified in the configuration, triples are loaded into that graph.
- Otherwise, they are loaded into the default graph.
```python
store.load("data.ttl")
```

## add(subject: str, predicate: str, object: str)
Insert a single RDF triple into the triplestore.
- If a graph is specified, the triple is added there.
- Otherwise, it is added to the default graph.
```python
store.add("http://example.org/s", "http://example.org/p", "http://example.org/o")
```

## delete(subject: str, predicate: str, object: str)
Remove a single RDF triple from the triplestore.
- If a graph is specified, the triple is removed from that graph.
- Otherwise, it is removed from the default graph.
```python
store.delete("http://example.org/s", "http://example.org/p", "http://example.org/o")
```

## query(sparql: str) -> List[Dict[str, str]]
Execute a SPARQL **SELECT** query and return the results as a list of dictionaries.
```python
results = store.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
```

## execute(sparql: str) -> Any
Execute any SPARQL query, including **SELECT, ASK, CONSTRUCT, DESCRIBE, and UPDATE(INSERT, DELETE etc)** operations.

Although it can also execute SELECT queries, `query()` is the recommended method for that use case.
 
- SELECT → returns list of dictionaries
- ASK → returns bool
- CONSTRUCT / DESCRIBE → returns a graph serialization or triple list (backend-dependent)
- UPDATE (INSERT, DELETE) → returns None
```python
results = store.execute("CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }")
```

## clear()
Remove all triples from the triplestore.
- If a graph is specified, only that graph is cleared.
- Otherwise, the default graph is cleared.
```python
store.clear()
```
