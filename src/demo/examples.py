#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.maths import *;
from src.thirdparty.quantum import *;
from src.thirdparty.render import *;
from src.thirdparty.types import *;

from src.api import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'action_display_statistics',
    'action_prepare_circuit_and_job',
    'basic_action_display_circuit',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN ACTIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def action_prepare_circuit_and_job(
    option: BACKEND | BACKEND_SIMULATOR,
    num_shots: int,
    theta1: int,
    theta2: int,
    theta3: int,
):
    '''
    Prepares the quntum circuit and jobs for the Examples notebook.

    @inputs
    - `backend` - an enum value to indicate which backend to use.
    - `num_shots` - number of shots of the job prepared.
    '''
    @connect_to_backend(option=option, n=3)
    def action(
        option: BACKEND | BACKEND_SIMULATOR,
        backend: QkBackend,
        num_shots: int,
    ):
        queue = isinstance(option, BACKEND);
        # create circuit:
        print(f'Example quantum circuit with {"backend" if queue else "simulator"}');
        u, u_inv = qk_unitary_gate_pair(theta1=theta1, theta2=theta2, theta3=theta3);
        circuit = QuantumCircuit(3, 3);
        circuit.append(u, [2]);
        circuit.barrier();
        circuit.h(1);
        circuit.x(1);
        circuit.cx(1, 2);
        circuit.x(1);
        circuit.h(1);
        circuit.cx(2, 0);
        circuit.barrier();
        circuit.append(u_inv, [2]);
        circuit.measure(0, 0);
        circuit.measure(1, 1);
        circuit.measure(2, 2);

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
        latest_state.set_job(job, queue=queue);
        return;

    action(num_shots=num_shots);
    return;

def action_display_statistics(
    queue: bool = False,
    job_id: Optional[str] = None,
    backend_option: Optional[BACKEND | BACKEND_SIMULATOR] = None,
    as_widget: bool = False,
):
    '''
    Displays statistics of the job results of running the example circuit.

    @inputs
    - `queue` - <boolean> `true` = display widget to choose job from IBM backend queue. `false` = use latest simulation.
    - `job_id` - <string | None> if set, will attempt to recover this job and display output.
    - `backend_option` - <enum | None> if set, will be used in combination with `job_id` to retrieve job.
    - `as_widget` - <boolean> if `true` displays a widget interface so that use can select backend + job before carrying out action.
        If `false` (default), attempts to retrieve job and carry out action if job exists and is done.
    '''
    @recover_job(
        queue = queue,
        ensure_job_done = True,
        job_id = job_id,
        backend_option = backend_option,
        use_latest = True,
        as_widget = as_widget,
    )
    def action(job: IBMQJob):
        result = job.result();
        counts, [counts_01, counts_2] = get_counts(result, [0, 1], [2], pad=True);
        display(QkVisualisation.plot_histogram(counts, title='Measurements'));
        display(QkVisualisation.plot_histogram(counts_01, title='Measurements of QBits 0+1'));
        display(QkVisualisation.plot_histogram(counts_2, title='Measurements of QBit 2'));

    action();
    return;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# BASIC ACTIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def basic_action_display_circuit(theta1: int, theta2: int, theta3: int):
    '''
    Displays the quantum circuit for the Examples notebook.
    '''
    print('Example quantum circuit');
    circuit = QuantumCircuit(3, 3);
    circuit.u(theta1, theta2, theta3, 2);
    circuit.barrier();
    circuit.h(1);
    circuit.x(1);
    circuit.cx(1, 2);
    circuit.x(1);
    circuit.h(1);
    circuit.cx(2, 0);
    circuit.barrier();
    circuit.u(-theta1, -0, -theta3, 2);
    circuit.measure(0, 0);
    circuit.measure(1, 1);
    circuit.measure(2, 2);
    display(circuit.draw(output=DRAW_MODE.COLOUR.value, cregbundle=False, initial_state=True));
    return;