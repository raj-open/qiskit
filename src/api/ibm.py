#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations;

from src.thirdparty.code import *;
from src.thirdparty.config import *;
from src.thirdparty.misc import *;
from src.thirdparty.quantum import *;
from src.thirdparty.render import *;
from src.thirdparty.system import *;
from src.thirdparty.types import *;

from src.core.env import *;
from src.api.latest import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'get_ibm_account',
    'CreateBackend',
    'connect_to_backend',
    'display_backends',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS / LOCAL VARIABLES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# local usage only
_provider: Optional[QkAccountProvider] = None;
T = TypeVar('T');
ARGS = ParamSpec('ARGS');

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
    - `option`       - enum<BACKEND | BACKEND_SIMULATOR>; choice of simulator/backend.
    - `force_reload` - <boolean> default=false; Whether to force reload IBM account. Only relevant for cloud computations.

    NOTE: to be used with `with`-blocks.
    '''

    nr_qubits: int;
    option: BACKEND | BACKEND_SIMULATOR;
    provider: Optional[QkAccountProvider];

    def __init__(
        self,
        option: BACKEND | BACKEND_SIMULATOR,
        n: int  = 1,
        force_reload: bool = False
    ):
        self.option = option;
        self.nr_qubits = n;
        self.provider = None;
        if isinstance(option, BACKEND):
            self.provider = get_ibm_account(force_reload=force_reload);
        return;

    def __enter__(self) -> tuple[BACKEND | BACKEND_SIMULATOR, Optional[QkBackend]]:
        option = self.option;
        if isinstance(option, BACKEND_SIMULATOR):
            be = QkBackendAer.get_backend(option.value);
            latest_state.set_backend(option=option, queue=False);
        elif option == BACKEND.LEAST_BUSY:
            def filt(x: IBMQSimulator) -> bool:
                return x.configuration().n_qubits >= self.nr_qubits \
                    and x.configuration().simulator == False \
                    and x.status().operational == True;
            be = ibmq.least_busy(backends=self.provider.backends(filters=filt));
            option = backend_from_name(name=str(be))
            latest_state.set_backend(option=option, queue=True);
        else:
            try:
                be = self.provider.get_backend(option.value);
                latest_state.set_backend(option=option, queue=True);
            except:
                be = None;
                latest_state.set_backend(option=None, queue=True);
        return option, be;

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # NOTE: At the moment does nothing. This may change depending upon IBM's implementation.
        return;

# decorator
def connect_to_backend(
    option: BACKEND | BACKEND_SIMULATOR,
    n: int  = 1,
    force_reload: bool = False
) -> Callable[[Callable[Concatenate[BACKEND | BACKEND_SIMULATOR, QkBackend, ARGS], T]], Callable[ARGS, Optional[T]]]:
    '''
    Decorator to ease connection to IBM backend.
    '''
    def dec(
        action: Callable[Concatenate[BACKEND | BACKEND_SIMULATOR, QkBackend, ARGS], T]
    ) -> Callable[ARGS, Optional[T]]:
        be = CreateBackend(option=option, n=n, force_reload=force_reload);
        @wraps(action)
        def wrapped_action(**kwargs) -> Optional[T]:
            with be as (option, backend):
                if backend is None:
                    return;
                return action(option, backend, **kwargs);
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
        warnings   = False,
    );
    provider = IBMQ.load_account();
    return provider;

def display_backends():
    provider = get_ibm_account(force_reload=False);
    backends = provider.backends();
    names_simulator = [str(be) for be in backends if isinstance(be, IBMQSimulator)];
    names_queue = [str(be) for be in backends if isinstance(be, IBMQBackend) and not isinstance(be, IBMQSimulator)];
    items_simulator = '\n'.join([ f'<li>{item}</li>' for item in names_simulator]);
    items_queue = '\n'.join([ f'<li>{item}</li>' for item in names_queue]);
    display(HTML(
        dedent(
            '''
            <b>AVAILABLE BACKENDS (SIMULATOR):</b>
            <ul>
            {items_simulator}
            </ul>
            </br>
            <b>AVAILABLE BACKENDS (QUEUE):</b>
            <ul>
            {items_queue}
            </ul>
            '''
        ).format(
            items_simulator = items_simulator,
            items_queue = items_queue,
        )
    ));
    return;
