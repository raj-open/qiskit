#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations;

from src.thirdparty.code import *;
from src.thirdparty.config import *;
from src.thirdparty.maths import *;
from src.thirdparty.system import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'set_rng_seed',
    'get_rng_seed',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_SEED: int = 1234;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def set_rng_seed():
    '''
    Seeds random number generator via value of `SEED` argument in .env file.
    '''
    global _SEED;
    try:
        load_dotenv(dotenv_path='.' or os.getcwd());
        env = dotenv_values('.env');
        seed = int(env.get('SEED') or '1234');
        np.random.seed(seed);
        random.seed(seed);
    except:
        seed = 1234;
        np.random.seed(seed);
        random.seed(seed);
    _SEED = seed;
    return;

def get_rng_seed() -> int:
    return _SEED;
