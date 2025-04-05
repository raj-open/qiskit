#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from enum import Enum

import ipywidgets as widgets
import matplotlib.pyplot as mplt
from IPython.display import HTML
from IPython.display import Latex
from IPython.display import display
from IPython.display import display_latex
from IPython.display import display_markdown
from IPython.display import display_png
from matplotlib.figure import Axes as mpltAxes
from matplotlib.figure import Figure as mpltFigure

# from array_to_latex import to_ltx as array_to_latex; # <- has issues
from qiskit.visualization import array_to_latex

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODIFICATIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class PRINT_MODE(Enum):
    LATEX = "latex"
    PLAIN = "plain"


class PLOT_VALUES(Enum):
    ABSOLUTE = "absolute"
    POWER = "power"
    LOG_POWER = "log-power"
    ENTROPY = "entropy"
    REAL = "real"
    IMAG = "imag"


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    "HTML",
    "PLOT_VALUES",
    "PRINT_MODE",
    "Latex",
    "array_to_latex",
    "display",
    "display_latex",
    "display_markdown",
    "display_png",
    "mplt",
    "mpltAxes",
    "mpltFigure",
    "widgets",
]
