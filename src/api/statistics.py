#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations;

from src.thirdparty.code import *;
from src.thirdparty.config import *;
from src.thirdparty.misc import *;
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

def get_counts(
    result: QkResult,
    *bits: list[int],
    pad: bool = False,
) -> tuple[
    int,
    dict[str, int],
    list[dict[str, int]],
]:
    '''
    Returns statistics of job results.
    '''
    counts_raw = result.get_counts();
    counts: dict[str, int] = {};
    if isinstance(counts_raw, list):
        if len(counts_raw) > 0:
            keys = counts_raw[0].keys();
            counts = {
                key: sum([count.get(key, 0) for count in counts_raw])
                for key in keys
            };
    else:
        counts = counts_raw;
    # NOTE: Qiskit places spaces in key to signify different blocks of registered cbits. Remove these here:
    counts = {
        re.sub(pattern=r'\s+', repl='', string=key): value
        for key, value in counts.items()
    };
    # NOTE: qiskit orders the measured bits from buttom to top, so reverse this.
    if pad:
        n = get_key_length(counts);
        keys = binary_sequences(n);
        counts = { key: counts.get(key[::-1], 0) for key in keys };
    else:
        counts = { key[::-1]: value for key, value in counts.items() };
    tot = sum(counts.values());
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
    return tot, counts, statistic;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_key_length(X: dict[str, Any]):
    for key in X.keys():
        return len(key);
    return 0;

def match_subkey(key_long: str, key: str, C: list[int]) -> bool:
    return all(
        key_long[index] == a
        for index, a in zip(C, key)
    );
