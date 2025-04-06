#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from math import nan

import polars as pl

from tests.unit.thirdparty.unit import *

from src._core.utils.dataframes import *

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------


@fixture(scope="function", autouse=False)
def ser_values_string() -> pl.Series:
    return pl.Series(
        [
            "cat",
            None,
            "ant",
            "",
            "",
            "ant",
            "elephant",
            None,
            None,
            "tiger",
        ],
        dtype=pl.String,
    )


@fixture(scope="function", autouse=False)
def ser_values_numbers() -> pl.Series:
    return pl.Series(
        [
            94,
            None,
            -8,
            0,
            0,
            58,
            -8,
            nan,
            None,
            1000,
        ],
        dtype=pl.Int64,
        strict=False,
    )


@fixture(scope="function", autouse=False)
def ser_international1() -> pl.Series:
    return pl.Series(
        [
            "cat",
            None,
            "m^2",
            "5",
            "5 m^2",
            "-3.1",
            "-3.1 E-6 m/s^2",
            "7.1",
            "+7.1",
            "8000.2",
            "8 000.2",
            "8,000.2",
            "1030200.4",
            "1 030 200.4",
            "1 030 200.4 kg * m / s^2",
            "1,030,200.4",
            "1,030,200.4 kg * m / s^2",
        ],
        dtype=pl.String,
    )


@fixture(scope="function", autouse=False)
def ser_non_international1() -> pl.Series:
    return pl.Series(
        [
            "cat",
            None,
            "m^2",
            "5",
            "5 m^2",
            "-3,1",
            "-3,1 E-6 m/s^2",
            "7,1",
            "+7,1",
            "8000,2",
            "8 000,2",
            "8.000,2",
            "1030200,4",
            "1 030 200,4",
            "1 030 200,4 kg * m / s^2",
            "1.030.200,4",
            "1.030.200,4 kg * m / s^2",
        ],
        dtype=pl.String,
    )


@fixture(scope="function", autouse=False)
def ser_formatted1() -> pl.Series:
    return pl.Series(
        [
            "cat",
            None,
            "m^2",
            "5",
            "5 m^2",
            "-3.1",
            "-3.1E-6 m/s^2",
            "7.1",
            "+7.1",
            "8000.2",
            "8000.2",
            "8000.2",
            "1030200.4",
            "1030200.4",
            "1030200.4 kg * m / s^2",
            "1030200.4",
            "1030200.4 kg * m / s^2",
        ],
        dtype=pl.String,
    )


@fixture(scope="function", autouse=False)
def ser_numbers2() -> pl.Series:
    return pl.Series(
        [
            19.000000009,
            1900.000000009,
            1900,
            89.123000000001,
            74.4657142673,
            74.4657152673,
            None,
        ],
        dtype=pl.Float64,
        strict=False,
    )


@fixture(scope="function", autouse=False)
def ser_formatted2() -> pl.Series:
    return pl.Series(
        [
            "19",
            "1900",
            "1900",
            "89.123",
            "74.46571",
            "74.46572",
            None,
        ],
        dtype=pl.String,
    )


# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


def tests_polars_get_unique_values(
    # fixtures
    test: TestCase,
    ser_values_string: pl.Series,
    ser_values_numbers: pl.Series,
):
    X = ser_values_string
    X_ = polars_get_unique_values(X, drop_empty=True)
    test.assertSetEqual(
        set(X_),
        {
            "cat",
            "ant",
            "elephant",
            "tiger",
        },
    )

    X_ = polars_get_unique_values(X, drop_empty=False)
    test.assertSetEqual(
        set(X_),
        {
            "",
            "cat",
            "ant",
            "elephant",
            "tiger",
        },
    )

    X = ser_values_numbers
    X_ = polars_get_unique_values(X)
    test.assertSetEqual(
        set(X_),
        {
            -8,
            0,
            58,
            94,
            1000,
        },
    )

    return


def tests_polars_clean_numbers_DECIMALS_AS_POINTS(
    # fixtures
    test: TestCase,
    ser_international1: pl.Series,
    ser_formatted1: pl.Series,
):
    X = ser_international1
    expected = ser_formatted1
    result = polars_clean_numbers(X)
    test.assertTrue(result.equals(expected, null_equal=True))
    pass


def tests_polars_clean_numbers_DECIMALS_AS_COMMAS(
    # fixtures
    test: TestCase,
    ser_non_international1: pl.Series,
    ser_formatted1: pl.Series,
):
    X = ser_non_international1
    expected = ser_formatted1
    result = polars_clean_numbers(X)
    test.assertTrue(result.equals(expected, null_equal=True))
    pass


def tests_polars_clean_numbers_AMBIVALENT_CASES_RESOLVABLE(
    # fixtures
    test: TestCase,
):
    X = pl.Series(["8.45", "8,45", "8,456.1"])
    expected = pl.Series(["8.45", "8.45", "8456.1"])
    result = polars_clean_numbers(X)
    test.assertTrue(result.equals(expected, null_equal=True))

    X = pl.Series(["8.456", "8,456", "8,456.1"])
    expected = pl.Series(["8.456", "8456", "8456.1"])
    result = polars_clean_numbers(X)
    test.assertTrue(result.equals(expected, null_equal=True))
    pass


def tests_polars_clean_numbers_AMBIVALENT_CASES_UNRESOLVABLE(
    # fixtures
    test: TestCase,
):
    X = pl.Series(["8.456", "8,456", "8,456.1", "3.000.100,2"])
    with assert_raises(Exception, match=r".*\bambivalent\b.*"):
        polars_clean_numbers(X)

    with assert_not_raises():
        result = polars_clean_numbers(X, ambivalences="std")

    expected = pl.Series(["8.456", "8456", "8456.1", "3000100.2"])
    test.assertTrue(result.equals(expected, null_equal=True))

    with assert_not_raises():
        result = polars_clean_numbers(X, ambivalences="non-std")

    expected = pl.Series(["8456", "8.456", "8456.1", "3000100.2"])
    test.assertTrue(result.equals(expected, null_equal=True))
    pass


def test_polars_fuzzy_rounding(
    # fixtures
    test: TestCase,
    ser_numbers2: pl.Series,
    ser_formatted2: pl.Series,
):
    X = ser_numbers2
    expected = ser_formatted2
    result = polars_fuzzy_rounding(X, n=5)
    test.assertTrue(result.equals(expected, null_equal=True))
    return
