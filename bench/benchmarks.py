# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

import argparse
import importlib
import platform
import sys
from pathlib import Path

from bench import skeleton

TriplestoreSpec = tuple[str, str]

TRIPLESTORES: dict[str, TriplestoreSpec] = {
    "jena": ("bench.jena", "Apache Jena"),
    "graphdb": ("bench.graphDB", "GraphDB"),
    "blazegraph": ("bench.blazegraph", "Blazegraph"),
    "oxigraph": ("bench.oxigraph", "Oxigraph"),
    "allegrograph": ("bench.allegrograph", "AllegroGraph"),
    "milleniumdb": ("bench.milleniumDB", "MilleniumDB")
}


def run_benchmark(store_key: str) -> None:
    module_name, label = TRIPLESTORES[store_key]

    if platform.system() == "Windows":
        if label.lower() == "allegrograph":
            msg = (
                f"\nBenchmarking {label}\n"
                f"{label} is not supported on native Windows systems. "
                "Run it via WSL or in a Linux environment.\n"
                "Start the server with:\n"
                "    ./bin/agraph-control --config ./lib/agraph.cfg start"
            )
            print(msg)
            return

        if label.lower() == "milleniumdb":
            msg = (
                f"\nBenchmarking {label}\n"
                f"{label} is not supported on native Windows systems. "
                "Run it via WSL or in a Linux environment."
            )
            print(msg)
            return

    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        msg = f"Could not import module '{module_name}': {e}"
        raise RuntimeError(msg) from e

    try:
        init = module.init
        load = module.load
        query = module.query
    except AttributeError as e:
        msg = f"Missing required function in module '{module_name}': {e}"
        raise RuntimeError(msg) from e

    try:
        time_all, time_load, time_query, res = skeleton.benchmark(label, init, load, query)
        skeleton.bench_report(label, time_all, time_load, time_query, res)
    except RuntimeError as e:
        msg = f"Benchmark failed for '{label}': {e}"
        raise RuntimeError(msg) from e


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Run benchmarks for various RDF triplestores using a Turtle (.ttl) file.\n\n"
            "Usage examples:\n"
            "  python -m bench.benchmarks data.ttl            # run all benchmarks\n"
            "  python -m bench.benchmarks data.ttl jena       # run only Jena\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "ttl_file",
        help="Path to the Turtle (.ttl) data file (e.g., data.ttl)"
    )
    parser.add_argument(
        "triplestore",
        nargs="?",
        choices=TRIPLESTORES.keys(),
        help=f"Optional triplestore to benchmark. One of: {', '.join(TRIPLESTORES)}"
    )

    args = parser.parse_args()

    try:
        ttl_path = Path(args.ttl_file)
        if not ttl_path.is_file():
            msg = f"Turtle file not found: '{ttl_path}'"
            raise FileNotFoundError(msg)

        skeleton.ttlname = args.ttl_file

        if args.triplestore:
            run_benchmark(args.triplestore)
        else:
            for store_key in TRIPLESTORES:
                run_benchmark(store_key)

    except Exception as e:
        print(f"{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
