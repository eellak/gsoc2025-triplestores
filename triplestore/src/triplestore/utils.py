from __future__ import annotations

# Copyright (C) 2025 Maira Papadopoulou
# SPDX-License-Identifier: Apache-2.0
import logging
import platform
import subprocess
from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

from triplestore.exceptions import TriplestoreMissingConfigValue

logger = logging.getLogger(__name__)


def detect_host_url(port: int, path: str = "", fallback: str | None = None) -> str:
    """
    Detect the Windows host IP from within WSL and return the base URL to use for HTTP services.
    Falls back to localhost if detection fails.

    Parameters
    ----------
    port : int
        Target TCP port to include in the returned URL.
    path : str, optional
        Optional path suffix to append to the base URL (default: "").
    fallback : str | None, optional
        If provided, this URL is returned when auto-detection fails.

    Returns
    -------
    str
        The detected base URL, or the fallback/localhost URL when detection fails.
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


def validate_config(user_config: Mapping[str, Any], *, required_keys: Iterable[str], optional_defaults: Mapping[str, Any] | None,
                    alias_map: Mapping[str, Any] | None, backend_name: str = "backend") -> dict[str, Any]:
    """
    Validate and normalize a backend configuration dictionary.

    This function ensures that:
    1. All required keys are present (after resolving aliases).
    2. Optional keys are filled in with defaults if not provided.
    3. Unknown keys trigger a warning message (but are preserved in the result).

    Parameters
    ----------
    user_config : Mapping[str, Any]
        The configuration dictionary provided by the user.
    required_keys : Iterable[str]
        Keys that must always be present in the final configuration.
    optional_defaults : Mapping[str, Any], optional
        Optional keys with their default values if missing.
    alias_map : Mapping[str, str], optional
        Mapping of alias → canonical key names.
    backend_name : str, default="backend"
        Name of the backend, used in error/warning messages.

    Returns
    -------
    dict[str, Any]
        A normalized configuration dictionary containing:
        - All required keys,
        - All optional keys (with user or default values),
        - All provided aliases converted to canonical keys,
        - Any unknown keys (with a warning).

    Raises
    ------
    ValueError
        If one or more required keys are missing.
    """

    if optional_defaults is None:
        optional_defaults = {}
    if alias_map is None:
        alias_map = {}

    normalized_config: dict[str, Any] = {}
    for key, value in user_config.items():
        canonical_key = alias_map.get(key, key)
        normalized_config[canonical_key] = value

    missing_keys = [k for k in required_keys if k not in normalized_config]
    if missing_keys:
        msg = (
            f"[{backend_name}] Configuration error: Missing required config keys for: '"
            f"{', '.join(missing_keys)}'"
        )
        raise TriplestoreMissingConfigValue(msg)

    for key, default_val in optional_defaults.items():
        if key not in normalized_config:
            normalized_config[key] = default_val

    allowed_keys = set(required_keys) | set(optional_defaults)
    allowed_with_aliases = allowed_keys | set(alias_map.keys())
    unknown_keys = [k for k in user_config if k not in allowed_with_aliases]

    if unknown_keys:
        msg = (
            f"[{backend_name}] Ignoring unrecognized config keys for: '"
            f"{', '.join(sorted(unknown_keys))}'"
        )
        logger.warning(msg)

    return normalized_config
