#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.code import *;
from src.thirdparty.io import *;
from src.thirdparty.types import *;

from src.parsers.dimacs import *;
from src.models.boolsat import *;

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
) -> ProblemSAT:
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

            ```text
            C_j = (¬)A_i1 ⋁ (¬)A_i2 ⋁ ... ⋁ (¬)A_ik
            ```

    cf. <https://people.sc.fsu.edu/~jburkardt/data/cnf/cnf.html>
    '''
    if path is not None:
        problem_text = read_file(path=path);
    assert problem_text is not None, 'Either a path to a text file or text must be provided!';
    clauses = parse_text_as_dimacs(problem_text);
    problem = ProblemSAT(name=name, clauses=clauses);
    problem.setup();
    return problem;
