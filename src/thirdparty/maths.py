#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import math
import random
from fractions import Fraction
from typing import TypeVar

import numpy as np
from numpy import cos
from numpy import pi
from numpy import sin
from numpy import sqrt

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODIFICATIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# local usage only
T = TypeVar("T")


def sample(
    X: list[T],
    size: int = 1,
    replace: bool = True,
) -> list[T]:
    """
    @inputs
    - `X` - a list
    - `size` <int> - desired sample size
    - `replace` <bool> - optional replacement

    @returns a sample from an uniformly distributed set.
    """
    return np.random.choice(X, size=size, replace=replace).tolist()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    "Fraction",
    "cos",
    "math",
    "np",
    "pi",
    "random",
    "sample",
    "sin",
    "sqrt",
]
