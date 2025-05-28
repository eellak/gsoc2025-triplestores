# Exploring triplestores

## GraphDB Demo

### Overview
This demo showcases how to use GraphDB for:
- Importing RDF and CSV data using HTTP POST requests to tthe GraphDB /statements endpoint
- Running SPARQL queries over the imported data
- Testing reasoning capabilities and comparing results between reasoning-enabled and non-reasoning repositories
- Benchmarking system performance using Execution Time, CPU Usage and Memory as metrics

### Requirements
- Python 3.x
- GraphDB 11.0 (Desktop version)

### Setup
1. Download GraphDB Desktop: https://graphdb.ontotext.com/
2. Set license: "Setup" → "License" → "Set new license", paste the license key received via email and click Register.
3. Create repository: "Setup" → "Repositories" → "Create new repository"

### Running the Demo
To run the demo script:
```shell
python graphdb_demo.py
```

## KuzuDB Demo

### Overview
This demo showcases how to use KuzuDB for:
- Creating a new graph database and schema, node and relationship tables
- Importing structured data from a CSV file into node table
- Converting RDF Turtle data  into CSV format using `rdflib` and importing it as triples into table
- Running Cypher queries over the imported data
- Benchmarking system performance using Execution Time, CPU Usage, and Memory as metrics

### Requirements
- Python 3.x
- kuzu 
- rdflib 

### Setup
1. Install the required Python packages:
```shell
pip install kuzu rdflib 
```

### Running the Demo
To run the demo script:
```shell
python KuzuDBdemo.py
```

### Visualizing the Graph with Docker
To visually explore the imported data, you can use the Kuzu Explorer:
```shell
docker run -p 8000:8000 \
    -v /path/to/kuzu_demo_db:/database \
    --rm kuzudb/explorer:latest
```
Replace /path/to/kuzu_demo_db with the absolute path to your database folder 
Open your web browser and navigate to:
```shell
http://localhost:8000
```
## Apache Jena Fuseki Demo

### Overview
This demo showcases how to use Apache Jena Fuseki for:
- Importing RDF triples from a Turtle file (example.ttl)
- Converting structured data from a CSV file (Cleaned_AdministrativeArea_domain_stats.csv) into RDF triples in Turtle format
- Uploading the converted triples to a dataset (my-new-dataset) in Fuseki
- Running SPARQL queries over the imported data
- Benchmarking system performance using Execution Time, CPU Usage, and Memory as metrics

### Requirements
- Python 3.x
- Java (version 8 or later)
- Apache Jena Fuseki 5.4.0

### Setup
1. Install Java (required by Fuseki):  
   [https://adoptium.net](https://adoptium.net)
2. Download and extract the Fuseki server:  
   [https://jena.apache.org/download/](https://jena.apache.org/download/)  
3. Start the Fuseki server:  
   ```shell
   ./fuseki-server
4. Access the Fuseki web UI at:
http://localhost:3030/

### Running the Demo
To run the demo script:
```shell
python apachejena_fuseki_demo.py
```

### Using the Fuseki Web UI
The Fuseki web UI allows you to:
- Manage datasets
- Upload RDF data (Turtle, RDF/XML, etc.)
- Execute SPARQL queries interactively