# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

import os
import sys

import pytest


def main() -> int:
    files = [
        "triplestore/tests/test_oxigraph.py",
        "triplestore/tests/test_jena.py",
        "triplestore/tests/test_graphdb.py",
        "triplestore/tests/test_blazegraph.py",
    ]

    # AllegroGraph needs creds; its test file prompts at import time.
    # Enable only if the user explicitly opts in and provides env creds.
    if os.getenv("RUN_ALLEGROGRAPH") == "1":
        user = os.getenv("AG_USERNAME")
        pwd = os.getenv("AG_PASSWORD")
        if not (user and pwd):
            print(
                "[Skip] AllegroGraph tests requested but AG_USERNAME/AG_PASSWORD are missing. "
                "Export them and rerun, e.g.: RUN_ALLEGROGRAPH=1 AG_USERNAME=username AG_PASSWORD=password"
            )
        else:
            files.append("triplestore/tests/test_allegrograph.py")

    # Allow passing through extra pytest args, e.g. -q or -k pattern
    extra_args = sys.argv[1:]
    return pytest.main(files + extra_args)


if __name__ == "__main__":
    raise SystemExit(main())
