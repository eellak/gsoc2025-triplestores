from __future__ import annotations

# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0
import logging
import platform
import subprocess

logger = logging.getLogger(__name__)


def detect_host_url(port: int, path: str = "", fallback: str | None = None) -> str:
    """
    Detect the Windows host IP from within WSL and return the base URL to use for HTTP services.
    Falls back to localhost if detection fails.
    """
    try:
        if "microsoft" in platform.uname().release.lower():
            route = subprocess.check_output(["ip", "route"]).decode()
            for line in route.splitlines():
                if line.startswith("default via"):
                    ip = line.split()[2]
                    return f"http://{ip}:{port}{path}"
    except subprocess.SubprocessError as e:
        msg = f"Auto-detection of host IP failed: {e}"
        logger.warning(msg)

    return fallback or f"http://localhost:{port}{path}"


def detect_graphdb_url() -> str:
    return detect_host_url(7200)


# def detect_blazegraph_url() -> str:
#     return detect_host_url(9999, "/blazegraph")


def init_allegrograph_repo(repo_name: str):
    try:
        subprocess.run(["bash", "./bench/init_allegrograph_repo.sh", repo_name], check=True)
    except subprocess.CalledProcessError as e:
        msg = f"Failed to initialize AllegroGraph repo '{repo_name}'"
        raise RuntimeError(msg) from e
