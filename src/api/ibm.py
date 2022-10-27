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
from src.thirdparty.types import *;

from src.core.env import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'BACKEND_SIMULATOR',
    'BACKEND',
    'connect_to_ibm_account',
    'CreateBackend',
    'get_past_job',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BACKEND_SIMULATOR(Enum):
    AER = 'aer_simulator';
    QASM = 'qasm_simulator';
    UNITARY = 'unitary_simulator';
    # simulator_statevector
    # simulator_mps
    # simulator_extended_stabilizer
    # simulator_stabilizer

class BACKEND(Enum):
    LEAST_BUSY = -1;
    BELEM = 'ibmq_belem'
    HANOI = 'ibmq_hanoi';
    LIMA = 'ibmq_lima';
    MANILA = 'ibmq_manila';
    MELBOURNE = 'ibmq_melbourne';
    NAIROBI = 'ibm_nairobi';
    OSLO = 'ibm_oslo';
    QUITO = 'ibmq_quito';

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS: connection
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def connect_to_ibm_account(force_reload: bool = False) -> QkAccountProvider:
    '''
    Connects to IBM Lab session.

    NOTE:
    - Requires .env file in root folder of project with TOKEN entry.
    - use `force_reload=True` to reload credentials. Otherwise only reloads credentials if current ones do not work.
    '''
    if force_reload:
        return connect_to_ibm_account_force_reload();
    try:
        return IBMQ.load_account();
    except:
        return connect_to_ibm_account_force_reload();

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS: backend
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CreateBackend(QkBackend):
    def __init__(
        self,
        nr_qubits: int  = 1,
        provider: Optional[QkAccountProvider] = None,
        kind: BACKEND | BACKEND_SIMULATOR = BACKEND.LEAST_BUSY,
    ):
        assert provider is not None or isinstance(kind, BACKEND_SIMULATOR), 'If provider is not set, must use the simulator!';
        self._kind = kind;
        self._nr_qubits = nr_qubits;
        self._provider = provider;
        return;

    def __enter__(self) -> QkBackend:
        kind = self._kind;
        if isinstance(self._kind, BACKEND_SIMULATOR):
            return QkBackendAer.get_backend(kind.value);
        elif kind == BACKEND.LEAST_BUSY:
            def filt(x: IBMQSimulator) -> bool:
                return x.configuration().n_qubits >= self._nr_qubits \
                    and x.configuration().simulator == False \
                    and x.status().operational == True;
            return ibmq.least_busy(
                backends = self._provider.backends(filters=filt),
            );
        return self._provider.get_backend(kind.value);

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS: jobs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_past_job(
    job_index: str,
    provider: QkAccountProvider,
    kind: BACKEND,
) -> IBMQJob:
    with CreateBackend(provider=provider, kind=kind) as backend:
        job = backend.retrieve_job(job_index);
        return job;

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
