#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations;

from src.thirdparty.code import *;
from src.thirdparty.config import *;
from src.thirdparty.misc import *;
from src.thirdparty.run import *;
from src.thirdparty.types import *;

from src.core.utils import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'CallState',
    'GetState',
    'CallValue',
    'CallError',
    'keep_calm_and_carry_on',
    'run_safely',
    'to_async',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# local usage only
T = TypeVar('T');
V = TypeVar('V');
ARGS = ParamSpec('ARGS');

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Class State for keeping track of results in the course of a computation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dataclass
class CallState(Generic[V]):
    '''
    An auxiliary class which keeps track of the latest state of during calls.
    '''
    tag: Option[str] = field(default=None);
    result: Optional[V] = field(default=None, repr=False);
    timestamp: str = field(default_factory=get_timestamp_string);
    has_action: bool = field(default=False);
    no_action: bool = field(default=False);
    has_error: bool = field(default=False);
    values: list[tuple[bool, dict]] = field(default_factory=list, repr=False);
    errors: list[str] = field(default_factory=list, repr=False);

    def __copy__(self) -> CallState:
        return CallState(**asdict(self));

    def __add__(self, other) -> CallState:
        '''
        Combines states sequentially:
        - takes on latest `timestamp`.
        - takes on lates `value`.
        - takes on `tag` of latest non-null value.
        - takes on latest value of `no_action`
        - `has_action` = `true` <==> at least one action taken,
          unless `no_action` = `true`.
        - `has_error` = `true` <==> at least one error occurred.
        '''
        if isinstance(other, CallState):
            no_action = other.no_action;
            has_action = False if no_action else (self.has_action or other.has_action);
            return CallState(
                tag = other.tag or self.tag,
                value = other.value,
                timestamp = other.timestamp,
                has_action = has_action,
                no_action = no_action,
                has_error = self.has_error or other.has_error,
                values = self.values + other.values,
                errors = self.errors + other.errors,
            );
        raise Exception('Cannot add states!');

    ## NOTE: only need __radd__ for additions of form <other> + <state>
    def __radd__(self, other) -> CallState:
        if other == 0:
            return self.__copy__();
        raise Exception('Cannot add a CallState to the right of a non-zero object!');

    def get_result(self) -> V:
        if self.result is not None:
            return self.result;
        raise Exception('No result set!');

    @property
    def first_data(self) -> dict:
        '''
        Returns data in first value collected or else defaults to empty dictionary.
        '''
        return self.values[0][1] if len(self.values) > 0 else dict();

    @property
    def data(self) -> list[dict]:
        '''
        Returns the data collected.
        '''
        return [ data for _, data in self.values ];

    @property
    def data_log(self) -> list[dict]:
        '''
        Returns the data to be logged.
        '''
        return [ data for log, data in self.values if log == True ];

    @property
    def data_log_json(self) -> list[str]:
        '''
        Returns the data to be logged as json.
        '''
        return list(map(json.dumps, self.data_log));

def GetState(result: Result[CallState, CallState]) -> CallState:
    if isinstance(result, Ok):
        return result.unwrap();
    return result.unwrap_err();

def CallValue(
    tag: str = None,
    result: Optional[V] = None,
    has_action: bool = True,
    no_action: bool = False,
    value: Option[tuple[bool, dict] | list[tuple[bool, dict]]] = Nothing(),
) -> CallState[V]:
    x = [];
    if isinstance(value, Some):
        x = value.unwrap() or [];
        x = x if isinstance(x, list) else [ x ];
    X = CallState(tag=tag, result=result, values=x, has_action=has_action, no_action=no_action, has_error=False);
    return X;

