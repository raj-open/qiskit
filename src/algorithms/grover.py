#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.maths import *;
from src.thirdparty.quantum import *;

from src.models.boolsat import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'grover_algorithm_from_sat',
    'grover_iterator_from_sat',
    'grover_iterate',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def grover_algorithm_from_sat(
    problem: ProblemSAT,
    prob: float = 0,
    verbose: bool = False,
) -> QuantumCircuit:
    '''
    Constructs a Quantum-Circuit for Grover's Algorithm.

    @inputs
    - `problem` - an instance of the SAT problem.
    - `prob` - <float> proportion (if known) of solutions which fulfil problem.
    - `verbose` - <bool>, whether or not to display feedback.
    '''
    n = problem.number_of_variables;
    Nc = problem.number_of_clauses;
    final = n + Nc;

    # comput optimal number of iterations:
    r = heuristic_optimal_rounds(n=n, prob=prob);
    if verbose:
        print(f'{n} qubits, r={r} rounds');
    # compute Grover iterate:
    oracle = oracle_cnf(n=n, clauses=problem.clauses);
    grit = grover_iterate(oracle=oracle, num_ancilla=Nc+1);
    grit = grit.decompose();

    # define circuit shape
    circuit = QuantumCircuit(
        QuantumRegister(n, 'q'),
        QuantumRegister(Nc, 'a'),
        QuantumRegister(1, 'final'),
        ClassicalRegister(n, 'c'),
        ClassicalRegister(1, 'answer'),
    );

    # compose circuit:

    # set answer bit to |-⟩ so that oracle functions like phase oracle:
    circuit.x(final);
    circuit.h(final);

    # main part of grover algorithm:
    circuit.barrier();
    circuit.h(range(n));
    for r in range(r):
        circuit.append(grit, range(n + Nc + 1), []);
    circuit.barrier();

    # add measurement gates:
    circuit.measure(range(n), range(n));
    circuit.measure(final, n);

    return circuit;

def grover_iterator_from_sat(
    problem: ProblemSAT,
) -> QuantumCircuit:
    n = problem.number_of_variables;
    Nc = problem.number_of_clauses;
    oracle = oracle_cnf(n=n, clauses=problem.clauses);
    grit = grover_iterate(oracle=oracle, num_ancilla=Nc+1);
    return grit;

def grover_iterate(
    oracle: QuantumCircuit,
    num_ancilla: int = 0,
) -> QuantumCircuit:
    '''
    Constructs the Grover Iterate (cf. [§8.1, Kaye (2007)]).

    Steps:
    - apply oracle
    - apply the n-qubit Hadamard gate H.
    - apply U_{0^⊥} .
    - apply the n-qubit Hadamard gate H.
    '''
    n = oracle.num_qubits - num_ancilla;
    U = -np.eye(2**n);
    U[0, 0] = 1;

    circuit = oracle.copy();
    circuit.name = 'Grover-Iterate';
    circuit.h(range(n));
    circuit.unitary(QkOperator(U), range(n));
    circuit.h(range(n));
    return circuit;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS - HEURISTICS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def heuristic_optimal_rounds(
    n: int,
    m: int = 1,
    prob: float = 0,
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
    prob = m / 2**n if prob <= 0 else prob;
    u = np.sqrt(prob);
    theta = np.arcsin(u);
    r = int(round(pi/(4*theta) - 1/2));
    return r;
