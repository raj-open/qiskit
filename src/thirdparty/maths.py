#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from fractions import Fraction;
import math;
import numpy as np;
from numpy import pi;
import random;
from typing import TypeVar;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODIFICATIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# local usage only
T = TypeVar('T');

def sample(
    X: list[T],
    size: int = 1,
    replace: bool = True,
) -> list[T]:
    '''
    @inputs
    - `X` - a list
    - `size` <int> - desired sample size
    - `replace` <bool> - optional replacement

    @returns a sample from an uniformly distributed set.
    '''
    return np.random.choice(X, size=size, replace=replace).tolist();

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'Fraction',
    'math',
    'np',
    'pi',
    'random',
    'sample',
];
