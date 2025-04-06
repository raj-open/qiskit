#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from asyncio import new_event_loop as asyncio_new_event_loop
from functools import wraps
from typing import Awaitable
from typing import Callable
from typing import ParamSpec
from typing import TypeVar

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "make_synchronous",
]

# ----------------------------------------------------------------
# LOCAL CONSTANTS
# ----------------------------------------------------------------

RETURN = TypeVar("RETURN")
PARAMS = ParamSpec("PARAMS")

# ----------------------------------------------------------------
# METHDOS
# ----------------------------------------------------------------


def make_synchronous():
    """
    Decorates an asynch method, making it into a synchronous task
    """

    def dec(method: Callable[PARAMS, Awaitable[RETURN]]) -> Callable[PARAMS, RETURN]:
        @wraps(method)
        def wrapped_method(
            *_: PARAMS.args,
            **__: PARAMS.kwargs,
        ) -> RETURN:
            # run the async tasks
            loop = asyncio_new_event_loop()
            try:
                loop.run_until_complete(method(*_, **__))
            finally:
                loop.close()
            return

        return wrapped_method

    return dec
