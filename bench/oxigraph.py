#!/usr/bin/env -S uv run --script

# benchmarking oxigraph

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyoxigraph",
# ]
# ///


# Copyright (C) 2025 Alexios Zavras
# SPDX-License-Identifier: Apache-2.0


from pyoxigraph import *

from bench.skeleton import bench_report, benchmark

# implementation


def init():
    global rdf_store
    rdf_store = Store()


def load(fname):
    with open(fname, "rb") as f: 
        rdf_store.bulk_load(f, RdfFormat.TURTLE)
    rdf_store.optimize()


def query(query, base):
    return next(rdf_store.query(query, base_iri=base), None)


if __name__ == "__main__":
    import sys
    import bench.skeleton

    if len(sys.argv) != 2:
        print("Usage: python oxigraph.py <turtle_file>")
        sys.exit(1)

    turtle_file = sys.argv[1]
    bench.skeleton.ttlname = turtle_file

    benc_res = benchmark("Oxigraph", init, load, query)
    bench_report("Oxigraph", *benc_res)