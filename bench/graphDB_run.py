# GraphDB auto-run support

# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess
import time
from pathlib import Path

import requests

GDB_URL = "http://localhost:7200"


def graphdb_run():
    try:
        response = requests.get(f"{GDB_URL}/rest/repositories", timeout=2)
        if response.ok:
            return
    except requests.RequestException:
        pass

    candidates = [
        Path(os.environ["USERPROFILE"])
        / "AppData"
        / "Roaming"
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Unknown"
        / "GraphDB Desktop.lnk",
        Path("C:/Program Files/GraphDB/GraphDB.exe"),
        Path("C:/Program Files (x86)/GraphDB/GraphDB.exe")
    ]

    for path in candidates:
        if path.exists():
            if path.suffix == ".lnk":
                subprocess.Popen(["powershell", "-Command", f'Start-Process "{path}"'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen([str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            break
    else:
        msg = "GraphDB Desktop not found. You have to download GraphDB first from https://graphdb.ontotext.com/"
        raise RuntimeError(msg)

    for _ in range(120):
        try:
            if requests.get(f"{GDB_URL}/rest/repositories", timeout=1).ok:
                return
        except requests.RequestException:
            time.sleep(1)

    msg = "GraphDB did not start within 2 minutes."
    raise RuntimeError(msg)
