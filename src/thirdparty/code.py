#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from functools import partial;
from functools import reduce;
from functools import wraps;
from dataclasses import Field;
from dataclasses import MISSING;
from dataclasses import asdict;
from dataclasses import dataclass;
from dataclasses import field;
from itertools import chain as itertools_chain;
from itertools import product as itertools_product;
from operator import itemgetter;
from pydantic import BaseModel;
# cf. https://github.com/mplanchard/safetywrap
from safetywrap import Ok;
from safetywrap import Err;
from safetywrap import Nothing;
from safetywrap import Result;
from safetywrap import Option;
from safetywrap import Some;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'partial',
    'reduce',
    'wraps',
    'asdict',
    'dataclass',
    'field',
    'Field',
    'MISSING',
    'itertools_chain',
    'itertools_product',
    'itemgetter',
    'BaseModel',
    'Err',
    'Nothing',
    'Ok',
    'Option',
    'Result',
    'Some',
];
