#!/usr/bin/env -S uv run --script

# benchmark script for MillenniumDB

# /// script
# requires-python = ">=3.12"
# ///

# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

import csv
import io
import shutil
import subprocess
import tempfile
from pathlib import Path
from time import sleep

from bench import skeleton
from bench.skeleton import bench_report, benchmark

# Configuration
MDB_HOME = Path.home() / "projects" / "MillenniumDB"
MDB_BIN = MDB_HOME / "build" / "Release" / "bin"
MDB_IMPORT = MDB_BIN / "mdb-import"
MDB_SERVER = MDB_BIN / "mdb-server"
DB_DIR = MDB_HOME / "mdb_benchmark_db"
PREFIX = "http://rdf.zvr.invalid/demofamilydata/"
MDB_URL = "http://localhost:4321/"

server_process = None


# implementation
def build_millenniumdb():
    subprocess.run(["cmake", "-Bbuild/Release", "-DCMAKE_BUILD_TYPE=Release"], cwd=MDB_HOME, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["cmake", "--build", "build/Release", "-j", "4"], cwd=MDB_HOME, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def init():
    global server_process
    subprocess.run(["pkill", "-f", "mdb-server"], check=False, capture_output=True)

    if DB_DIR.exists():
        shutil.rmtree(DB_DIR)


def load(_):
    data_file = Path(skeleton.ttlname).resolve()
    subprocess.run([str(MDB_IMPORT), str(data_file), str(DB_DIR)], check=True, cwd=MDB_HOME, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    global server_process
    server_process = subprocess.Popen([str(MDB_SERVER), str(DB_DIR)], cwd=MDB_HOME, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    sleep(1)


def query(query, base):
    # Save query to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sparql", delete=False) as qfile:
        qfile.write(query)
        query_path = qfile.name

    # Run MillenniumDB query script
    result = subprocess.run([str(MDB_HOME / "scripts/query"), query_path], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=MDB_HOME)

    Path(query_path).unlink(missing_ok=True)

    if result.returncode != 0:
        msg = f"MillenniumDB query failed:\n{result.stderr.decode()}"
        raise RuntimeError(msg)

    # Parse CSV output
    try:
        csv_text = result.stdout.decode()
        reader = csv.DictReader(io.StringIO(csv_text))
        first_row = next(reader, None)
        if not first_row:
            return None

        def strip_uri(val):
            return val.split("/")[-1] if val and val.startswith("http") else val

        return {k: strip_uri(v) for k, v in first_row.items()}
    except (UnicodeDecodeError, csv.Error) as e:
        msg = f"Failed to parse MillenniumDB CSV output:\n{e}"
        raise RuntimeError(msg)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python milleniumDB.py <turtle_file>")
        sys.exit(1)

    skeleton.ttlname = str(Path(sys.argv[1]).resolve())

    build_millenniumdb()

    try:
        res = benchmark("MillenniumDB", init, load, query)
        bench_report("MillenniumDB", *res)
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()
