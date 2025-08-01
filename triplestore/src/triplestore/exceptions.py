# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0


class TriplestoreError(Exception):
    """Base exception for the triplestore library."""


class BackendNotFoundError(TriplestoreError):
    """Raised when a backend is not registered or supported."""
