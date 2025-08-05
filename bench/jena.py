#!/usr/bin/env -S uv run --script

# benchmarking apache jena fuseki

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
# ]
# ///


# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

import subprocess
import time
from pathlib import Path

import requests
from bench.skeleton import bench_report, benchmark

# configuration
base_url = "http://localhost:3030"
dataset = "benchmark_dataset"
load_url = f"{base_url}/{dataset}/data"
query_url = f"{base_url}/{dataset}/query"
admin_url = f"{base_url}/$/datasets"

headers_query = {
    "Accept": "application/sparql-results+json",
}
headers_load = {
    "Content-Type": "text/turtle"
}
headers_admin = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# Optional authentication
AUTH = None  # e.g. ("admin", "password")

# implementation


def init():
    try:
        res = requests.get(admin_url, auth=AUTH, timeout=60)
    except requests.RequestException:
        start_script = Path(__file__).parent / "jena_run.bat"
        if not start_script.exists():
            msg = f"Apache Jena Fuseki start script not found: {start_script}"
            raise RuntimeError(msg)
        subprocess.Popen(f'start "" cmd /c "{start_script}"', shell=True)
        time.sleep(5)

    try:
        res = requests.get(admin_url, auth=AUTH, timeout=10)
    except requests.RequestException as err:
        msg = f"Could not connect to Fuseki admin endpoint: {err}"
        raise RuntimeError(msg) from err

    # Delete existing dataset if present
    existing = [ds["ds.name"].lstrip("/") for ds in res.json().get("datasets", [])]
    if dataset in existing:
        delete_url = f"{admin_url}/{dataset}"
        resp = requests.delete(delete_url, auth=AUTH, timeout=60)
        if resp.status_code != 200:
            msg = f"Failed to delete dataset '{dataset}': {resp.status_code}\n{resp.text}"
            raise RuntimeError(msg)

    # Create new dataset
    response = requests.post(admin_url, headers=headers_admin, data={"dbName": dataset, "dbType": "tdb2"}, auth=AUTH, timeout=60)
    if response.status_code != 200:
        msg = f"Failed to create dataset '{dataset}': {response.status_code}\n{response.text}"
        raise RuntimeError(msg)


def load(fname):
    rdf_data = Path(fname).read_bytes()
    response = requests.post(load_url, headers=headers_load, data=rdf_data, auth=AUTH, timeout=60)
    if response.status_code not in {200, 204}:
        msg = f"Import failed with status {response.status_code}:\n{response.text}"
        raise RuntimeError(msg)


def query(query, base):
    try:
        response = requests.post(query_url, headers=headers_query, data={"query": query}, auth=AUTH, timeout=60)
    except (requests.RequestException, ValueError):
        return None

    if response.status_code != 200:
        return None

    try:
        data = response.json()
        bindings = data.get("results", {}).get("bindings", [])
        if not bindings:
            return None

        row = bindings[0]

        def strip_uri(val):
            return val.split("/")[-1] if val.startswith("http") else val

        return {k: strip_uri(v["value"]) for k, v in row.items()}
    except (requests.RequestException, ValueError):
        return None


if __name__ == "__main__":
    import platform
    import subprocess
    import sys
    from pathlib import Path

    if len(sys.argv) != 2:
        print("Usage: python jena.py <turtle_file>")
        sys.exit(1)

    if platform.system() != "Windows":
        print("This script is configured for Windows only.")
        sys.exit(1)

    start_script = Path(__file__).parent / "jena_run.bat"

    if not start_script.exists():
        print(f"Fuseki start script not found: {start_script}")
        sys.exit(1)

    server_proc = subprocess.Popen(f'start "" cmd /c "{start_script}"', shell=True)

    try:
        from bench import skeleton
        skeleton.ttlname = sys.argv[1]
        benc_res = benchmark("Apache Jena Fuseki", init, load, query)
        bench_report("Apache Jena Fuseki", *benc_res)
    finally:
        server_proc.terminate()