def CallError(
    tag: str = None,
    has_action: bool = True,
    error: Option[str | BaseException | list[str | BaseException]] = Nothing(),
) -> CallState[V]:
    x = [];
    if isinstance(error, Some):
        x = error.unwrap() or [];
        x = x if isinstance(x, list) else [ x ];
        x = list(map(str, x));
    return CallState(tag=tag, errors=x, has_action=has_action, has_error=True);

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHOD keep_calm_and_carry_on - handles chain of promises
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def keep_calm_and_carry_on(*actions: Callable[[], Result[CallState, CallState]]) -> Result[CallState, CallState]:
    '''
    This executes a chain of promises silently accumulating errors along the way,
    then processes the array (tuple) of results at the end.

    NOTE: Assumes that each action only executes safely (i.e. is guaranteed to return a Result[...]).
    '''
    return Result.collect((call_action_passively(action) for action in actions)) \
        .and_then(post_process_results);

def call_action_passively(action: Callable[[], Result[CallState, CallState]]) -> Result[CallState, Nothing]: # pragma: no cover
    '''
    Calls action and transforms result into an Ok-state.

    NOTE: Assumes that action only executes safely (i.e. is guaranteed to return a Result[...]).
    '''
    return action().and_then(Ok).or_else(Ok);

def post_process_results(states: tuple[CallState, ...]) -> Result[CallState, CallState]: # pragma: no cover
    '''
    Looks at the resulting State-object of each perfomed action.
    If any errors occurred, these are combined into a single error and returned.
    Otherwise the last value is returned.

    NOTE: Assumes that there is at least one result.
    '''
    state: CallState = sum(states);
    return Err(state) if state.has_error else Ok(state);

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DECORATOR - forces methods to run safely
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def run_safely(tag: str | None = None, error_message: str | None = None):
    '''
    Creates a decorator for an action to perform it safely.

    @inputs (parameters)
    - `tag` - optional string to aid error tracking.
    - `error_message` - optional string for an error message.

    ### Example usage ###
    ```py
    @run_safely(tag='recognise int', error_message='unrecognise string')
    def action1(x: str) -> Result[int, CallState]:
        return Ok(int(x));

    assert action1('5') == Ok(5);
    result = action1('not a number');
    assert isinstance(result, Err);
    err = result.unwrap_err();
    assert isinstance(err, CallState);
    assert err.tag == 'recognise int';
    assert err.errors == ['unrecognise string'];

    @run_safely('recognise int')
    def action2(x: str) -> Result[int, CallState]:
        return Ok(int(x));

    assert action2('5') == Ok(5);
    result = action2('not a number');
    assert isinstance(result, Err);
    err = result.unwrap_err();
    assert isinstance(err, CallState);
    assert err.tag == 'recognise int';
    assert len(err.errors) == 1;
    ```
    NOTE: in the second example, err.errors is a list containing
    the stringified Exception generated when calling `int('not a number')`.
    '''
    def dec(action: Callable[ARGS, Result[V, CallState]]) -> Callable[ARGS, Result[V, CallState]]:
        '''
        Wraps action with return type Result[..., CallState],
        so that it is performed safely a promise,
        catching any internal exceptions as an Err(...)-component of the Result.
        '''
        @wraps(action)
        def wrapped_action(*_, **__) -> Result[V, CallState]:
            # NOTE: intercept Exceptions first, then flatten:
            return Result.of(lambda: action(*_, **__)) \
                .or_else(
                    lambda err: Err(CallError(
                        tag = tag or action.__name__,
                        error = Some(error_message or err),
                    ))
                ) \
                .flatmap(lambda value: value); # necessary to flatten result.
        return wrapped_action;
    return dec;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DECORATOR - converts to async method
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def to_async(executor: Optional[Any] = None):
    '''
    Creates a decorator for a synchronous function to perform it asynchronously.
    '''
    def dec(routine: Callable[ARGS, T]) -> Callable[Concatenate[AbstractEventLoop, ARGS], Awaitable[T]]:
        '''
        Decoratos a synchronous function to perform it asynchronously.
        '''
        @wraps(routine)
        def wrapped_method(*_: ARGS.args, loop: AbstractEventLoop, **__: ARGS.kwargs) -> T:
            return loop.run_in_executor(
                executor = executor,
                func     = lambda: routine(*_, **__),
            );
        return wrapped_method;
    return dec;
