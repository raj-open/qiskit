#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.maths import *;
from src.thirdparty.quantum import *;
from src.thirdparty.types import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'oracle_cnf',
    'oracle_disjunct',
    'phase_oracle_dnf',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def oracle_cnf(
    n: int,
    clauses: list[list[tuple[Literal[0]|Literal[1],int]]],
) -> QuantumCircuit:
    Nc = len(clauses);
    final = n + Nc;
    circuit = QuantumCircuit(
        QuantumRegister(n, 'q'),
        QuantumRegister(Nc, 'a'),
        QuantumRegister(1, 'final'),
    );
    variables = [ [ index for sgn, index in clause] for clause in clauses ];
    codes = [ tuple( sgn for sgn, index in clause ) for clause in clauses ];
    disjuncts = list(map(oracle_disjunct, codes));
    preprocessing_items = list(zip(range(Nc), variables, disjuncts));

    # encode clauses
    for k, vars, D in preprocessing_items:
        circuit.append(D, vars + [n + k]);
    # conjunction of disjunctions:
    circuit.mcx(list(range(n,n + Nc)), final);
    # undo preprocessing
    for k, vars, D in preprocessing_items[::-1]:
        circuit.append(D, vars + [n + k]);
    return circuit;

def oracle_disjunct(
    code: tuple[Literal[0]|Literal[1]],
) -> QuantumCircuit:
    '''
    NOTE: Assumes that the literals are of a reasonably small size.
    '''
    # NOTE: disjunction of Li = ¬(conjunction of ¬Li):
    n = len(code);
    final = n;
    circuit = QuantumCircuit(n + 1);
    literals_pos = [ index for index, x in enumerate(code) if x == 1 ];
    # equivalent to: negate just literals_neg then negate all.
    if len(literals_pos) > 0:
        circuit.x(literals_pos);
    # store conjunction in ancillary bit
    circuit.mcx(list(range(n)), final)
    circuit.x(range(n + 1));
    return circuit;

# NOTE: This method is only useful if the conjuncts are all encoded in a homogenous manner.
def phase_oracle_dnf(
    n:     int,
    codes: list[tuple[Literal[0]|Literal[1], ...]],
) -> QuantumCircuit:
    '''
    Constructs the phase equivalent oracle for a clause in DNF.
    @inputs
    - `n` - <integer> number of qbits
    - `codes` - <[(0|1, ...)]> list of 'conjunction' of literals.
    '''
    circuit = QuantumCircuit(n, 0);
    circuit.name = 'phase oracle'
    N = 2**n;
    u = np.ones(shape=[2]*n);
    for code in codes:
        code = code[::-1];
        u[code] = -1;
    U = np.diag(u.reshape(N));
    circuit.unitary(QkOperator(U), range(n));
    return circuit;
