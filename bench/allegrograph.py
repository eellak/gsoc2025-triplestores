#!/usr/bin/env -S uv run --script

# benchmarking allegrograph

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
# ]
# ///


# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

import getpass
import subprocess
from pathlib import Path

import requests
from bench.skeleton import bench_report, benchmark

# configuration
ENDPOINT = "http://localhost:10035/repositories/benchmark"
REPOSITORY_ID = "benchmark"
USERNAME = input("Enter AllegroGraph username: ")
PASSWORD = getpass.getpass("Enter AllegroGraph password: ")
HEADERS = {"Accept": "application/sparql-results+json"}

# implementation


def init():
    try:
        subprocess.run(["bash", "./bench/allegrograph_init.sh"], check=True)
    except subprocess.CalledProcessError as err:
        msg = f"Failed to create repo: {err}"
        raise RuntimeError(msg) from err


def load(fname):
    rdf_data = Path(fname).read_bytes()

    response = requests.post(f"{ENDPOINT}/statements", headers={"Content-Type": "text/turtle"}, data=rdf_data, auth=(USERNAME, PASSWORD), timeout=60)
    if response.status_code >= 400:
        msg = f"Import failed with status {response.status_code}:\n{response.text}"
        raise RuntimeError(msg)


def query(query_str, _):
    try:
        response = requests.post(ENDPOINT, headers=HEADERS, data={"query": query_str}, auth=(USERNAME, PASSWORD), timeout=60)
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    try:
        data = response.json()
        bindings = data.get("results", {}).get("bindings", [])
        if not bindings:
            return None

        row = bindings[0]
        return {k: v["value"] for k, v in row.items()}
    except (requests.RequestException, ValueError):
        return None


if __name__ == "__main__":
    import sys

    import bench.skeleton

    if len(sys.argv) != 2:
        print("Usage: python allegrograph.py <turtle_file>")
        sys.exit(1)

    turtle_file = sys.argv[1]
    bench.skeleton.ttlname = turtle_file

    benc_res = benchmark("AllegroGraph", init, load, query)
    bench_report("AllegroGraph", *benc_res)
