# Blazegraph Demo

## Overview
This demo showcases how to use Blazegraph for:
- Importing RDF data from a Turtle file (example.ttl)
- Converting structured data from a CSV file (Cleaned_AdministrativeArea_domain_stats.csv) into RDF triples (in Turtle format)
- Uploading the converted triples to a namespace in Blazegraph
- Running SPARQL queries over the imported data 
- Benchmarking system performance using Execution Time, CPU Usage, and Memory as metrics

## Requirements
- Python 3.x
- Java (version 8 or later)
- Blazegraph (usually blazegraph.jar)

## Setup
- Download the Blazegraph standalone jar file: https://github.com/blazegraph/database/releases
- Start the Blazegraph server by running:
```shell
java -server -Xmx4g -jar blazegraph.jar
```
- Open your browser and navigate to:
```shell
http://localhost:9999/blazegraph
```
- In the Blazegraph web UI:
  - Go to "Namespaces" → "New namespace"
  - Create a new namespace (e.g., demo)

## Running the Demo
To run the demo script:
```shell
python blazegraph_demo.py
```

