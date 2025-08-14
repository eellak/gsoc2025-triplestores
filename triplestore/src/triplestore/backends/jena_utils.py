# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from textwrap import dedent

import psutil
import requests


def sanitize_fuseki_dataset_name(name: str) -> str:
    """
    Convert a dataset name into a Fuseki path-safe service name:
    keep [A-Za-z0-9_-], collapse everything else to '-'.
    """
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", name.strip())
    return cleaned.strip("-") or "ds"


def create_tdb2_location() -> Path:
    """
    Compute the TDB2 directory for the current user.

    Rules:
    - If FUSEKI_BASE is set -> use sibling folder 'DB2', i.e., dirname(FUSEKI_BASE)/DB2
    - Otherwise -> fallback to ~/fuseki/DB2
    The directory is created if missing.
    """
    fb = os.environ.get("FUSEKI_BASE")
    if fb:
        base = Path(fb).expanduser().resolve()
        tdb2 = base.parent / "DB2"
    else:
        tdb2 = Path.home() / "fuseki" / "DB2"
    tdb2.mkdir(parents=True, exist_ok=True)
    return tdb2


def create_config_path() -> Path:
    """
    Decide where to write config.ttl:

    - If FUSEKI_BASE is set -> inside it (FUSEKI_BASE/config.ttl)
    - Else -> ~/fuseki/base/config.ttl

    The directory is created if missing.
    """
    fb = os.environ.get("FUSEKI_BASE")
    if fb:
        base = Path(fb).expanduser().resolve()
    else:
        base = Path.home() / "fuseki" / "base"
    base.mkdir(parents=True, exist_ok=True)
    return base / "config.ttl"


def find_fuseki_server() -> str:
    """
    Locate the 'fuseki-server' executable.

    Search order:
    1) $FUSEKI_HOME/fuseki-server  (if FUSEKI_HOME is set)
    2) PATH lookup via shutil.which('fuseki-server')

    Raises:
        FileNotFoundError if not found.
    """
    fh = os.environ.get("FUSEKI_HOME")
    if fh:
        cand = str(Path(fh).expanduser().resolve() / "fuseki-server")
        if Path(cand).exists():
            return cand

    exe = shutil.which("fuseki-server")
    if exe:
        return exe

    msg = (
        "\n[APACHE JENA] "
        "Unable to locate the 'fuseki-server' executable.\n"
        "How to fix:\n"
        "  • Install Apache Jena Fuseki and set FUSEKI_HOME to its installation directory.\n OR\n"
        "  • Ensure the directory containing 'fuseki-server' is on your PATH.\n OR\n"
        "  • On Windows, the launcher may be 'fuseki-server.bat' or 'fuseki-server.cmd'.\n\n"
        "Examples (Linux/macOS):\n"
        '  export FUSEKI_HOME="/path/to/apache-jena-fuseki-<version>"\n'
        '  export PATH="$FUSEKI_HOME:$PATH"\n'
        "  command -v fuseki-server\n\n"
        "Examples (Windows PowerShell):\n"
        "  $env:FUSEKI_HOME='C:\\\\path\\\\to\\\\apache-jena-fuseki-<version>'\n"
        '  $env:Path="$env:FUSEKI_HOME;$env:Path"\n'
        "  where fuseki-server\n\n"
        "If the issue persists, verify that the file exists and is executable (Permissions)\n"
        "and that you have access rights to the directory."
    )

    raise FileNotFoundError(msg)


def create_config_and_run_fuseki(dataset_name: str, show_server_logs: bool = False) -> Path:
    """
    Create a minimal Fuseki config.ttl for a TDB2-backed dataset and launch Fuseki.

    The config exposes the endpoints: query, update, data (GSP RW), upload.

    Args:
        dataset_name: Desired dataset/service name (will be sanitized for URL path).
        show_server_logs: If True, forward server stdout/stderr to the terminal.
                          If False (default), silence server output.

    Returns:
        Path to the written config.ttl.

    Raises:
        RuntimeError if the server does not become ready within the startup timeout.
        FileNotFoundError if 'fuseki-server' cannot be located.
    """
    service = sanitize_fuseki_dataset_name(dataset_name)
    tdb2_loc = create_tdb2_location()
    config_path = create_config_path()

    ttl = dedent(f"""
    PREFIX fuseki:  <http://jena.apache.org/fuseki#>
    PREFIX tdb2:    <http://jena.apache.org/2016/tdb#>
    PREFIX ja:      <http://jena.hpl.hp.com/2005/11/Assembler#>

    <#service> a fuseki:Service ;
      fuseki:name "{service}" ;
      fuseki:endpoint [ fuseki:operation fuseki:query  ; fuseki:name "query"  ] ;
      fuseki:endpoint [ fuseki:operation fuseki:update ; fuseki:name "update" ] ;
      fuseki:endpoint [ fuseki:operation fuseki:gsp_rw ; fuseki:name "data"   ] ;
      fuseki:endpoint [ fuseki:operation fuseki:upload ; fuseki:name "upload" ] ;
      fuseki:dataset <#dataset> .

    <#dataset> a tdb2:DatasetTDB2 ;
      tdb2:location "{tdb2_loc.as_posix()}" .
    """).strip() + "\n"

    config_path.write_text(ttl, encoding="utf-8")

    # Sensible defaults for memory (no-op if already set outside)
    os.environ.setdefault("JAVA_TOOL_OPTIONS", "-Xms4g -Xmx8g")

    fuseki = find_fuseki_server()
    # Start Fuseki with explicit --config
    if show_server_logs:
        subprocess.Popen([fuseki, "--config", str(config_path)])
    else:
        subprocess.Popen(
            [fuseki, "--config", str(config_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    base_url = f"http://localhost:3030/{service}/query"
    timeout = 20
    start_time = time.time()
    while True:
        try:
            response = requests.post(base_url, data={"query": "ASK {}"}, timeout=2)
            if response.status_code == 200:
                print(f"[APACHE JENA] Server is up after {time.time() - start_time:.1f}s.")
                break
        except requests.RequestException:
            pass
        if time.time() - start_time > timeout:
            msg = f"[APACHE JENA] Server did not start within {timeout}s."
            raise RuntimeError(msg)
        time.sleep(1)

    return config_path


def stop_fuseki_server(timeout: int = 5) -> bool:
    """
    Stop all running 'fuseki-server' processes on this machine.

    This is a broad stop: it does not target a specific dataset/config.
    It first attempts a graceful terminate(), then force kills if needed.

    Args:
        timeout: Seconds to wait for graceful termination before kill().

    Returns:
        True if at least one process was stopped, False if none was found.
    """
    found = False
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info.get("cmdline") or []
            if any("fuseki-server" in part for part in cmdline):
                found = True
                proc.terminate()
                try:
                    proc.wait(timeout=timeout)
                except psutil.TimeoutExpired:
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return found


def add_graph_clause_if_needed(q: str, graph: str) -> str:
            lower = q.lower()
            where_idx = lower.find(" where ")
            if where_idx == -1 or "select" not in lower[:where_idx]:
                return q
            try:
                open_idx = q.index("{", where_idx)
            except ValueError:
                return q

            if "graph" in q[open_idx: open_idx + len(q)].lower():
                return q

            depth, close_idx = 0, -1
            for i in range(open_idx, len(q)):
                ch = q[i]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        close_idx = i
                        break
            if close_idx == -1:
                return q

            return (
                q[:open_idx + 1]
                + f" GRAPH <{graph}> {{"
                + q[open_idx + 1:close_idx]
                + " }"
                + q[close_idx:]
            )
