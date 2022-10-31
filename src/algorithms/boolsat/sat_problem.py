#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.code import *;
from src.thirdparty.types import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'ProblemSAT',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dataclass
class ProblemSAT():
    name: str = field(default='SAT problem');
    clauses: list[list[tuple[Literal[-1]|Literal[1], int]]] = field(default_factory=list);

    variables: list[int] = field(init=False);
    variable_range: int = field(init=False);
    number_of_variables: int = field(init=False);
    number_of_clauses: int = field(init=False);

    def setup(self):
        # extract basic information about variables and clauses:
        variables = set();
        for clause in self.clauses:
            variables = variables.union([index for sgn, index in clause]);
        self.variables = sorted(list(variables), reverse=False);
        # there may be redundancies:
        self.number_of_variables = len(self.variables);
        self.number_of_clauses = len(self.clauses);
        pass;

    def map_solution_to_literals(self, solution: list[bool]) -> dict[str, bool]:
        '''
        Converts a solution to the SAT-problem in terms of the named atoms in the problem.

        NOTE: If a solution does not cover an atom, then atom is set to false.
        '''
        return {
            index: False for index in self.variables
        } | {
            index: value
            for index, value in zip(self.variables, solution)
        };

    def verify(self, solution: list[bool]) -> bool:
        '''
        Verifies a solution to the SAT-problem.

        NOTE: If a solution does not cover an atom, then atom is set to false.
        '''
        soln = self.map_solution_to_literals(solution);
        return all(
            any(
                (sgn == 1 and soln[index]) or (sgn == -1 and not soln[index])
                for sgn, index in clause
            )
            for clause in self.clauses
        );
