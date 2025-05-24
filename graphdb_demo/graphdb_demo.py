# For import & export
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
    print(f"[{phase_name}]")
    print(f"Time: {elapsed:.2f} seconds")
    print(f"CPU Usage: {cpu_percent:.1f}%")
    print(f"Memory Usage: {mem_percent:.1f}% ({mem_used_mb:.1f} MB)")

# Repo's info
GDB_URL = "http://localhost:7200"
# Repository with Reasoning
REPO_ID = "maira_repo"
# Repository without Reasoning
# REPO_ID = "maira_repo_none"
FILE_PATH = "example.ttl"
CSV_FILE = "AdministrativeArea_domain_stats.csv"
GRAPH_IRI = "" 

# Import Data from a TTL File
# URL creation
import_url = f"{GDB_URL}/repositories/{REPO_ID}/statements"
# Load RDF data from file
with open(FILE_PATH, "rb") as f:
    rdf_data = f.read()

headers = {
    "Content-Type": "text/turtle"  
}
params = {}
if GRAPH_IRI:
    params["context"] = f"<{GRAPH_IRI}>"

# Start Time Counter
start = time.perf_counter()
# POST request to GraphDB Desktop
response = requests.post(import_url, data=rdf_data, headers=headers, params=params)
# Check if success
if response.status_code == 204:
    print("RDF data imported successfully!")
else:
    print("Import failed!")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
print_benchmarks("Import RDF", start)


# Import Data from a CSV File
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
# Start Time Counter
start = time.perf_counter()
# POST request to GraphDB Desktop
response = requests.post(import_url, data=csv_rdf, headers=headers, params=params)
# Check if success
if response.status_code == 204:
    print("CSV data imported successfully!")
else:
    print("CSV import failed!")
    print(response.status_code, response.text)
print_benchmarks("Import CSV as RDF", start)

# Export Data from GraphDB Desktop
# URL creation
export_url = f"{GDB_URL}/repositories/{REPO_ID}"
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
    resp = requests.post(export_url, data=query, headers=sparql_headers)
    if resp.status_code == 200:
        filename = title + ".csv"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(resp.text)
        print(f"Exported query '{title}' to '{filename}'")
    else:
        print(f"Query '{title}' failed!", resp.status_code, resp.text)
    print_benchmarks(f"Query: {title}", start)
