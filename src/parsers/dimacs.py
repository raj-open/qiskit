#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.logic import *;
from src.thirdparty.misc import *;
from src.thirdparty.types import *;

from src.setup import *;
from src.parsers.methods import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'parse_text_as_dimacs',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_GRAMMAR = GRAMMAR_DIMACS;
_GRAMMAR_NAME = 'DIMACS';

TYPE_LITERAL: TypeAlias = tuple[Literal[0] | Literal[1], int];
TYPE_DISJ: TypeAlias = list[TYPE_LITERAL];
TYPE_CNF: TypeAlias = list[TYPE_DISJ];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN METHODS string -> Expression
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def parse_text_as_dimacs(text: str) -> TYPE_CNF:
    try:
        u = tokenise_input(
            grammar_name = _GRAMMAR_NAME,
            grammar      = _GRAMMAR,
            start_token  = 'start',
            text         = text,
        );
        u = prune_tree(u, recursive=True);
        u = collapse_tree(u, recursive=True);
        return list(parse_problem(u));
    except:
        raise Exception(f'Could not parse text with \x1b[1m{_GRAMMAR_NAME}\x1b[0m.');

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# RECURSIVE PROCESSING OF TOKENS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def parse_problem(u: LarkTree) -> Generator[
    list[tuple[Literal[-1] | Literal[1], int]],
    None,
    None,
]:
    '''
    Parses file in the dimacs format to a SAT problem description.
    '''
    children = sub_expressions(u);
    match u.data:
        case 'start':
            for child in children:
                yield from parse_problem(child)
        case 'comments' | 'comment':
            return;
        case 'instruction':
            # NOTE: the instructions are superfluous
            return;
        case 'clauses':
            for child in children:
                yield from parse_problem(child);
        case 'clause':
            clause = [parse_literal(child) for child in children];
            yield clause;
        case _:
            raise Exception('Could not parse expression!');
    return;

def parse_literal(u: LarkTree) -> TYPE_LITERAL:
    try:
        children = sub_expressions(u);
        # NOTE: indexes are 1-based in text file ---> replace by 0-based
        index = int(lexed_to_string(children[0])) - 1;
    except:
        raise Exception('Could not read index of literal!');
    match u.data:
        case 'positive_literal':
            return (1, index);
        case 'negative_literal':
            return (0, index);
        case _:
            raise Exception('Unexpected literal!');
