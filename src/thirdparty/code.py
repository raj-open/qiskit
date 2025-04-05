#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from dataclasses import MISSING
from dataclasses import Field
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from functools import partial
from functools import reduce
from functools import wraps
from itertools import chain as itertools_chain
from itertools import product as itertools_product
from operator import itemgetter
from typing import Callable
from typing import ParamSpec
from typing import TypeVar

from lazy_load import lazy
from pydantic import BaseModel
from safetywrap import Err
from safetywrap import Nothing

# cf. https://github.com/mplanchard/safetywrap
from safetywrap import Ok
from safetywrap import Option
from safetywrap import Result
from safetywrap import Some

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODIFICATIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ARGS = ParamSpec("ARGS")
T = TypeVar("T")


def make_lazy(method: Callable[ARGS, T]) -> Callable[ARGS, T]:
    """
    Decorates a method and makes it return a lazy-load output.
    """

    @wraps(method)
    def wrapped_method(**kwargs) -> T:
        return lazy(partial(method), **kwargs)

    return wrapped_method


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    "MISSING",
    "BaseModel",
    "Err",
    "Field",
    "Nothing",
    "Ok",
    "Option",
    "Result",
    "Some",
    "asdict",
    "dataclass",
    "field",
    "itemgetter",
    "itertools_chain",
    "itertools_product",
    "make_lazy",
    "partial",
    "reduce",
    "wraps",
]
