#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.maths import *;
from src.thirdparty.quantum import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'deutsch_jozsa_algorithm',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def deutsch_jozsa_algorithm(
    n: int,
    oraclenr: int = -1,
    verbose: bool = False,
) -> QuantumCircuit:
    '''
    Constructs a Quantum-Circuit for the Deutsch-Jozsa problem.

    @inputs
    - `n` - <integer>, the number of qbits that the function takes.
    - `oraclenr` - <integer>, the choice of the 'unknown' function.
    - `verbose` - <bool>, whether or not to log feedback.
    '''
    circuit = QuantumCircuit(n + 1, n);

    # Set up the input register:
    for k in range(n):
        circuit.h(k);

    # Set up the output qubit:
    circuit.x(n);
    circuit.h(n);

    # Append black-box oracle gate to circuit:
    if oraclenr == -1:
        oraclenr = np.random.randint(0, 2);

    oracle = deutsch_jozsa_oracle(n=n, oraclenr=oraclenr);
    circuit.append(oracle, range(n + 1));

    # Perform the H-gotes again and measurements
    for k in range(n):
        circuit.h(k)
        circuit.measure(k, k);

    return circuit;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def deutsch_jozsa_oracle(
    n: int,
    oraclenr: int,
) -> QkGate:
    '''
    Constructs the black-box function for the Deutsch-Jozsa problem.

    @inputs
    - `n` - <integer>, the number of qbits that the function takes.
    - `oraclenr` - <integer>, the choice of the 'unknown' function, which determines if the function is balanced or unbalanced.
    '''
    # circuit = QkProblems.dj_problem_oracle(problem=oraclenr, to_gate=True); # gives one out of 4 oracles
    circuit = QuantumCircuit(n + 1);

    match oraclenr:
        case 1:
            output = np.random.randint(0, 2);
            if output == 1:
                circuit.x(n);
        case _:
            for k in range(n):
                circuit.cx(k, n);

    gate = circuit.to_gate();
    gate.name = 'D-J Oracle';
    return gate;
