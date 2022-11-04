#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from enum import Enum;
from IPython.display import HTML;
from IPython.display import Latex;
from IPython.display import display_latex;
from IPython.display import display_png;
from IPython.display import display_markdown;
from IPython.display import display;
import ipywidgets as widgets;
import matplotlib.pyplot as mplt;
from matplotlib.figure import Figure as mpltFigure;
from matplotlib.figure import Axes as mpltAxes;
# from array_to_latex import to_ltx as array_to_latex; # <- has issues
from qiskit.visualization import array_to_latex;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODIFICATIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class PRINT_MODE(Enum):
    LATEX = 'latex';
    PLAIN = 'plain';

class PLOT_VALUES(Enum):
    ABSOLUTE = 'absolute';
    POWER = 'power';
    LOG_POWER = 'log-power';
    ENTROPY = 'entropy'
    REAL = 'real';
    IMAG = 'imag';

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'array_to_latex',
    'display_latex',
    'display_markdown',
    'display_png',
    'display',
    'HTML',
    'Latex',
    'mplt',
    'mpltAxes',
    'mpltFigure',
    'PLOT_VALUES',
    'PRINT_MODE',
    'widgets',
];
