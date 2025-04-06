#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from math import isnan
from typing import Any
from typing import Literal
from typing import TypeVar

import polars as pl

from .code import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "combine_subtables",
    "polars_clean_booleans",
    "polars_clean_numbers",
    "polars_coerce_empty",
    "polars_count_non_empty",
    "polars_drop_null",
    "polars_fill_null",
    "polars_fuzzy_rounding",
    "polars_get_null",
    "polars_get_unique_values",
    "polars_is_empty",
]

# ----------------------------------------------------------------
# LOCAL CONSTANTS / VARIABLES
# ----------------------------------------------------------------

T = TypeVar("T")
RETURN = TypeVar("RETURN")


# ----------------------------------------------------------------
# GET VALUES
# ----------------------------------------------------------------


def polars_get_unique_values(
    X: pl.Series,
    /,
    *,
    drop_empty: bool = True,
) -> list[T]:
    """
    Gets all unique non-null values of a series
    If of type string, optionally drops empty strings.
    """
    X = polars_drop_null(X)
    X = X.unique()

    if drop_empty and X.dtype == pl.String:
        X = X.filter(~X.eq(""))

    return X.to_list()


# ----------------------------------------------------------------
# HANDLE NULLS
# ----------------------------------------------------------------


def polars_drop_null(X: pl.Series, /) -> pl.Series:
    """
    Drops elements of a series which are null, NA, etc.
    """
    try:
        X = X.drop_nulls()

    except Exception as _:
        pass

    try:
        X = X.drop_nans()

    except Exception as _:
        pass

    return X


def polars_get_null(X: pl.Series, /) -> pl.Series:
    """
    Returns when element of a series are null, NA, etc.
    """
    try:
        return X.is_null() | X.is_nan()

    except Exception as _:
        return X.is_null()


def polars_fill_null(X: pl.Series, value: Any, /) -> pl.Series:
    """
    Returns when element of a series are null, NA, etc.
    """
    if isinstance(value, float) and isnan(value):
        value = None
    cond = polars_get_null(X)
    data = pl.DataFrame({"values": X}, strict=False)
    data = data.with_columns(
        pl.when(cond)
        .then(pl.lit(value))
        .otherwise(pl.col("values"))
        .alias("values")
    )  # fmt: skip
    X = data.get_column("values")
    return X


# ----------------------------------------------------------------
# COUNTS
# ----------------------------------------------------------------


def polars_coerce_empty(X: pl.Series, /) -> pl.Series:
    """
    Coerces empty-like values to nulls.
    We consider "empty" the following values:

    - `""` if column type is string
    - `0.0` if column type is numerical (but not integer)

    NOTE: since integers can be used as indices,
    we do not want to treat the value 0 (which could simply the value of an id)
    as "empty".
    """
    match X.dtype:
        case pl.String():
            X = X.replace("", None)

        case t if t in [pl.Float32, pl.Float64]:
            X = X.fill_nan(None)
            X = X.replace(0, None)

        # case t if t.is_numeric():
        #     return X.replace(0, None).null_count()

    return X


def polars_is_empty(X: pl.Series, /) -> bool:
    """
    Determines whether a column consists purely of empty values.
    We also consider "empty" the following values:

    - `""` if column type is string
    - `0.0` if column type is numerical (but not integer)

    NOTE: since integers can be used as indices,
    we do not want to treat the value 0 (which could simply the value of an id)
    as "empty".
    """
    X = polars_coerce_empty(X)
    return X.is_null().all()


def polars_count_non_empty(X: pl.Series, /) -> int:
    """
    Returns the number of non-empty values in a column
    We also consider "empty" the following values:

    - `""` if column type is string
    - `0.0` if column type is numerical (but not integer)

    NOTE: since integers can be used as indices,
    we do not want to treat the value 0 (which could simply the value of an id)
    as "empty".
    """
    X = polars_coerce_empty(X)
    num_nulls = X.null_count()
    n = len(X)
    return n - num_nulls


# ----------------------------------------------------------------
# NUMERICAL
# ----------------------------------------------------------------


def polars_fuzzy_rounding(
    X: pl.Series,
    /,
    *,
    n: int,
):
    """
    Uses pure polars methods to cleanly round values.
    E.g.
    ```py
    X = pl.Series([
        19.000000009,
        89.123000000001,
        74.4657152673,
        None,
    ])
    print(polars_fuzzy_rounding(X, n=5))
    ```
    results in
    ```bash
    shape: (4,)
    Series: '' [str]
    [
        "19"
        "89.123"
        "74.46572"
        null
    ]
    ```
    """
    X = (
        X
        # ensure high precision otherwise numbers will be rounded too strongly
        .cast(pl.Float64)
        # perform rounding round
        .round(
            n
        )  # NOTE: this keeps numbers in floating point format, so str(...) will always contain "."
        # cast as string
        .cast(pl.String)
        # trim trailing 0s past decimal point
        .str.strip_chars_end("0")
        # trim decimal point (if and only if there are no post-decimal digits)
        .str.strip_chars_end(".")
    )
    return X


