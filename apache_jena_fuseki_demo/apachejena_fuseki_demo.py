# For HTTP POST
import requests
# For benchmarks
import time
import psutil
import pandas as pd

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


# Fuseki server configuration
fuseki_import_url = "http://localhost:3030/my-new-dataset/data"
fuseki_query_url = "http://localhost:3030/my-new-dataset/query"

# Load a sample RDF dataset in Turtle format and import to Fuseki
ttl_file_path = "example.ttl"
with open(ttl_file_path, "rb") as f:
    ttl_data = f.read()
# Start Time Counter
start = time.perf_counter()
# POST the file to Fuseki
response = requests.post(
    fuseki_import_url,
    data=ttl_data,
    headers={"Content-Type": "text/turtle"}
)
if response.status_code not in [200, 201, 204]:
    print(f"Error: {response.status_code}\n{response.text}")
print_benchmarks("Import RDF", start)

# Perform a SPARQL SELECT query to verify the imported RDF data
sparql_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?s ?p ?o WHERE {
  ?s ?p ?o
} LIMIT 5
"""
# Start Time Counter
start = time.perf_counter()
query_response = requests.post(
    fuseki_query_url,
    data={"query": sparql_query},
    headers={
        "Accept": "application/sparql-results+json"
    }
)
print_benchmarks("Export RDF", start)
if query_response.status_code == 200:
    results = query_response.json()
    print("Found imported data:")
    for binding in results["results"]["bindings"]:
        s = binding["s"]["value"]
        p = binding["p"]["value"]
        o = binding["o"]["value"]
        print(f"  {s} -- {p} --> {o}")
else:
    print(f"Error in query ({query_response.status_code}): {query_response.text}")


# Convert CSV file to TTL file because Apache Jena Fuseki accepts only RDF files
csv_file = "Cleaned_AdministrativeArea_domain_stats.csv"
df = pd.read_csv(csv_file)
# Clean column names: remove invalid characters and replace spaces with underscores
df.columns = df.columns.str.replace(r"[#]", "", regex=True)
df.columns = df.columns.str.replace(" ", "_")
# Prefixes
ttl_lines = [
    "@prefix ex: <http://example.org/> .",
    "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
    "",
]
# Convert every line
for idx, row in df.iterrows():
    subject_uri = f"ex:row{idx+1}"

    for col, value in row.items():
        if pd.isna(value):
            continue

        col_clean = col
        value_clean = str(value).replace('"', '\\"')

        if isinstance(value, (int, float)):
            ttl_lines.append(f"{subject_uri} ex:{col_clean} {value_clean} .")
        else:
            ttl_lines.append(f'{subject_uri} ex:{col_clean} "{value_clean}" .')

    ttl_lines.append("")

ttl_output = "converted_data.ttl"
with open(ttl_output, "w", encoding="utf-8") as f:
    f.write("\n".join(ttl_lines))
# Import the generated Turtle data to Fuseki
ttl_file_path = "converted_data.ttl"
with open(ttl_file_path, "rb") as f:
    ttl_data = f.read()
# Start Time Counter
start = time.perf_counter()
# POST the file to Fuseki
response = requests.post(
    fuseki_import_url,
    data=ttl_data,
    headers={"Content-Type": "text/turtle"}
)
if response.status_code not in [200, 201, 204]:
    print(f"Error: {response.status_code}\n{response.text}")
print_benchmarks("Import RDF", start)

# Perform a SPARQL SELECT query to verify the new RDF triples
sparql_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?s ?p ?o WHERE {
  ?s ?p ?o
} LIMIT 5
"""
# Start Time Counter
start = time.perf_counter()
query_response = requests.post(
    fuseki_query_url,
    data={"query": sparql_query},
    headers={
        "Accept": "application/sparql-results+json"
    }
)
print_benchmarks("Export RDF", start)
if query_response.status_code == 200:
    results = query_response.json()
    print("Found imported data:")
    for binding in results["results"]["bindings"]:
        s = binding["s"]["value"]
        p = binding["p"]["value"]
        o = binding["o"]["value"]
        print(f"  {s} -- {p} --> {o}")
else:
    print(f"Error in query ({query_response.status_code}): {query_response.text}")