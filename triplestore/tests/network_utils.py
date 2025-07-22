# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

import logging
import platform
import subprocess

logger = logging.getLogger(__name__)


def detect_graphdb_url(default: str = "http://localhost:7200") -> str:
    try:
        if "microsoft" in platform.uname().release.lower():
            route = subprocess.check_output(["ip", "route"]).decode()
            for line in route.splitlines():
                if line.startswith("default via"):
                    ip = line.split()[2]
                    return f"http://{ip}:7200"
    except subprocess.SubprocessError as e:
        msg = f"GraphDB auto-detection failed: {e}"
        logger.warning(msg)
    return default
