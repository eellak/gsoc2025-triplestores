# KuzuDB Demo

## Overview
This demo showcases how to use KuzuDB for:
- Creating a new graph database and schema, node and relationship tables
- Importing structured data from a CSV file into node table
- Converting RDF Turtle data  into CSV format using `rdflib` and importing it as triples into table
- Running Cypher queries over the imported data
- Benchmarking system performance using Execution Time, CPU Usage, and Memory as metrics

## Requirements
- Python 3.x
- kuzu 
- rdflib 

## Setup
1. Install the required Python packages:
```shell
pip install kuzu rdflib 
```

## Running the Demo
To run the demo script:
```shell
python KuzuDBdemo.py
```

## Visualizing the Graph with Docker
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

