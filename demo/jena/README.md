# Apache Jena Fuseki Demo

## Overview
This demo showcases how to use Apache Jena Fuseki for:
- Importing RDF triples from a Turtle file (example.ttl)
- Converting structured data from a CSV file (Cleaned_AdministrativeArea_domain_stats.csv) into RDF triples in Turtle format
- Uploading the converted triples to a dataset (my-new-dataset) in Fuseki
- Running SPARQL queries over the imported data
- Benchmarking system performance using Execution Time, CPU Usage, and Memory as metrics

## Requirements
- Python 3.x
- Java (version 8 or later)
- Apache Jena Fuseki 5.4.0

## Setup
1. Install Java (required by Fuseki):  
   [https://adoptium.net](https://adoptium.net)
2. Download and extract the Fuseki server:  
   [https://jena.apache.org/download/](https://jena.apache.org/download/)  
3. Start the Fuseki server:  
   ```shell
   ./fuseki-server
4. Access the Fuseki web UI at:
http://localhost:3030/

## Running the Demo
To run the demo script:
```shell
python apachejena_fuseki_demo.py
```

## Using the Fuseki Web UI
The Fuseki web UI allows you to:
- Manage datasets
- Upload RDF data (Turtle, RDF/XML, etc.)
- Execute SPARQL queries interactively
