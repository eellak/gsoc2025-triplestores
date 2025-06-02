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

from .skeleton import bench_report, benchmark

# implementation


def init():
    global rdf_store
    rdf_store = Store()


def load(fname):
    rdf_store.bulk_load(fname, "text/turtle")
    rdf_store.optimize()


def query(query, base):
    return next(rdf_store.query(query, base_iri=base))


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python oxigraph.py <turtle_file>")
        sys.exit(1)

    turtle_file = sys.argv[1]

    benc_res = benchmark("Oxigraph", init, load, query)
    bench_report("Oxigraph", *benc_res)
