#!/usr/bin/env -S uv run --script

# benchmarking oxigraph

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyoxigraph",
# ]
# ///


# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0


from bench.benchmark import bench_report, benchmark
from triplestore import Triplestore

# implementation


def init():
    global rdf_store
    rdf_store = Triplestore("oxigraph", config={})


def load(fname):
    rdf_store.load(fname)


def query(query, _):
    results = rdf_store.query(query)
    return results[0] if results else None


if __name__ == "__main__":
    import sys

    import bench.benchmark

    if len(sys.argv) != 2:
        print("Usage: python oxigraph.py <turtle_file>")
        sys.exit(1)

    turtle_file = sys.argv[1]
    bench.benchmark.ttlname = turtle_file

    benc_res = benchmark("Oxigraph", init, load, query)
    bench_report("Oxigraph", *benc_res)
