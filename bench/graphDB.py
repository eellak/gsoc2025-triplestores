#!/usr/bin/env -S uv run --script

# benchmarking graphdb

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
from bench.graphDB_run import graphdb_run
from bench.skeleton import bench_report, benchmark

# configuration

GDB_URL = "http://localhost:7200"
REPO_ID = "repo"
BASE_IRI = "http://rdf.zvr.invalid/demofamilydata/"
GRAPH_IRI = ""

load_url = f"{GDB_URL}/repositories/{REPO_ID}/statements"
query_url = f"{GDB_URL}/repositories/{REPO_ID}"

headers_load = {
    "Content-Type": "text/turtle"
}

headers_query = {
    "Content-Type": "application/sparql-query",
    "Accept": "application/sparql-results+json"
}

# implementation


def init():

    graphdb_run()

    # Delete repository if it already exists
    delete_url = f"{GDB_URL}/repositories/{REPO_ID}"
    requests.delete(delete_url, timeout=60)

    # Create new repository
    create_url = f"{GDB_URL}/rest/repositories"

    body = f"""#
        # name: {REPO_ID}
        # location:
        #
        prefix st: <http://www.openrdf.org/config/repository#>
        prefix sr: <http://www.openrdf.org/config/repository/sail#>
        prefix sail: <http://www.openrdf.org/config/sail#>
        prefix xsd: <http://www.w3.org/2001/XMLSchema#>
        prefix graphdb: <http://www.ontotext.com/config/graphdb#>

        [] a st:Repository ;
        st:repositoryID "{REPO_ID}" ;
        st:repositoryImpl [
            st:repositoryType "graphdb:SailRepository" ;
            sr:sailImpl [
                sail:sailType "graphdb:Sail" ;
                graphdb:ruleset "rdfsplus-optimized" ;
                graphdb:enable-context-index true ;
                graphdb:enablePredicateList true ;
                graphdb:in-memory-literal-properties false ;
                graphdb:enable-literal-index true ;
                graphdb:enable-geo-spatial false ;
                graphdb:enable-full-text-search false ;
                graphdb:fts-index-policy "ALL" ;
                graphdb:strict-parsing true ;
                graphdb:enable-query-logging false
            ]
        ] .
        """

    files = {
        "config": ("repo-config.ttl", body, "application/x-turtle")
    }

    resp = requests.post(create_url, files=files, timeout=60)
    if resp.status_code not in {200, 201}:
        msg = f"Failed to create repo '{REPO_ID}': {resp.status_code} {resp.text}"
        raise RuntimeError(msg)


def load(fname):
    rdf_data = Path(fname).read_bytes()

    params = {}
    if GRAPH_IRI:
        params["context"] = f"<{GRAPH_IRI}>"

    resp = requests.post(load_url, data=rdf_data, headers=headers_load, params=params, timeout=60)
    if resp.status_code not in {200, 204}:
        msg = f"Import failed with status {resp.status_code}:\n{resp.text}"
        raise RuntimeError(msg)


def query(query, base):
    resp = requests.post(query_url, data=query, headers=headers_query, timeout=60)

    if resp.status_code != 200:
        return None

    data = resp.json()
    bindings = data.get("results", {}).get("bindings", [])
    if not bindings:
        return None

    row = bindings[0]

    def strip_uri(val):
        return val.split("/")[-1] if val.startswith("http") else val

    return {k: strip_uri(v["value"]) for k, v in row.items()}


if __name__ == "__main__":
    import sys

    import bench.skeleton

    if len(sys.argv) != 2:
        print("Usage: python graphDB.py <turtle_file>")
        sys.exit(1)

    turtle_file = sys.argv[1]
    bench.skeleton.ttlname = turtle_file

    benc_res = benchmark("GraphDB", init, load, query)
    bench_report("GraphDB", *benc_res)
