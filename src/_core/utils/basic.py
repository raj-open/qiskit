#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import json
import re
from datetime import datetime
from enum import Enum
from enum import StrEnum
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Sequence
from typing import TypeVar
from typing import overload

from .code import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "extract_string",
    "extract_strip",
    "flatten",
    "flatten_sets",
    "indicator_function_factory",
    "json_deserialise",
    "safe_format_string",
    "split_string_list",
]

# ----------------------------------------------------------------
# LOCAL CONSTANTS / VARIABLES
# ----------------------------------------------------------------

MAX_ITER = 1000
T = TypeVar("T")
_DATE_PATTERN = re.compile(pattern=r"^\d+-\d+-\d+$")
_TIME_PATTERN = re.compile(pattern=r"^\d+:\d+(:\d+(\.\d+)?)?$")

# ----------------------------------------------------------------
# METHODS - STRINGS
# ----------------------------------------------------------------


def safe_format_string(
    text: str,
    *pos_args: Any,
    **kwargs: Any,
) -> str:
    """
    Safely formats string leaving missing arguments alone.
    """
    n_pos = len(pos_args)
    for _ in range(MAX_ITER):
        try:
            return text.format(*pos_args, **kwargs)

        except IndexError as err:
            if n_pos == 0:
                text = re.sub(pattern="\\{\\}", repl="{{}}", string=text)
            text = re.sub(pattern=f"\\{{{n_pos}\\}}", repl=f"{{{{{n_pos}}}}}", string=text)
            n_pos += 1

        except KeyError as err:
            key = [*err.args, "?"][0]
            text = re.sub(pattern=f"\\{{{key}\\}}", repl=f"{{{{{key}}}}}", string=text)

    raise Exception(f"could not safely format '{text}'")


@overload
def extract_string(x: None, /) -> None: ...


@overload
def extract_string(x: str | StrEnum, /) -> str: ...


@overload
def extract_string(x: Sequence[str | StrEnum] | set[str | StrEnum], /) -> list[str]: ...


@overload
def extract_string(x: dict[str | StrEnum, str | StrEnum], /) -> dict[str, str]: ...


def extract_string(
    x: (
        None
        | str
        | StrEnum
        | Sequence[str | StrEnum]
        | set[str | StrEnum]
        | dict[str | StrEnum, str | StrEnum]
    ),
    /,
):  # -> None | str | list[str] | dict[str, str]:
    """
    Returns the underlying string value of a string or string-enum.

    - Converts string/enum to string
    - Converts list of strings/enums to list of strings
    - Converts dictionary of strings/enums to dictionary of strings
    """
    match x:
        case None:
            return None

        # DEV-NOTE: must prioritise Enum over str, since StrEnum extends str!
        case Enum():
            return x.value

        case str():
            return x

        case dict():
            return {extract_string(key): extract_string(value) for key, value in x.items() }  # fmt: skip

        case _:
            return [extract_string(xx) for xx in x]


def extract_strip(
    x: str | StrEnum,
    /,
    *,
    left: str | None = None,
    right: str | None = None,
) -> str:
    """
    Performs left/right-strip to a string or string enum.
    """
    x = extract_string(x)

    if left is not None:
        x = x.removeprefix(left)

    if right is not None:
        x = x.removesuffix(right)

    return x


def json_deserialise(x: str) -> Any:
    """
    Parses a JSON-ised string
    """
    # if parses normally, return this
    try:
        return json.loads(x)

    except Exception as err:
        pass

    # otherwise attempt to parse as time/date
    try:
        if re.match(pattern=_TIME_PATTERN, string=x):
            return datetime.fromisoformat(f"2000-01-01 {x}").time()

        elif re.match(pattern=_DATE_PATTERN, string=x):
            return datetime.fromisoformat(x).date()

        else:
            return datetime.fromisoformat(x)

    except Exception as err:
        pass

    raise Exception(f"failed to parse {x}")


def split_string_list(
    value: str | None,
    /,
    *,
    sep: str = ",",
    remove_empty: bool = True,
) -> list[str]:
    """
    Parses a (typically) comma-separated list of string as a list of strings,
    optionally removes empty values (default `true`).
    """
    if value is None:
        return []

    value = value.strip()
    if value == "":
        return []

    values: list[str] = re.split(pattern=sep, string=value or "")
    values = [x.strip() for x in values]
    if remove_empty:
        values = [x for x in values if x != ""]

    return values


# ----------------------------------------------------------------
# METHODS - FUNCTIONS
# ----------------------------------------------------------------


def indicator_function_factory(value: T) -> Callable[[T], bool]:
    """
    Returns a boolean-valued function
    that returns `true` <==> the given value is assumed.
    """

    def indicator_function(x: T) -> bool:
        return x == value

    return indicator_function


# ----------------------------------------------------------------
# METHODS - ARRAYS
# ----------------------------------------------------------------


def flatten(X: Iterable[list[T]]) -> list[T]:
    X_flat = []
    for XX in X:
        X_flat.extend(XX)
    return X_flat


def flatten_sets(X: Iterable[set[T]]) -> set[T]:
    X_flat = set([])
    for XX in X:
        X_flat = X_flat.union(XX)
    return X_flat
