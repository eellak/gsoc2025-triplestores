# Triplestore Demo Scripts

This folder contains example scripts that showcase how to use the **`triplestore`** library to load RDF data, run SPARQL queries, and clear graphs across different backends. It also emphasizes the abstraction between triplestores.

## Contents

- `allegrograph.py` – Demo for **AllegroGraph**
- `blazegraph.py` – Demo for **Blazegraph**
- `graphdb.py` – Demo for **GraphDB**
- `jena.py` – Demo for **Apache Jena Fuseki**
- `oxigraph.py` – Demo for **Oxigraph**
- `demo.py` – **Unified demo** script that runs on any available backend, selected via a command-line argument.

All demos:
- load the file **`triplestore/data.ttl`**
- count triples in a test graph (`http://example.org/test`)
- clear the graph and display the updated triple count

⚠️ **Note:** Make sure that the file `triplestore/data.ttl` exists, as all demo scripts depend on it.

## How to Run

**Prerequisites:**  
- The `triplestore` library must be installed.  
- Backends must be running and accessible (except for **Jena**, which is automatically started by the script).

### Unified demo for any backend

```bash
python demo.py --backend <backend>
```
Or
```bash
python demo.py -b <backend>
```
Use the `--backend` or `-b` parameter to select which triplestore to run the demo with.

### Individual backend demos

Each file can also be run directly, for example:

```bash
python <backend>.py
```
These scripts are equivalent to `demo.py --backend <name>` but dedicated to each backend.

---

The default configuration used is:
```python
config = {"name": "test2025", "graph": "http://example.org/test"}
```
You can extend this with base_url, credentials, or other backend-specific parameters if needed.

## Expected Output
When running a demo, you should see output similar to:

```text
 Loading data…
 Loaded. Triple count in <http://example.org/test>: 42

 Clearing graph…
 Cleared. Triple count in <http://example.org/test>: 0
```