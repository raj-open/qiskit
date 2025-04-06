#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.code import *
from src.thirdparty.config import *
from src.thirdparty.system import *
from src.thirdparty.types import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    "get_env_float",
    "get_env_int",
    "get_env_optional_float",
    "get_env_optional_int",
    "get_env_optional_string",
    "get_env_string",
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_env_value(env: dict, key: str, default: Any = None) -> Any:  # pragma: no cover
    return env[key] if key in env else default


def get_env_string(env: dict, key: str, default: str | None = None) -> str:
    result = Result.of(lambda: str(env[key] or default))
    if default is None:
        return result.unwrap()
    return result.unwrap_or(default)


def get_env_optional_string(env: dict, key: str) -> str | None:
    result = Result.of(lambda: str(env[key]))
    return result.unwrap_or(None)


def get_env_int(env: dict, key: str, default: int | None = None) -> int:
    result = Result.of(lambda: int(env[key] or default))
    if default is None:
        return result.unwrap()
    return result.unwrap_or(default)


def get_env_optional_int(env: dict, key: str) -> int | None:
    result = Result.of(lambda: int(env[key]))
    return result.unwrap_or(None)


def get_env_float(env: dict, key: str, default: float | None = None) -> float:
    result = Result.of(lambda: float(env[key] or default))
    if default is None:
        return result.unwrap()
    return result.unwrap_or(default)


def get_env_optional_float(env: dict, key: str) -> float | None:
    result = Result.of(lambda: float(env[key]))
    return result.unwrap_or(None)
