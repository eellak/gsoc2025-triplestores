import kuzu
import shutil
from rdflib import Graph
# For benchmarks
import time
import psutil

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

# Delete any existing database folder
shutil.rmtree("kuzu_demo_db", ignore_errors=True)
# Create a new database and open a connection
db = kuzu.Database("kuzu_demo_db")
conn = kuzu.Connection(db)

# Create node table for Area
conn.execute(f"""
    CREATE NODE TABLE Area(
        domain STRING,
        quads INT64,
        entities INT64,
        density STRING,
        PRIMARY KEY(domain)
    );
""")

# Start Time Counter
start = time.perf_counter()
conn.execute("COPY Area FROM 'Cleaned_AdministrativeArea_domain_stats.csv' (HEADER=TRUE);")
print_benchmarks("Import CSV", start)

# Create Relationship table for Area
conn.execute("CREATE REL TABLE RELATED_TO(FROM Area TO Area, strength DOUBLE);")
# Select a few areas to create relationships
result = conn.execute("MATCH (a:Area) RETURN a.domain LIMIT 5;")
areas = []
while result.has_next():
    row = result.get_next()
    areas.append(row[0])

# Start Time Counter  
start = time.perf_counter()
for i in range(len(areas) - 1):
    domain1 = areas[i].replace("'", "''")
    domain2 = areas[i + 1].replace("'", "''")
    strength = round(1.0 - i * 0.2, 2)

    conn.execute(f"""
        MATCH (a:Area), (b:Area)
        WHERE a.domain = '{domain1}' AND b.domain = '{domain2}'
        CREATE (a)-[:RELATED_TO {{strength: {strength}}}]->(b);
    """)
print_benchmarks("Import REL CSV", start)

# Check the created relationships
response = conn.execute("""
    MATCH (a:Area)-[r:RELATED_TO]->(b:Area)
    RETURN a.domain, b.domain, r.strength;
""")
print("\nRelationships between areas:")
while response.has_next():
    print(response.get_next())

# Convert a Turtle (TTL) file to CSV using rdflib
g = Graph()
g.parse("example.ttl", format="turtle")
with open("example_triples.csv", "w", encoding="utf-8") as f:
    f.write("id,subject,predicate,object\n")
    for idx, (subj, pred, obj) in enumerate(g, start=1):
        f.write(f'{idx},"{subj}","{pred}","{obj}"\n')

# Create node table Triple for example
conn.execute("""
    CREATE NODE TABLE Triple(
        id INT64,
        subject STRING,
        predicate STRING,
        object STRING,
        PRIMARY KEY(id)
    );
""")

start = time.perf_counter()
conn.execute("COPY Triple FROM 'example_triples.csv' (HEADER=TRUE);")
print_benchmarks("Import TTL Triples CSV", start)
# Check the created triples
response = conn.execute("""
    MATCH (t:Triple) RETURN t.subject, t.predicate, t.object LIMIT 5;
""")
print("\nThe triples from the example file:")
while response.has_next():
    print(response.get_next())