# ----------------------------------------------------------------
# COERCION
# ----------------------------------------------------------------


def polars_clean_booleans(
    X: pl.Series,
    /,
):
    """
    Given a data series of strings
    attempts to convert strings to boolean values in as safe and reliable manner as possible.
    """
    X = X.str.to_lowercase()
    # replace all escaped quotes by quotes
    X = X.str.replace_all(r"\\(\"|')", "$1", literal=False)
    # strip all quotes
    X = X.str.replace_all(r"^(\"|')+|(\"|')+$", "", literal=False)
    # trim leading/trailing whitespace
    X = X.str.replace_all(r"^\s+|\s+$", "", literal=False)
    # replace empty strings by nulls
    X = X.replace(pl.lit(""), pl.lit(None), return_dtype=pl.String)
    # replace 0/1 by false/true
    X = X.str.replace(r"^0$", "false", literal=False)
    X = X.str.replace(r"^1$", "true", literal=False)
    # deserialise "false" -> False, "true" -> "True"
    X = X.str.json_decode(pl.Boolean, infer_schema_length=None)
    return X


def polars_clean_numbers(
    X: pl.Series,
    /,
    *,
    ambivalences: Literal["std", "non-std"] | None = None,
) -> pl.Series:
    """
    Given a data series of strings
    attempts to prepare numerical values for conversion to floating point numbers

    In the case of ambivalent formats (some with `.` some with `,` as decimal points)
    looks to full context to determine whether all values can be treated
    as `standard` (`.`) or `non-standard` (`,`) numbers.

    If ambivalences are unresolvable throws an error,
    unless the `ambivalences` argument is set.
    """
    if X.dtype not in [pl.String, pl.Utf8]:
        return X

    # store in a data frame
    data = pl.DataFrame({"values": X}, schema={"values": pl.String})

    # strip out escaped quotes
    data = data.with_columns(
        pl.col("values")
        # replace all escaped quotes by quotes
        .str.replace_all(r"\\(\"|')", "$1", literal=False)
        # strip all quotes
        .str.replace_all(r"^(\"|')+|(\"|')+$", "", literal=False)
        # trim leading/trailing whitespace
        .str.replace_all(r"^\s+|\s+$", "", literal=False)
        # replace empty strings by nulls
        .replace(pl.lit(""), pl.lit(None), return_dtype=pl.String)
        .alias("values")
    )

    # pattern for number + possibly empty information e.g. units
    pattern = r"^\s*([\+\-]?\d+(?:\s*[\.\,]?\s*\d+)*[\.\,]?(?:\s*[Ee]\s*[\+\-]?\s*\d+)?)\s*(.*\S|)\s*$"  # fmt: skip
    pattern_standard = r"^[\+\-]?\d+([\,]?\d{3})*([\.]\d*)?([Ee][\+\-]?\s*\d+)?$"  # fmt: skip
    pattern_non_standard = r"^[\+\-]?\d+([\.]?\d{3})*([\,]\d*)?([Ee][\+\-]?\s*\d+)?$"  # fmt: skip

    # read out number and information
    data = data.with_columns(
        pl.col("values")
        .str
        .contains(pattern, literal=False)
        .alias("match")
    )  # fmt: skip
    data = data.with_columns(
        pl.when(pl.col("match"))
        .then(
            # extract number part and remove all white space
            pl.col("values")
            .str
            .replace_all(pattern, r"${1}", literal=False)
            .str
            .replace_all(r"\s", r"", literal=False)
        )
        .otherwise(pl.lit(None))
        .alias("number")
    )  # fmt: skip

    # recognise standard/non-standard numerical patterns
    data = data.with_columns(
        pl.col("number").str.contains(pattern_standard, literal=False).alias("match-std")
    )  # fmt skip
    data = data.with_columns(
        pl.col("number")
        .str.contains(pattern_non_standard, literal=False)
        .alias("match-non-std")
    )  # fmt skip

    # update matching
    data = data.with_columns(
        (pl.col("match-std") | pl.col("match-non-std")).alias("match")
    )  # fmt skip
    data = data.with_columns(
        pl.when(pl.col("match"))
        .then(
            # extract info part
            pl.col("values")
            .str
            .replace_all(pattern, r"${2}", literal=False)
        )
        .otherwise(pl.lit(None))
        .alias("info")
    )  # fmt: skip

    # process standard/non-standard numbers
    data = data.with_columns(
        pl.when(pl.col("match-std"))
        .then(
            pl.col("number")
            # remove all commas
            .str
            .replace_all(r",", r"", literal=False)
        )
        .otherwise(pl.lit(None))
        .alias("number-std")
    )  # fmt: skip
    data = data.with_columns(
        pl.when(pl.col("match-non-std"))
        .then(
            pl.col("number")
            # remove all points
            .str
            .replace_all(r"\.", r"", literal=False)
            # replace (all = final) comma with point
            .str
            .replace_all(r",", r".", literal=False)
        )
        .otherwise(pl.lit(None))
        .alias("number-non-std")
    )  # fmt: skip

    # check ambivalences
    data = data.with_columns(
        pl.when(
            pl.col("number-std").is_not_null(),
            pl.col("number-non-std").is_not_null(),
            ~pl.col("number-std").eq(pl.col("number-non-std")),
        )
        .then(pl.lit(True))
        .otherwise(pl.lit(False))
        .alias("ambivalent")
    )  # fmt: skip

    # compute number of ambivalent cases
    num_ambivalent = data["ambivalent"].sum()

    # determine *in full context* whether all are std / all are non-std
    all_std = (data["match-non-std"] & ~data["match-std"]).sum() == 0  # fmt: skip
    all_non_std = (data["match-std"] & ~data["match-non-std"]).sum() == 0  # fmt: skip

    # set number for non-ambivalent cases
    data = data.with_columns(pl.lit(None).alias("number"))
    data = data.with_columns(
        pl.when(
            ~pl.col("ambivalent"),
            pl.col("number-non-std").is_not_null(),
        )
        .then(pl.col("number-non-std"))
        .otherwise(pl.col("number"))
        .alias("number")
    )  # fmt: skip
    data = data.with_columns(
        pl.when(
            ~pl.col("ambivalent"),
            pl.col("number-std").is_not_null(),
        )
        .then(pl.col("number-std"))
        .otherwise(pl.col("number"))
        .alias("number")
    )  # fmt: skip

    match all_std, all_non_std, num_ambivalent, ambivalences:
        case _, _, 0, _:
            pass

        case (True, _, _, _) | (False, False, _, "std"):
            # there are ambivalences, but from the context we make assume that all numbers use . as decimal,
            # or else the coercion argument is set
            data = data.with_columns(
                pl.when(pl.col("ambivalent"))
                .then(pl.col("number-std"))
                .otherwise(pl.col("number"))
                .alias("number")
            )  # fmt: skip

        case (_, True, _, _) | (False, False, _, "non-std"):
            # there are ambivalences, but from the context we make assume that all numbers use , as decimal
            # or else the coercion argument is set
            data = data.with_columns(
                pl.when(pl.col("ambivalent"))
                .then(pl.col("number-non-std"))
                .otherwise(pl.col("number"))
                .alias("number")
            )  # fmt: skip

        case _:
            # there are ambivalences, and in the context no assumptions can be made and no coercion is set
            raise Exception(f"{num_ambivalent} entries exhibit an ambivalent numerical format and it is unclear from the table whether all numbers use . or , as decimal!")  # fmt: skip

    # join back in with information
    data = data.with_columns(
        pl.when(pl.col("match"))
        # join split parts where the format was recognised
        .then(
            data.select(
                # concatenate with space as delimiter
                pl.concat_str(
                    "number",
                    "info",
                    separator=" ",
                    ignore_nulls=False,
                )
                # strip white space
                .str
                .strip_chars()
                .alias("values")
            )["values"]
        )
        # otherwise restore original values
        .otherwise(pl.col("values"))
    )  # fmt: skip

    # get values
    X = data["values"]

    return X


# ----------------------------------------------------------------
# COMBINATIONS
# ----------------------------------------------------------------


def combine_subtables(
    *parts: pl.DataFrame,
    sort: bool = True,
    reset: bool = False,
) -> pl.DataFrame:
    """
    Safely vertically stacks tables
    """
    result = pl.concat(parts, how="diagonal_relaxed") if len(parts) > 0 else pl.DataFrame()
    # TODO: add these methods
    # if sort:
    #     # DEV-NOTE: .sort_index ensures data stays in original order
    #     result = result.sort_index()
    #     result = result.with_row_index().sort(pl.col("index"))
    # if reset:
    #     result = result.reset_index(drop=True)
    return result
