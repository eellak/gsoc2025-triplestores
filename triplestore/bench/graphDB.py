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

from bench.skeleton import bench_report, benchmark
from triplestore import Triplestore

# configuration
config = {
    "name": "bench2025",
}

# implementation


def init():
    global rdf_store
    rdf_store = Triplestore("graphdb", config=config)


def load(fname):
    rdf_store.load(fname)


def query(query, _):
    results = rdf_store.query(query)
    return results[0] if results else None


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
