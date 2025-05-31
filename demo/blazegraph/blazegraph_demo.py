import requests
# For benchmarks
import time
import psutil
# For creating RDF file
import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
import re

# Benchmark helper
def print_benchmarks(phase_name, start_time):
    # Count Time
    elapsed = time.perf_counter() - start_time

    # CPU & Memory Utilization
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    mem_percent = memory.percent
    mem_used_mb = memory.used / (1024 ** 2)

    # Prints
    print(f"\n[{phase_name}]")
    print(f"Time: {elapsed:.2f} seconds")
    print(f"CPU Usage: {cpu_percent:.1f}%")
    print(f"Memory Usage: {mem_percent:.1f}% ({mem_used_mb:.1f} MB)")


# Blazegraph namespace endpoint
namespace = "demo"
base_url = f"http://localhost:9999/blazegraph/namespace/{namespace}/sparql"

# Import an RDF Turtle file to Blazegraph
with open("example.ttl", "rb") as f:
    turtle_data = f.read()
# Start Time Counter 
start = time.perf_counter()
# Μake POST request to import RDF data
headers = {"Content-Type": "text/turtle"}
response = requests.post(base_url, headers=headers, data=turtle_data)
print_benchmarks("Import RDF", start)
if response.status_code != 200:
    print(f"Import failed! Status code: {response.status_code}")
    print(response.text)

# Export all RDF triples 
query = """
CONSTRUCT {
  ?s ?p ?o
}
WHERE {
  ?s ?p ?o
}
"""

# Start Time Counter
start = time.perf_counter()
# Μake GET request to export RDF data
params = {"query": query}
headers = {"Accept": "text/turtle"}
response = requests.get(base_url, headers=headers, params=params)
print_benchmarks("Export RDF", start)
if response.status_code == 200:
    with open("exported.ttl", "wb") as f:
        f.write(response.content)
else:
    print(f"Export failed! Status code: {response.status_code}")
    print(response.text)

# Convert a CSV file to RDF triples
CSV_FILE = "Cleaned_AdministrativeArea_domain_stats.csv"
GRAPH_IRI = None 

# Load the CSV file
df = pd.read_csv(CSV_FILE, sep=",", on_bad_lines='skip', encoding="utf-8")
# Initialize an empty RDF graph
g = Graph()
# Define a namespace for predicates
EX = Namespace("http://example.org/stat#")

# Convert CSV file to RDF data
for idx, row in df.iterrows():
    area_uri = URIRef(f"http://example.org/area/{idx}")
    g.add((area_uri, RDF.type, EX.AdministrativeArea))

    for col in df.columns:
        value = row[col]
        if pd.notnull(value):
            safe_col = re.sub(r'\W+', '_', col.strip())
            pred = EX[safe_col]
            obj = Literal(str(value), datatype=XSD.string)
            g.add((area_uri, pred, obj))

# Serialize the RDF graph into Turtle format
csv_rdf = g.serialize(format="turtle")
headers = {"Content-Type": "text/turtle"}
# Start Time Counter
start = time.perf_counter()
# POST request to GraphDB Desktop
response = requests.post(base_url, data=csv_rdf, headers=headers)
# Check if success
if response.status_code == 204:
    print("CSV data imported successfully!")
else:
    print("CSV import failed!")
    print(response.status_code, response.text)
print_benchmarks("Import CSV as RDF", start)

# Define SPARQL queries to run and export
queries = {
    "People_with_name": """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?person ?name
        WHERE {
          ?person a foaf:Person ;
                  foaf:name ?name .
        }
    """,
    "Large_population_areas": """
        PREFIX ex: <http://example.org/stat#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?area ?pop
        WHERE {
          ?area rdf:type ex:AdministrativeArea ;
                ex:population ?pop .
          FILTER(xsd:integer(?pop) > 100000)
        }
        ORDER BY DESC(?pop)
        LIMIT 10
    """,
    "Query_named_graph": f"""
        PREFIX ex: <http://example.org/stat#>
        SELECT ?area ?domain
        WHERE {{
          GRAPH <{GRAPH_IRI}> {{
            ?area a ex:AdministrativeArea ;
                   ex:domainCount ?domain .
          }}
        }}
        LIMIT 10
    """ if GRAPH_IRI else None,
    "Alice_is_a_Human" : """
    PREFIX ex: <http://example.org/>
    SELECT ?s
    WHERE {
    ?s a ex:Human .
    }
    """
}

# Headers for SPARQL query
sparql_headers = {
    "Content-Type": "application/sparql-query",
    "Accept": "text/csv"
}

# Loop for queries
for title, query in queries.items():
    if not query:
        continue
    start = time.perf_counter()
    resp = requests.post(base_url, data=query, headers=sparql_headers)
    if resp.status_code == 200:
        filename = title + ".csv"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(resp.text)
        print(f"Exported query '{title}' to '{filename}'")
    else:
        print(f"Query '{title}' failed!", resp.status_code, resp.text)
    print_benchmarks(f"Query: {title}", start)
