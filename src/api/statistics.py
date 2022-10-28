#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations;

from src.thirdparty.code import *;
from src.thirdparty.config import *;
from src.thirdparty.quantum import *;
from src.thirdparty.system import *;
from src.thirdparty.types import *;

from src.core.utils import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'get_counts',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_counts(result: QkResult, *bits: list[int]) -> tuple[dict[str, int], list[dict[str, int]]]:
    '''
    Returns statistics of job results.
    '''
    counts_raw = result.get_counts();
    counts = {};
    if isinstance(counts_raw, list):
        if len(counts_raw) > 0:
            keys = counts_raw[0].keys();
            counts = {
                key: sum([count.get(key, 0) for count in counts_raw])
                for key in keys
            };
    else:
        counts = counts_raw;
    # NOTE: qiskit orders the measured bits from buttom to top, so reverse this.
    counts = { key[::-1]: value for key, value in counts.items() };
    statistic = [
        {
            key: sum([
                value
                for key_long, value in counts.items()
                if match_subkey(key_long, key, C)
            ])
            for key in binary_sequences(len(C))
        }
        for C in bits
    ];
    return counts, statistic;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def match_subkey(key_long: str, key: str, C: list[int]) -> bool:
    return all(
        key_long[index] == a
        for index, a in zip(C, key)
    );
