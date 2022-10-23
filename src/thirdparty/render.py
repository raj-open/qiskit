#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from IPython.display import Latex;
from IPython.display import display_latex;
from IPython.display import display_png;
from IPython.display import display_markdown;
from IPython.display import display;
import ipywidgets as widgets;
# from array_to_latex import to_ltx as array_to_latex; # <- has issues
from qiskit.visualization import array_to_latex;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'array_to_latex',
    'display_latex',
    'display_markdown',
    'display_png',
    'display',
    'Latex',
    'widgets',
];
