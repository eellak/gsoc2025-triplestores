#!/usr/bin/env python3

# Benchmarking KùzuDB

# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

import shutil
from pathlib import Path

import kuzu
from bench.skeleton import bench_report, benchmark
from rdflib import Graph

# implementation


def init():
    global conn
    db_path = "kuzudb_bench_db"
    # remove existing database
    if Path(db_path).exists():
        shutil.rmtree(db_path)
    db = kuzu.Database(db_path)
    conn = kuzu.Connection(db)


def load(fname):
    # Convert TTL to CSV
    g = Graph()
    g.parse(fname, format="turtle")
    csv_file = "data.csv"
    with Path(csv_file).open("w", encoding="utf-8") as f:
        f.write("id,subject,predicate,object\n")
        for idx, (s, p, o) in enumerate(g, start=1):
            f.write(f'{idx},"{s}","{p}","{o}"\n')

    # Create table and import CSV
    conn.execute("""
        CREATE NODE TABLE Triple(
            id INT64,
            subject STRING,
            predicate STRING,
            object STRING,
            PRIMARY KEY(id)
        );
    """)
    conn.execute(f"COPY Triple FROM '{csv_file}' (HEADER=TRUE);")


def query(query, base):
    result = conn.execute(query)
    if result.has_next():
        return result.get_next()
    return None


if __name__ == "__main__":
    import sys
    
    import bench.skeleton

    if len(sys.argv) != 2:
        print("Usage: python kuzudb.py <turtle_file>")
        sys.exit(1)

    ttl_file = sys.argv[1]
    bench.skeleton.ttlname = ttl_file

    res = benchmark("KùzuDB", init, load, query)
    bench_report("KùzuDB", *res)
