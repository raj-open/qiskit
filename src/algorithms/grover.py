#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.maths import *;
from src.thirdparty.quantum import *;

from src.core.log import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'grover_algorithm',
    'grover_algorithm_naive',
    'generate_satisfaction_problem',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def grover_algorithm(
    n: int,
    verbose: bool = False,
) -> QuantumCircuit:
    '''
    Constructs a Quantum-Circuit for Grover's Algorithm.

    @inputs
    - `n` - <integer>, length of set.
    - `verbose` - <bool>, whether or not to display feedback.
    '''
    raise Exception('Not yet implemented!');

def grover_algorithm_naive(
    n: int,
    marked: list[int],
    verbose: bool = False,
) -> QuantumCircuit:
    '''
    Constructs a Quantum-Circuit for the naïve version of Grover's Algorithm
    with foreknowledge of the marked elements.

    @inputs
    - `n` - <integer>, length of set.
    - `marked` - list[<integer>], the set of indexes to find.
    - `verbose` - <bool>, whether or not to log feedback.
    '''
    circuit = QuantumCircuit(n, n);
    circuit.h(range(n));

    r = heuristic_optimal_rounds(n=n, m=len(marked));
    if verbose:
        print(f'{n} qubits, basis state {[f"{x:0{n}b}" for x in marked]} marked, r={r} rounds');

    # Add r Grover iterates:
    oracle = phase_oracle(n=n, marked=marked);
    it = grover_iterate(n=n, oracle=oracle);
    for _ in range(r):
        circuit.append(it, range(n));

    # Add measurement gates:
    circuit.measure(range(n), range(n));

    return circuit;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def generate_satisfaction_problem(n: int, size: int = 0) -> list[int]:
    '''
    Generates a subset of bits of length `n`
    which are to be found by a search algorithm.
    '''
    if size <= 0:
        size = np.random.randint(0, 2**n);
    indexes = range(2**n);
    marked = sample(indexes, size=size, replace=False);
    return marked;

def heuristic_optimal_rounds(
    n: int,
    m: int,
):
    '''
    Computes an optimal number of rounds to maximise the
    amplitudes of the good indexes in Grover's Algorithm.
    Based on the theretical result (see [8.1.22, Kaye (2007)]):

        `Gᵏ|ψ⟩ = cos((2k + 1)θ)|ψ_{bad}⟩ + sin((2k + 1)θ)|ψ_{good}⟩`

    for `k ∈ ℕ`, where
    - `|ψ_{bad}⟩` is the part of the state with 'bad' indexes;
    - `|ψ_{good}⟩` is the part of the state with 'good' indexes;
    - `sin(θ)² = m/2ⁿ`, `m` = #'good' indexes;
    - `G` is the Grover iterator.

    From this it follows that a choice of `k = r`
    maximises the amplitudes of the 'good' indexes and minimises
    the amplitudes of the 'bad' indexes,
    where `r ∈ ℕ` is chosen,
    such that `|(2r+1)θ - π/2|` is minimised.
    '''
    u = np.sqrt(m/2**n);
    theta = np.arcsin(u);
    r = round(np.pi/(4*theta) - 1/2);
    return r;

def phase_oracle(
    n: int,
    marked: list[int],
) -> QuantumCircuit:
    '''
    Consider an unkown function `f : {0,1}ⁿ ⟶ {0,1}`
    and the associated unitary it generates:
        `|x⟩|b⟩ ⟼ |x⟩|b ⊕ ƒ(x)⟩`.
    Since `|x⟩(H|0⟩) ⟼ (-1)^f(x)·|x⟩(H|0⟩)`,
    we may take under convenient circumstances the second bit to be an eigenstate.
    We may thus construct from ƒ the diagonal operator `U_f`,
    which performs a Z-transformation on the 'correct' bits,
    and fixes the rest.
    '''
    circuit = QuantumCircuit(n, name='Phase oracle');
    A = np.identity(2**n);
    for index in marked:
        A[index, index] = -1;
    circuit.unitary(QkOperator(A), range(n));
    return circuit;

def grover_iterate(
    n: int,
    oracle: QkGate,
) -> QuantumCircuit:
    '''
    Constructs the Grover Iterate (cf. [§8.1, Kaye (2007)]).

    Steps:
    - apply oracle U_f.
    - apply the n-qubit Hadamard gate H.
    - Applies U_{0^⊥} .
    - Applies the n-qubit Hadamard gate H.
    '''
    circuit = QuantumCircuit(n, name='Grover-Iterate')
    oracle_0 = phase_oracle(n=n, marked=[0]);

    circuit.append(oracle, range(n));
    circuit.h(range(n));
    circuit.append(oracle_0, range(n));
    circuit.h(range(n));
    return circuit;
