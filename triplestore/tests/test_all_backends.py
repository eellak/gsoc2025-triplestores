# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

import sys

import pytest


def main() -> int:
    files = [
        "triplestore/tests/test_oxigraph.py",
        "triplestore/tests/test_jena.py",
        "triplestore/tests/test_graphdb.py",
        "triplestore/tests/test_blazegraph.py",
        "triplestore/tests/test_allegrograph.py",
    ]

    # Allow passing through extra pytest args, e.g. -q or -k pattern
    extra_args = sys.argv[1:]
    return pytest.main(files + extra_args)


if __name__ == "__main__":
    raise SystemExit(main())
