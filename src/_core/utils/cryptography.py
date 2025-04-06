#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import hashlib
import random

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "hash_password",
    "random_token",
]

# ----------------------------------------------------------------
# LOCAL CONSTANTS, VARIABLES
# ----------------------------------------------------------------

SYMB = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def random_token(n: int = 8, symb=SYMB):
    """
    Produces a random token of length `n`
    consisting of alphanumeric characters (case sensitive)
    as well as special characters:
    ```text
    -_
    ```
    """
    options = [a for a in symb]
    alpha = random.choices(options, k=n)
    token = "".join(alpha)
    return token


def hash_password(text: str):
    text_bytes = text.encode("utf-8")
    obj = hashlib.sha256(text_bytes)
    hex = obj.hexdigest()
    return hex
