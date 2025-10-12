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

from bench.benchmark import bench_report, benchmark
from triplestore import Triplestore

# configuration
config = {
    "name": "bench2025",
}

# implementation


def init():
    global rdf_store
    rdf_store = Triplestore("jena", config=config)


def load(fname):
    rdf_store.load(fname)


def query(query, _):
    results = rdf_store.query(query)
    return results[0] if results else None


def stop_server():
    rdf_store.stop_server()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python jena.py <turtle_file>")
        sys.exit(1)

    try:
        from bench import benchmark
        benchmark.ttlname = sys.argv[1]
        benc_res = benchmark("Apache Jena", init, load, query)
        bench_report("Apache Jena", *benc_res)
    finally:
        stop_server()
