#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.code import *;
from src.thirdparty.io import *;
from src.thirdparty.types import *;

from src.parsers.dimacs_cnf import *;
from src.algorithms.boolsat.sat_problem import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'read_problem_sat_from_dimacs_cnf',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHOD - read SAT problem from dimacs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def read_problem_sat_from_dimacs_cnf(
    name: str,
    path: Optional[str] = None,
    problem_text: Optional[str] = None,
):
    '''
    NOTE: A cnf file encodes 0th order logic propositions in conjunctive normal form
    (CNF - conjunction of disjunctions of literals).

    The DIMACS CNF format obeys the following standards:

    - lines beginning with `c` are comments
    - the head of the table is of the form `p cnf <integer> <integer>`.
        - Let `m, n` be these respective integers.
        - `m` = number of boolean variables
        - `n` = number of conjuncts (basic clauses for CNF)
        - we can ignored these values.
    - all further rows are of the format
        ```
        <integer> <integer> ... <integer> 0

        or

        <integer> <integer> ... <integer>
        <integer> <integer> ... <integer>
        ...
        <integer> <integer> ... <integer> 0
        ```

        - The integers are in ℤ \ {0} and indicate the index of the literals.
        - A negative sign is use to indicate negative literals.
        - Let `(-)i1 (-)i2 ... (-)ik 0` be row `j`.
        - The clause `C_j` is then

            ```
            C_j = (¬)A_i1 ⋁ (¬)A_i2 ⋁ ... ⋁ (¬)A_ik
            ```

        - If `b = 0` this

    ```text
    c  simple_v3_c2.cnf
    c
    p cnf 3 2
    1 -3 0
    2 3 -1 0
    ```

    cf. <https://people.sc.fsu.edu/~jburkardt/data/cnf/cnf.html>
    '''
    if path is not None:
        problem_text = read_file(path=path);
    assert problem_text is not None, 'Either a path to a text file or text must be provided!';
    clauses = parse_text_as_dimacs_cnf(problem_text);
    problem = ProblemSAT(name=name, clauses=clauses);
    problem.setup();
    return problem;
