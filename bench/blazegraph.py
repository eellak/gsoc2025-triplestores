#!/usr/bin/env -S uv run --script

# benchmarking Blazegraph

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
# ]
# ///

# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import requests
from bench.skeleton import bench_report, benchmark

# configuration
namespace = "benchmark"
base_url = f"http://localhost:9999/blazegraph/namespace/{namespace}/sparql"
namespace_admin_url = "http://localhost:9999/blazegraph/namespace"

headers_load = {"Content-Type": "text/turtle"}
headers_query = {
    "Content-Type": "application/sparql-query",
    "Accept": "application/sparql-results+json"
}
headers_admin = {"Content-Type": "text/plain"}

# implementation


def init():
    try:
        res = requests.get(namespace_admin_url, timeout=60)
    except requests.RequestException as err:
        msg = f"Could not connect to Blazegraph server: {err}"
        raise RuntimeError(msg) from err

    # Delete existing namespace if present
    if namespace in res.text:
        delete_url = f"{namespace_admin_url}/{namespace}"
        resp = requests.delete(delete_url, timeout=60)
        if resp.status_code != 200:
            msg = f"Failed to delete existing namespace '{namespace}': {resp.status_code}\n{resp.text}"
            raise RuntimeError(msg)

    # Create new namespace
    config = f"""
        com.bigdata.namespace.{namespace}.spo.com.bigdata.btree.BTree.branchingFactor=1024
        com.bigdata.rdf.sail.truthMaintenance=true
        com.bigdata.namespace.{namespace}.lex.com.bigdata.btree.BTree.branchingFactor=400
        com.bigdata.rdf.store.AbstractTripleStore.textIndex=true
        com.bigdata.rdf.store.AbstractTripleStore.fts.index.textPredicates=true
        com.bigdata.namespace.{namespace}.namespace={namespace}
        com.bigdata.rdf.store.AbstractTripleStore.justify=false
        com.bigdata.rdf.sail.isolatableIndices=false
        com.bigdata.rdf.sail.namespace={namespace}
        com.bigdata.rdf.store.AbstractTripleStore.quads=false
        com.bigdata.rdf.store.AbstractTripleStore.axiomsClass=com.bigdata.rdf.axioms.NoAxioms
        com.bigdata.rdf.sail.statementIdentifiers=false
        com.bigdata.rdf.sail.class=com.bigdata.rdf.sail.BigdataSail
        com.bigdata.rdf.store.AbstractTripleStore.geoSpatial=false
        com.bigdata.rdf.sail.reasoning.supported=true
        com.bigdata.rdf.sail.reasoning.rulesets=rdfs
        com.bigdata.rdf.sail.reasoning.owlMaxIterationCount=0
    """

    response = requests.post(
        namespace_admin_url,
        headers=headers_admin,
        data=config.strip(),
        timeout=60
    )

    if response.status_code != 201:
        msg = f"Failed to create namespace '{namespace}': {response.status_code}\n{response.text}"
        raise RuntimeError(msg)


def load(fname):
    rdf_data = Path(fname).read_bytes()

    resp = requests.post(base_url, headers=headers_load, data=rdf_data, timeout=60)
    if resp.status_code not in {200, 204}:
        msg = f"Import failed with status {resp.status_code}:\n{resp.text}"
        raise RuntimeError(msg)


def query(query, base):
    try:
        resp = requests.post(base_url, headers=headers_query, data=query, timeout=60)
    except (requests.RequestException, ValueError):
        return None

    if resp.status_code != 200:
        return None

    try:
        data = resp.json()
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
    import sys

    import bench.skeleton

    if len(sys.argv) != 2:
        print("Usage: python blazegraph.py <turtle_file>")
        sys.exit(1)

    turtle_file = sys.argv[1]
    bench.skeleton.ttlname = turtle_file

    benc_res = benchmark("Blazegraph", init, load, query)
    bench_report("Blazegraph", *benc_res)
