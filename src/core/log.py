#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.code import *;
from src.thirdparty.io import *;
from src.thirdparty.log import *;
from src.thirdparty.misc import *;
from src.thirdparty.types import *;

from src.core.calls import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'LOG_LEVELS',
    'configure_logging',
    'log_info',
    'log_debug',
    'log_warn',
    'log_error',
    'log_fatal',
    'log_result',
    'log_dev',
    'catch_fatal',
    'prompt_user_input',
    'prompt_secure_user_input',
    'prompt_confirmation',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class LOG_LEVELS(Enum): # pragma: no cover
    INFO  = logging.INFO;
    DEBUG = logging.DEBUG;

# local usage only
_LOGGING_DEBUG_FILE: str = 'logs/debug.log';
T = TypeVar('T');

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def configure_logging(level: LOG_LEVELS): # pragma: no cover
    logging.basicConfig(
        format  = '%(asctime)s [\x1b[1m%(levelname)s\x1b[0m] %(message)s',
        level   = level.value,
        datefmt = r'%Y-%m-%d %H:%M:%S',
    );
    return;

def log_debug(*messages: Any):
    logging.debug(*messages);

def log_info(*messages: Any):
    logging.info(*messages);

def log_warn(*messages: Any):
    logging.warning(*messages);

def log_error(*messages: Any):
    logging.error(*messages);

def log_fatal(*messages: Any):
    logging.fatal(*messages);
    exit(1);

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Special Methods
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Intercept fatal errors
def catch_fatal(method: Callable[[], T]) -> T:
    try:
        return method();
    except Exception as e:
        log_fatal(e);

def log_result(result: Result[CallState, CallState], debug: bool = False):
    '''
    Logs safely encapsulated result of call as either debug/info or error.

    @inputs
    - `result` - the result of the call.
    - `debug = False` (default) - if the result is okay, will be logged as an INFO message.
    - `debug = True` - if the result is okay, will be logged as a DEBUG message.
    '''
    if isinstance(result, Ok):
        value = result.unwrap();
        log_debug(value);
        for x in value.data_log:
            log_info(x);
    else:
        err = result.unwrap_err();
        log_debug(err);
        for e in err.errors:
            log_error(e);
    return;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DEBUG LOGGING FOR DEVELOPMENT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def log_dev(*messages: Any): # pragma: no cover
    with open(_LOGGING_DEBUG_FILE, 'a') as fp:
        print(*messages, file=fp);

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# User Input
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def prompt_user_input(message: str, expectedformat: Callable) -> Optional[str]:
    answer = None;
    while True:
        try:
            answer = input(f'{message}: ');
        ## Capture Meta+C:
        except KeyboardInterrupt:
            print('');
            return None;
        ## Capture Meta+D:
        except EOFError:
            print('');
            return None;
        except:
            continue;
        if expectedformat(answer):
            break;
    return answer;

def prompt_secure_user_input(message: str, expectedformat: Callable) -> Optional[str]:
    answer = None;
    while True:
        try:
            ## TODO: zeige **** ohne Zeilenumbruch an.
            answer = getpass(f'{message}: ', stream=None);
        ## Capture Meta+C:
        except KeyboardInterrupt:
            print('');
            return None;
        ## Capture Meta+D:
        except EOFError:
            print('');
            return None;
        except:
            continue;
        if expectedformat(answer):
            break;
    return answer;

def prompt_confirmation(message: str, default: bool = False) -> bool:
    answer = prompt_user_input(message, lambda x: not not re.match(r'^(y|yes|j|ja|n|no|nein)$', x));
    if isinstance(answer, str):
        return True if re.match(r'^(y|yes|j|ja)$', answer) else False;
    return default;
