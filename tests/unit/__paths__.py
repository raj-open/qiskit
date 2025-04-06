#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import os
import re
from pathlib import Path

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "get_mock_case_path",
    "get_module",
    "get_resource_path",
    "get_root_path",
    "get_source_path",
]

# ----------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------

_source = str(Path(__file__).parent)
_root = str(Path(__file__).parent.parent.parent)

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def get_path(root: str, *parts: str) -> str:
    return root if len(parts) == 0 else os.path.join(root, *parts)


def get_root_path(*parts: str) -> str:
    return get_path(_root, *parts)


def get_source_path(*parts: str) -> str:
    return get_path(_source, *parts)


def get_resource_path(*parts: str) -> str:
    """
    @returns path within `resource` folder
    """
    return get_source_path("resources", *parts)


def get_mock_case_path(*parts: str, case: int) -> str:
    """
    @returns path within `resources/mock_cases/mock_case{n}` folder
    """
    return get_resource_path("mock_cases", f"mock_case{case}", *parts)


def get_module(path: str, root="src", prefix=r"^tests_(.*)") -> str:
    """
    Replaces path to current file by corresponding module in source.
    """
    path = os.path.relpath(path=path, start=_source)
    # remove extension
    path = os.path.splitext(path)[0]
    # remove test-prefixes
    parts = re.split(pattern=r"/", string=path)
    parts = [re.sub(pattern=prefix, repl=r"\1", string=part) for part in parts]
    # join to form module name
    m = ".".join([root, *parts])
    return m
