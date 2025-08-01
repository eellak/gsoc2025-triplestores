# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0

import csv
import io
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from time import sleep
from typing import Any

import requests

from triplestore.base import TriplestoreBackend

logger = logging.getLogger(__name__)


class MillenniumDB(TriplestoreBackend):
    """
    MillenniumDB backend using the official CLI tools and subprocess.
    """
    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

        self.mdb_home = Path(config.get("mdb_home", "~/projects/MillenniumDB")).expanduser()
        if not self.mdb_home.exists():
            msg = f"[MillenniumDB] Path does not exist: {self.mdb_home}"
            raise FileNotFoundError(msg)
        self.db_dir = self.mdb_home / "mdb_benchmark_db"

        self.mdb_import = self.mdb_home / "build" / "Release" / "bin" / "mdb-import"
        self.mdb_server = self.mdb_home / "build" / "Release" / "bin" / "mdb-server"
        self.mdb_query = self.mdb_home / "scripts" / "query"

        self.graph_uri = config.get("graph")
        self.server_process: subprocess.Popen | None = None

        if not self.mdb_import.exists() or not self.mdb_server.exists():
            subprocess.run(["cmake", "-Bbuild/Release", "-DCMAKE_BUILD_TYPE=Release"],
                        cwd=self.mdb_home, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            subprocess.run(["cmake", "--build", "build/Release", "-j", "4"],
                        cwd=self.mdb_home, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def load(self, filename: str) -> None:
        if self.db_dir.exists():
            shutil.rmtree(self.db_dir)

        result = subprocess.run([str(self.mdb_import), str(filename), str(self.db_dir)], cwd=self.mdb_home, capture_output=True, check=True)

        if result.returncode != 0:
            msg = f"[MillenniumDB] Load failed:\n{result.stderr.decode()}"
            raise RuntimeError(msg)

        self.server_process = subprocess.Popen([str(self.mdb_server), str(self.db_dir)], cwd=self.mdb_home,
                                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sleep(1)

    def add(self, s: str, p: str, o: str) -> None:
        self._start_server()
        existing = self.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
        self._stop_server()

        triple = {"s": f"<{s}>", "p": f"<{p}>", "o": f"<{o}>"}
        if triple in existing:
            return

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".ttl", mode="w", encoding="utf-8")
        tmp.write(f"<{s}> <{p}> <{o}> .\n")
        tmp.close()

        self.load(tmp.name)
        Path(tmp.name).unlink(missing_ok=True)

    def delete(self, s: str, p: str, o: str) -> None:
        self._start_server()
        existing = self.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
        self._stop_server()

        target = {"s": f"<{s}>", "p": f"<{p}>", "o": f"<{o}>"}
        triples = [row for row in existing if row != target]

        if len(triples) == len(existing):
            return

        with tempfile.NamedTemporaryFile(mode="w", suffix=".ttl", delete=False) as f:
            for row in triples:
                f.write(f"{row['s']} {row['p']} {row['o']} .\n")
            ttl_path = f.name

        if self.db_dir.exists():
            shutil.rmtree(self.db_dir)

        result = subprocess.run(
            [str(self.mdb_import), ttl_path, str(self.db_dir)],
            cwd=self.mdb_home,
            capture_output=True, check=True
        )
        Path(ttl_path).unlink(missing_ok=True)

        if result.returncode != 0:
            msg = f"[MillenniumDB] Delete failed:\n{result.stderr.decode()}"
            raise RuntimeError(msg)

        self._start_server()

    def query(self, sparql: str) -> list[dict[str, str]]:
        url = "http://localhost:1234/sparql"
        headers = {
            "Content-Type": "application/sparql-query",
            "Accept": "text/csv"
        }

        response = requests.post(url, headers=headers, data=sparql, timeout=60)

        if response.status_code != 200:
            msg = f"[MillenniumDB] Query failed with status {response.status_code}:\n{response.text}"
            raise RuntimeError(msg)

        try:
            csv_text = response.text
            reader = csv.DictReader(io.StringIO(csv_text))
            return [{k: v for k, v in row.items()} for row in reader]
        except (UnicodeDecodeError, csv.Error) as e:
            msg = f"[MillenniumDB] Failed to parse query output:\n{e}"
            raise RuntimeError(msg) from e

    def clear(self) -> None:
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None

        if self.db_dir.exists():
            shutil.rmtree(self.db_dir)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".ttl", encoding="utf-8", delete=False) as f:
            f.write("")  # no triples
            empty_ttl = f.name

        result = subprocess.run(
            [str(self.mdb_import), empty_ttl, str(self.db_dir)],
            cwd=self.mdb_home,
            capture_output=True, check=True
        )
        Path(empty_ttl).unlink(missing_ok=True)

        if result.returncode != 0:
            msg = f"[MillenniumDB] Clear/import empty failed:\n{result.stderr.decode()}"
            raise RuntimeError(msg)

        self.server_process = subprocess.Popen(
            [str(self.mdb_server), str(self.db_dir)],
            cwd=self.mdb_home,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        sleep(1)

    def __del__(self) -> None:
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()

    def _start_server(self):
        if self.server_process is None:
            self.server_process = subprocess.Popen(
                [str(self.mdb_server), str(self.db_dir)],
                cwd=self.mdb_home,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            sleep(1)

    def _stop_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
