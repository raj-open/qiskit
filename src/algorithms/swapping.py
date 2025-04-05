#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.maths import *
from src.thirdparty.quantum import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    "KET_MINUS",
    "KET_ONE",
    "KET_PLUS",
    "KET_ZERO",
    "ket_bra",
    "ket_ket",
    "swapping",
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

KET_ZERO = np.asarray([1, 0])
KET_ONE = np.asarray([0, 1])
KET_PLUS = np.asarray([1 / sqrt(2), 1 / sqrt(2)])
KET_MINUS = np.asarray([1 / sqrt(2), -1 / sqrt(2)])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def swapping(a1, b1, a2, b2):
    """
    0123

    (a1|00⟩ + b1|11⟩)(a2|00⟩ + b2|11⟩)
    = a1·a2·|0000⟩ + a1·b2·|0011⟩ + a2·b1·|1100⟩ + b1·b2·|1111⟩

    ~~> CNOT 1->2
    a1·a2·|0000⟩ + a1·b2·|0011⟩ + a2·b1·|1110⟩ + b1·b2·|1101⟩

    ~~> H1
    a1·a2·|0+00⟩ + a1·b2·|0+11⟩ + a2·b1·|1-10⟩ + b1·b2·|1-01⟩
    = 1/√2·(
        a1·a2·|0000⟩ + a1·b2·|0011⟩ + a2·b1·|1010⟩ + b1·b2·|1001⟩
      + a1·a2·|0100⟩ + a1·b2·|0111⟩ - a2·b1·|1110⟩ - b1·b2·|1101⟩
      )
    = 1/√2·(
        a1·a2·|0000⟩ + a1·b2·|0011⟩ + a1·a2·|0100⟩ + a1·b2·|0111⟩
      + b1·b2·|1001⟩ + a2·b1·|1010⟩ - b1·b2·|1101⟩ - a2·b1·|1110⟩
      )

    ~~> M12
    1/√2·twist(
         |00⟩ ⊗ (a1·a2·|00⟩ + b1·b2·|11⟩)
         |01⟩ ⊗ (a1·b2·|01⟩ + a2·b1·|10⟩)
         |10⟩ ⊗ (a1·a2·|00⟩ - b1·b2·|11⟩)
         |11⟩ ⊗ (a1·b2·|01⟩ - a2·b1·|10⟩)
    )
    = 1/√2·twist(
         |00⟩ ⊗ Z1⁰ X2⁰ (a1·a2·|00⟩ + b1·b2·|11⟩)
         |01⟩ ⊗ Z1⁰ X2¹ (a1·b2·|00⟩ + a2·b1·|11⟩)
         |10⟩ ⊗ Z1¹ X2⁰ (a1·a2·|00⟩ + b1·b2·|11⟩)
         |11⟩ ⊗ Z1¹ X2¹ (a1·b2·|00⟩ + a2·b1·|11⟩)
    )
    """
    c1, d1 = a1 * a2 / sqrt(2), b1 * b2 / sqrt(2)
    c2, d2 = a1 * b2 / sqrt(2), a2 * b1 / sqrt(2)
    p1 = c1**2 + d1**2
    p2 = c2**2 + d2**2
    c1, d1 = c1 / p1, d1 / p1
    c2, d2 = c2 / p2, d2 / p2
    return {
        "00": ("00", "11", c1, d1, p1),
        "01": ("01", "10", c2, d2, p2),
        "10": ("00", "11", c1, -d1, p1),
        "11": ("01", "10", c2, -d2, p2),
    }


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def flatten_vector(u: np.ndarray) -> np.ndarray:
    return u.flatten()


def tensorise_vector(u: np.ndarray) -> np.ndarray:
    return u.reshape((2, 2))


def ket_ket(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    w = np.asarray(
        [
            u[0] * v[0],
            u[0] * v[1],
            u[1] * v[0],
            u[1] * v[1],
        ]
    )
    return w


def ket_bra(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    return tensorise_vector(ket_ket(u, v))


def matrify(u: np.ndarray) -> np.ndarray:
    """
    rho = ∑ ⟨i ⊗ j|u⟩  |j⟩⟨i|
    d. h. rho[j, i] = u[i, j]
    d. h. rho = u.T
    """
    u = tensorise_vector(u)
    rho = u.T
    return rho


def unmatrify(rho: np.ndarray) -> np.ndarray:
    u = rho.T
    u = flatten_vector(u)
    return u
