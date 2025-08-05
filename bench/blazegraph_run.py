# Blazegraph auto-run support

# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0


import atexit
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

BLAZEGRAPH_URL = "http://localhost:9999/blazegraph"
ENV_VAR = "BLAZEGRAPH_JAR"

_blazegraph_process = None

logger = logging.getLogger(__name__)


def blazegraph_run():
    global _blazegraph_process

    try:
        if requests.get(f"{BLAZEGRAPH_URL}/namespace", timeout=2).ok:
            return
    except requests.RequestException:
        pass

    jar_path = os.environ.get(ENV_VAR)
    if not jar_path:
        msg = f"Environment variable '{ENV_VAR}' is not set.\nPlease set it to the full path of blazegraph.jar."
        raise RuntimeError(msg)

    jar_file = Path(jar_path)
    if not jar_file.exists():
        msg = f"The file specified in '{ENV_VAR}' does not exist:\n{jar_file}"
        raise RuntimeError(msg)

    creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0

    _blazegraph_process = subprocess.Popen(
        ["java", "-server", "-Xmx4g", "-jar", str(jar_file)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creation_flags)

    for _ in range(120):
        try:
            if requests.get(f"{BLAZEGRAPH_URL}/namespace", timeout=1).ok:
                return
        except requests.RequestException:
            time.sleep(1)

    msg = "Blazegraph did not start within 2 minutes."
    raise RuntimeError(msg)


def blazegraph_terminate():
    try:
        out = subprocess.check_output(
            'wmic process where "name=\'java.exe\' and CommandLine like \'%blazegraph.jar%\'" get ProcessId',
            shell=True,
            text=True
        )
        pids = [line.strip() for line in out.splitlines() if line.strip().isdigit()]
        for pid in pids:
            subprocess.run(["taskkill", "/PID", pid, "/F"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.exception("Failed to kill blazegraph")


atexit.register(blazegraph_terminate)
