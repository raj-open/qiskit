#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.misc import *;
from src.thirdparty.maths import *;
from src.thirdparty.quantum import *;
from src.thirdparty.render import *;
from src.thirdparty.types import *;

from src.api import *;
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
# METHODS - ACTIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def action_display_circuit(n: int):
    '''
    Displays the quantum circuit for the Grover algorithm.

    @inputs
    - `n` - <integer> size of input set for search problem.
    '''
    print('Quantumcircuit for Grover Algorithm:');
    oraclenr = np.random.randint(0, 2);
    circuit = deutsch_jozsa_algorithm(n=n, oraclenr=oraclenr, verbose=True);
    display(circuit.draw(output=DRAW_MODE.COLOUR.value, cregbundle=False, initial_state=True));
    return;

def action_prepare_circuit_and_job(
    option: BACKEND | BACKEND_SIMULATOR,
    num_shots: int,
    n: int,
    k: int,
):
    '''
    Prepares the quntum circuit and jobs for the Grover algorithm.

    @inputs
    - `backend` - an enum value to indicate which backend to use.
    - `n` - <integer> size of list in search problem.
    - `k` - <integer> number of indexes that can be searched for (must be positive).
    - `num_shots` - number of shots of the job prepared.
    '''
    @connect_to_backend(option=option, n=n)
    def action(
        option: BACKEND | BACKEND_SIMULATOR,
        backend: QkBackend,
        num_shots: int,
        n: int,
        k: int,
    ):
        # create circuit:
        print('Quantumcircuit for testing Grover algorithm');
        marked = generate_satisfaction_problem(n=n, size=k);
        circuit = grover_algorithm_naive(n=n, marked=marked, verbose=True);

        # display circuit:
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
        print(latest_info(backend=backend, job=job));
        latest_state.set_job(job, queue=isinstance(option, BACKEND));
        return;

    action(num_shots=num_shots, n=n, k=k);
    return;

def action_display_statistics(queue: bool = False):
    '''
    Displays statistics of the job results of running the Grover algorithm.

    @inputs
    - `queue` - <boolean> `true` = display widget to choose job from IBM backend queue. `false` = use latest simulation.
    '''
    @recover_job(queue=queue, ensure_job_done=True, use_latest=True)
    def action(job: IBMQJob):
        result = job.result();
        counts, _ = get_counts(result, pad=True);
        display(QkVisualisation.plot_histogram(counts, title='Measurements'));

    action();
    return;
