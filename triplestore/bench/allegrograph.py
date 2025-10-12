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

from bench.benchmark import bench_report, benchmark
from triplestore import Triplestore

# configuration
config = {
    "name": "bench2025",
    "auth": ("testuser", "12345!"),
}

# implementation


def init():
    global rdf_store
    rdf_store = Triplestore("allegrograph", config=config)


def load(fname):
    rdf_store.load(fname)


def query(query_str, _):
    results = rdf_store.query(query_str)
    return results[0] if results else None


if __name__ == "__main__":
    import sys

    import bench.benchmark

    if len(sys.argv) != 2:
        print("Usage: python allegrograph.py <turtle_file>")
        sys.exit(1)

    turtle_file = sys.argv[1]
    bench.benchmark.ttlname = turtle_file

    benc_res = benchmark("AllegroGraph", init, load, query)
    bench_report("AllegroGraph", *benc_res)
