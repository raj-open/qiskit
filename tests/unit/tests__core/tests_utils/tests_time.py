#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from datetime import datetime

from tests.unit.thirdparty.unit import *

from src._core.utils.time import *

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


@mark.parametrize(
    (
        "t",
        "t_expected",
    ),
    [
        (
            datetime.fromisoformat("2032-10-04 22:38:05"),
            datetime.fromisoformat("2032-10-04 22:38:05"),
        ),
        (
            datetime.fromisoformat("2032-10-04 22:38:05+09:00"),
            datetime.fromisoformat("2032-10-04 13:38:05"),
        ),
        (
            datetime.fromisoformat("2032-10-04 13:38:05-09:00"),
            datetime.fromisoformat("2032-10-04 22:38:05"),
        ),
    ],
)
def test_remove_timezone_SAME_DAY(
    test: TestCase,
    # parameters
    t: datetime | None,
    t_expected: datetime | None,
):
    print(t)
    result = remove_timezone(t)
    test.assertEqual(result, t_expected)


@mark.parametrize(
    (
        "t",
        "t_expected",
    ),
    [
        (
            datetime.fromisoformat("2032-10-05 03:38:05+09:00"),
            datetime.fromisoformat("2032-10-04 18:38:05"),
        ),
        (
            datetime.fromisoformat("2032-10-04 18:38:05-09:00"),
            datetime.fromisoformat("2032-10-05 03:38:05"),
        ),
    ],
)
def test_remove_timezone_DIFFERENT_DAY(
    test: TestCase,
    # parameters
    t: datetime | None,
    t_expected: datetime | None,
):
    result = remove_timezone(t)
    test.assertEqual(result, t_expected)


def test_remove_timezone_EDGE_CASE(
    test: TestCase,
):
    result = remove_timezone(None)
    test.assertIsNone(result)


@mark.parametrize(
    (
        "t",
        "t_expected",
    ),
    [
        (
            datetime.fromisoformat("2032-10-04 22:38:05"),
            datetime.fromisoformat("2032-10-04 22:38:05+00:00"),
        ),
        (
            datetime.fromisoformat("2032-10-04 22:38:05+09:00"),
            datetime.fromisoformat("2032-10-04 13:38:05+00:00"),
        ),
        (
            datetime.fromisoformat("2032-10-04 13:38:05-09:00"),
            datetime.fromisoformat("2032-10-04 22:38:05+00:00"),
        ),
    ],
)
def test_add_timezone_SAME_DAY(
    test: TestCase,
    # parameters
    t: datetime | None,
    t_expected: datetime | None,
):
    result = add_timezone(t)
    test.assertEqual(result, t_expected)


@mark.parametrize(
    (
        "t",
        "t_expected",
    ),
    [
        (
            datetime.fromisoformat("2032-10-05 03:38:05+09:00"),
            datetime.fromisoformat("2032-10-04 18:38:05+00:00"),
        ),
        (
            datetime.fromisoformat("2032-10-04 18:38:05-09:00"),
            datetime.fromisoformat("2032-10-05 03:38:05+00:00"),
        ),
    ],
)
def test_add_timezone_DIFFERENT_DAY(
    test: TestCase,
    # parameters
    t: datetime | None,
    t_expected: datetime | None,
):
    result = add_timezone(t)
    test.assertEqual(result, t_expected)


def test_add_timezone_EDGE_CASE(
    test: TestCase,
):
    result = add_timezone(None)
    test.assertIsNone(result)
