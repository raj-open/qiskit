#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from functools import wraps
from typing import Awaitable
from typing import Callable
from typing import Concatenate
from typing import ParamSpec
from typing import TypeVar

from safetywrap import Result

from .countdown import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "add_countdown",
    "add_countdown_async",
]

# ----------------------------------------------------------------
# LOCAL CONSTANTS/VARIABLES
# ----------------------------------------------------------------

PARAMS = ParamSpec("PARAMS")
RETURN = TypeVar("RETURN")

# ----------------------------------------------------------------
# DECORATORS
# ----------------------------------------------------------------


def add_countdown(
    duration: float,
):
    """
    Inserts a countdown class obj to a method

    @args
    - `duration` - duration of countdown in seconds
    """
    countdown = Countdown(duration=duration)

    def dec(
        method: Callable[Concatenate[Countdown, PARAMS], RETURN],
    ) -> Callable[PARAMS, Result[RETURN, BaseException]]:
        @wraps(method)
        def wrapped_action(
            *_: PARAMS.args,
            **__: PARAMS.kwargs,
        ) -> Result[RETURN, BaseException]:
            return method(countdown, *_, **__)

        return wrapped_action

    return dec


def add_countdown_async(
    duration: float,
):
    """
    Inserts a countdown class obj to an async method

    @args
    - `duration` - duration of countdown in seconds
    """
    countdown = Countdown(duration=duration)

    def dec(
        method: Callable[
            Concatenate[Countdown, PARAMS],
            Awaitable[RETURN],
        ],
    ) -> Callable[PARAMS, Awaitable[RETURN]]:
        @wraps(method)
        async def wrapped_action(
            *_: PARAMS.args,
            **__: PARAMS.kwargs,
        ) -> RETURN:
            result = await method(countdown, *_, **__)
            return result

        return wrapped_action

    return dec
