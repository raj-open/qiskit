#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from typing import Any

from tests.unit.thirdparty.unit import *

from src._core.utils.basic import *

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


@mark.parametrize(
    ("text", "args", "kwargs", "expected"),
    [
        (
            r"hello {} {food} {time}",
            ("bob",),
            {"time": 10.18, "pet": "cat", "food": "chicken"},
            r"hello bob chicken 10.18",
        ),
        (
            r"hello {} {food} {time}",
            (),
            {
                "time": 10.18,
                "pet": "cat",
            },
            r"hello {} {food} 10.18",
        ),
        (
            r"hello {0} {food} {time}",
            (),
            {
                "time": 10.18,
                "pet": "cat",
            },
            r"hello {0} {food} 10.18",
        ),
        (
            r"hello {0} {4} {food} {time}",
            (),
            {
                "time": 10.18,
                "pet": "cat",
            },
            r"hello {0} {4} {food} 10.18",
        ),
        (
            r"hello {food} {time} {0} {4}",
            (),
            {
                "time": 10.18,
                "pet": "cat",
            },
            r"hello {food} 10.18 {0} {4}",
        ),
        (
            r"hello {food} {time} {3} {9}",
            (),
            {
                "time": 10.18,
                "pet": "cat",
            },
            r"hello {food} 10.18 {3} {9}",
        ),
    ],
)
def test_safe_format_string_CASES(
    # fixtures
    test: TestCase,
    # parameters
    text: str,
    args: tuple,
    kwargs: dict[str, Any],
    expected: str,
):
    result = safe_format_string(text, *args, **kwargs)
    test.assertEqual(result, expected)


@mark.parametrize(
    ("X", "expected"),
    [
        (
            [[0, 1], ["a"]],
            [0, 1, "a"],
        ),
        (
            [[0, 1], [0, 1]],
            [0, 1, 0, 1],
        ),
        (
            [[0, 1], ["a"], ["bc", 4]],
            [0, 1, "a", "bc", 4],
        ),
    ],
)
def test_flatten_CASES(
    test: TestCase,
    # parameters
    X: list,
    expected: list[list],
):
    result = flatten(X)
    test.assertEqual(result, expected)


@mark.parametrize(
    ("X", "expected"),
    [
        (
            [],
            [],
        ),
        (
            [[]],
            [],
        ),
        (
            [[0]],
            [0],
        ),
    ],
)
def test_flatten_EDGE_CASES(
    test: TestCase,
    # parameters
    X: list,
    expected: list[list],
):
    result = flatten(X)
    test.assertEqual(result, expected)


@mark.parametrize(
    ("X", "expected"),
    [
        (
            [[0, 1], [0]],
            [0, 1, 0],
        ),
        (
            [[0, 1], [[0]]],
            [0, 1, [0]],
        ),
        (
            [[0, 1, [2]], [[0], 3]],
            [0, 1, [2], [0], 3],
        ),
    ],
)
def test_flatten_NESTING(
    test: TestCase,
    # parameters
    X: list,
    expected: list[list],
):
    result = flatten(X)
    test.assertEqual(result, expected)
