#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import re

import pint
from pint import UnitRegistry

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "CustomUnitRegistry",
    "convert_units",
    "get_custom_ureg",
    "pint",
    "print_unit",
    "set_custom_ureg",
]

# ----------------------------------------------------------------
# LOCAL CONSTANTS / VARIABLES
# ----------------------------------------------------------------

# local variable
_ureg = None

PATTERN_BAD_POWER = re.compile(r"([a-zA-Z]+)(\d+)")

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


class CustomUnitRegistry(UnitRegistry):
    def parse_expression(self, text: str, *_, **__):
        """
        Overrides the default parsing to preprocess unit strings.
        """
        text = self.__class__._preprocess_units(text)
        return super().parse_expression(text, *_, **__)

    @staticmethod
    def _preprocess_units(text: str):
        """
        Handle badly written units
        """
        text = re.sub(pattern=PATTERN_BAD_POWER, repl=r"\1^\2", string=text)
        # FIXME: this is a temporary solution that needs to be fixed in the sources
        text = re.sub(pattern=r"\bM\b", repl=r"m", string=text)
        text = re.sub(pattern=r"\b[Mm]M\b", repl=r"mm", string=text)
        text = re.sub(pattern=r"\b[Cc]M\b", repl=r"cm", string=text)
        text = re.sub(pattern=r"\bKg\b", repl=r"kg", string=text)
        return text

    def format_unit(self, unit: str):
        """
        Formats units to replace '**' with ' ^ '.
        """
        return re.sub(pattern=r"\*\*", repl="^", string=f"{unit:~C}")


def get_custom_ureg() -> CustomUnitRegistry:
    global _ureg
    # NOTE: register once, otherwise costs too much time!
    _ureg = _ureg or CustomUnitRegistry()
    return _ureg


def set_custom_ureg(ureg: CustomUnitRegistry, /):
    global _ureg
    _ureg = ureg
    return


def convert_units(unitFrom: str, unitTo: str) -> float:
    ureg = get_custom_ureg()
    cv = ureg.Quantity(1, unitFrom).to(unitTo).magnitude
    return cv


def print_unit(text: str, ascii: bool = True) -> str | None:
    ureg = get_custom_ureg()
    try:
        u = ureg.Unit(text)
        return f"{u:~C}" if ascii else f"{u:~P}"

    except Exception as _:
        return None
