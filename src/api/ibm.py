#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations;

from src.thirdparty.code import *;
from src.thirdparty.config import *;
from src.thirdparty.quantum import *;
from src.thirdparty.system import *;
from src.thirdparty.render import *;
from src.thirdparty.types import *;

from src.core.env import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'get_ibm_account',
    'CreateBackend',
    'connect_to_backend',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS / LOCAL VARIABLES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# local usage only
_provider: Optional[QkAccountProvider] = None;
T = TypeVar('T');

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS: connection
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_ibm_account(force_reload: bool = False) -> QkAccountProvider:
    '''
    Connects to IBM Lab session.

    NOTE:
    - Requires .env file in root folder of project with TOKEN entry.
    - use `force_reload=True` to reload credentials. Otherwise only reloads credentials if current ones do not work.
    '''
    global _provider;
    if force_reload:
        _provider = connect_to_ibm_account_force_reload();
    if _provider is None:
        try:
            _provider = IBMQ.load_account();
        except:
            _provider = connect_to_ibm_account_force_reload();
    return _provider;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS: backend
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CreateBackend(QkBackend):
    '''
    Creates connection to IBM `qiskit` backend.

    @inputs
    - `n`            - <integer> default=1; Number of qubits required (only relevant for cloud computations).
    - `kind`         - enum<BACKEND | BACKEND_SIMULATOR>; choice of simulator/backend.
    - `force_reload` - <boolean> default=false; Whether to force reload IBM account. Only relevant for cloud computations.

    NOTE: to be used with `with`-blocks.
    '''

    nr_qubits: int;
    kind: BACKEND | BACKEND_SIMULATOR;
    provider: Optional[QkAccountProvider];

    def __init__(
        self,
        kind: BACKEND | BACKEND_SIMULATOR,
        n: int  = 1,
        force_reload: bool = False
    ):
        self.kind = kind;
        self.nr_qubits = n;
        self.provider = None;
        if isinstance(kind, BACKEND):
            self.provider = get_ibm_account(force_reload=force_reload);
        return;

    def __enter__(self) -> tuple[BACKEND | BACKEND_SIMULATOR, Optional[QkBackend]]:
        kind = self.kind;
        if isinstance(self.kind, BACKEND_SIMULATOR):
            be = QkBackendAer.get_backend(kind.value);
        elif kind == BACKEND.LEAST_BUSY:
            def filt(x: IBMQSimulator) -> bool:
                return x.configuration().n_qubits >= self.nr_qubits \
                    and x.configuration().simulator == False \
                    and x.status().operational == True;
            be = ibmq.least_busy(backends=self.provider.backends(filters=filt));
            kind = backend_from_name(name=str(be))
            return kind, be;
        else:
            try:
                be = self.provider.get_backend(kind.value);
            except:
                be = None;
        return kind, be;

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # NOTE: At the moment does nothing. This may change depending upon IBM's implementation.
        return;

# decorator
def connect_to_backend(
    kind: BACKEND | BACKEND_SIMULATOR,
    n: int  = 1,
    force_reload: bool = False
) -> Callable[[Callable[[BACKEND | BACKEND_SIMULATOR, QkBackend], T]], Callable[[], Optional[T]]]:
    '''
    Decorator to ease connection to IBM backend.
    '''
    def dec(
        action: Callable[[BACKEND | BACKEND_SIMULATOR, QkBackend], T]
    ) -> Callable[[], Optional[T]]:
        be = CreateBackend(kind=kind, n=n, force_reload=force_reload);
        @wraps(action)
        def wrapped_action() -> Optional[T]:
            with be as (kind, backend):
                if backend is None:
                    return None;
                return action(kind, backend);
        return wrapped_action;
    return dec;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def connect_to_ibm_account_force_reload() -> QkAccountProvider:
    '''
    Connects to IBM Lab session with force reload of credentials.
    '''
    load_dotenv(dotenv_path='.' or os.getcwd());
    env = dotenv_values('.env');
    token = env.get('TOKEN');
    hub = env.get('HUB');
    group = env.get('GROUP');
    project = env.get('PROJECT');
    url = env.get('URL');
    # IBMQ.enable_account(token, url);
    IBMQ.save_account(
        token      = token,
        hub        = hub,
        group      = group,
        project    = project,
        url        = url,
        overwrite  = True,
    );
    provider = IBMQ.load_account();
    return provider;
