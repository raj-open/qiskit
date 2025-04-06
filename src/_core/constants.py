#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from typing import Literal

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "BASIC_FILETYPES",
    "ENCODING",
    "MIME_TYPES",
    "SIZE_1_KB",
    "SIZE_1_MB",
]

# ----------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------

SIZE_1_KB = 2**10
SIZE_1_MB = 2**10

ENCODING = Literal[
    "ascii",
    "utf-8",
    "unicode_escape",
]

BASIC_FILETYPES = Literal[
    ".json",
    ".yaml",
    ".csv",
    ".xlsx",
    ".pdf",
    ".txt",
    ".ifc",
]

MIME_TYPES = [
    "application/octet-stream",
    "text/plain",
    "application/json",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/x-yaml",
]
