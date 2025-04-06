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
    "concurrence_of_vector",
    "entropy",
    "entropy_of_vector",
    "ket_bra",
    "ket_ket",
    "svd",
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


def svd(u: np.ndarray) -> np.ndarray:
    rho = matrify(u)
    U, s, V = np.linalg.svd(rho)
    """
    rho = U @ diag(s) @ V
    """
    B1 = [V[0, :].flatten(), V[1, :].flatten()]
    B2 = [U[:, 0].flatten(), U[:, 1].flatten()]
    eig = [s[0], s[1]]

    # err = np.linalg(u - l[0]*ket_ket(B1[0], B2[0]) + l[1]*ket_ket(B1[1], B2[1]));
    return B1, B2, eig


def concurrence_of_vector(u: np.ndarray) -> float:
    _, _, eig = svd(u)
    return 2 * eig[0] * eig[1]


def entropy_of_vector(u: np.ndarray) -> float:
    _, _, eig = svd(u)
    return h(eig[0]) + h(eig[1])


def entropy(rho: np.ndarray) -> float:
    rho
    _, p, _ = np.linalg.svd(rho)
    return h(p[0]) + h(p[1])


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def h(t: float) -> float:
    """
    The 'entropy' function
    ```
    h(t) = -t·log(t)
    ```
    where log is computed in base 2
    """
    if t <= 0:
        return 0

    return -t * np.log2(t)


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
