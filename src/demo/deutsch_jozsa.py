#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations;

from src.thirdparty.code import *;
from src.thirdparty.misc import *;
from src.thirdparty.maths import *;
from src.thirdparty.quantum import *;
from src.thirdparty.render import *;
from src.thirdparty.types import *;

from src.api import *;
from src.widgets import *;
from src.algorithms import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'action_display_circuit',
    'action_display_statistics',
    'action_prepare_circuit_and_job',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS / LOCAL VARIABLES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# local usage only
_latest = Latest();

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - ACTIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def action_display_circuit(n: int):
    '''
    Displays the quantum circuit for the Deutsch-Josza algorithm.

    @inputs
    - `n` - <integer> size of input space for function (should be even).
    '''
    print('Quantumcircuit for Deutsch-Josza Algorithm:');
    oraclenr = np.random.randint(0, 2);
    # gate = deutsch_jozsa_oracle(n=n, oraclenr=oraclenr);
    circuit = deutsch_jozsa_algorithm(n=n, oraclenr=oraclenr, verbose=True);
    display(circuit.draw(output=DRAW_MODE.COLOUR.value, cregbundle=False, initial_state=True));
    return;

def action_prepare_circuit_and_job(
    option: BACKEND | BACKEND_SIMULATOR,
    n: int,
    num_shots: int,
):
    '''
    Prepares the quntum circuit and jobs for the Deutsch-Josza algorithm.

    @inputs
    - `backend` - an enum value to indicate which backend to use.
    - `n` - <integer> size of input space for function (should be even).
    - `num_shots` - number of shots of the job prepared.
    '''
    @connect_to_backend(option=option, n=n+1)
    def action(
        option: BACKEND | BACKEND_SIMULATOR,
        backend: QkBackend,
        n: int,
        num_shots: int,
    ):
        simulated = isinstance(option, BACKEND_SIMULATOR);
        _latest.set_backend(option, simulated=simulated);
        print('Quantumcircuit for testing Deutsch-Josza algorithm:');
        circuit = deutsch_jozsa_algorithm(n=n, verbose=True);
        display(circuit.draw(
            output        = DRAW_MODE.COLOUR.value,
            cregbundle    = False,
            initial_state = True,
        ));

        # run job and obtain results:
        # %qiskit_job_watcher
        job = qk_execute(
            experiments = circuit,
            backend = backend,
            shots = num_shots,
            optimization_level = 3,
        );
        _latest.set_job(job, simulated=simulated);

        print(dedent(f'''
        \x1b[1mNOTE:\x1b[0m
        - backend used: \x1b[1m{backend}\x1b[0m
        - job index: \x1b[1m{job.job_id()}\x1b[0m
        '''));
        return;

    action(n=n, num_shots=num_shots);
    return;

def action_display_statistics(queue: bool = False):
    '''
    Displays statistics of the job results of running the teleportation protocol.

    @inputs
    - `queue` - <boolean> `true` = display widget to choose job from IBM backend queue. `false` = use latest simulation.
    '''
    option = _latest.get_backend(not queue);
    job = _latest.get_job(not queue);
    # extract statitics:
    @recover_job(queue=queue, option=option, job=job, ensure_job_done=True)
    def action(job: IBMQJob):
        result = job.result();
        counts, _ = get_counts(result);
        display(QkVisualisation.plot_histogram(counts, title='Measurements'));
        return;
    action();
    return;
