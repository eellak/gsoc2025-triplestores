# GraphDB Demo

## Overview
This demo showcases how to use GraphDB for:
- Importing RDF and CSV data using HTTP POST requests to tthe GraphDB /statements endpoint
- Running SPARQL queries over the imported data
- Testing reasoning capabilities and comparing results between reasoning-enabled and non-reasoning repositories
- Benchmarking system performance using Execution Time, CPU Usage and Memory as metrics

## Requirements
- Python 3.x
- GraphDB 11.0 (Desktop version)

## Setup
1. Download GraphDB Desktop: https://graphdb.ontotext.com/
2. Set license: "Setup" → "License" → "Set new license", paste the license key received via email and click Register.
3. Create repository: "Setup" → "Repositories" → "Create new repository"

## Running the Demo
To run the demo script:
```shell
python graphdb_demo.py
```
