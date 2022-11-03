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
from src.algorithms import *;
from src.models.boolsat import *;
from src.models.quantum import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'basic_action_prepare_problem',
    'action_display_statistics',
    'action_prepare_circuit_and_job',
    'basic_action_display_circuit',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - ACTIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def action_prepare_circuit_and_job(
    option: BACKEND | BACKEND_SIMULATOR,
    num_shots: int,
    problem: ProblemSAT,
    prob: float = 0.,
):
    '''
    Prepares the quntum circuit and jobs for the Grover algorithm.

    @inputs
    - `backend` - an enum value to indicate which backend to use.
    - `num_shots` - number of shots of the job prepared.
    - `problem` - an instance of a SAT problem.
    - `prob` - <float> estimated proportion of models which satisfy the problem (leave as 0. if unknown).

    NOTE: At least one of `path` or `text` must be set!
    '''
    n = problem.number_of_variables;
    Nc = problem.number_of_clauses;

    @connect_to_backend(option=option, n=n + Nc + 1)
    def action(
        option: BACKEND | BACKEND_SIMULATOR,
        backend: QkBackend,
        num_shots: int,
        problem: ProblemSAT,
        prob: float = 0.,
    ):
        # create circuit:
        print('Quantumcircuit for testing Grover algorithm');
        circuit = grover_algorithm_from_sat(problem=problem, prob=prob);

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
            # FIXME: currently these two arguments are ignored by the qiskit package:
            # name = 'grovers-algorithm',
            # tags = ['algorithm=grover', f'shots={num_shots}', f'size={k}'],
        );
        print(latest_info(backend=backend, job=job));
        latest_state.set_job(job, queue=isinstance(option, BACKEND));
        return;

    # construct SAT problem from file:
    action(num_shots=num_shots, problem=problem, prob=prob);
    return;

def action_display_statistics(
    problem: ProblemSAT,
    queue: bool = False,
    job_id: Optional[str] = None,
    backend_option: Optional[BACKEND | BACKEND_SIMULATOR] = None,
    as_widget: bool = False,
):
    '''
    Displays statistics of the job results of running the Grover algorithm.

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
        n = problem.number_of_variables;
        result = job.result();
        N, counts, [counts_inputs, counts_outputs] = get_counts(result, list(range(n)), [n], pad=True);
        if N > 0:
            display(QkVisualisation.plot_distribution(counts, title=f'Measurements (batch size: {N})'));
            display(QkVisualisation.plot_distribution(counts_inputs, title=f'Measurements of search bits (batch size: {N})'));
            display(QkVisualisation.plot_distribution(counts_outputs, title=f'Measurements of answer bit (batch size: {N})'));
        else:
            print('[WARNING] No measurements were found!');

    action();
    return;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# BASIC ACTIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def basic_action_prepare_problem(
    path: Optional[str] = None,
    text: Optional[str] = None,
    verbose: bool = False,
) -> ProblemSAT:
    '''
    Creates SAT problem from file or string.

    @inputs
    - `path` - <string> optional path to a SAT problem.
    - `text` - <string> optional direct input in DIMACS format of SAT problem.
    - `verbose` - <boolean> if `true` will print out description of SAT problem.

    NOTE: At least one of `path` or `text` must be set!
    '''
    if path is not None:
        print(f'Load SAT Problem from {path or "(text entry)"}:')
    else:
        print(f'Load SAT Problem from {path or "(text entry)"}.')

    # construct SAT problem from file or text:
    problem = read_problem_sat_from_dimacs_cnf(name='Grover', path=path, problem_text=text);

    if verbose:
        display(problem.repr(mode=PRINT_MODE.LATEX, linebreaks=True));

    return problem;

def basic_action_display_circuit(
    problem: ProblemSAT,
    prob_min: float = 0.1,
    q_min: float = 0.1,
):
    '''
    Displays the quantum circuit for the Grover algorithm.

    @inputs
    - `problem` - an instance of a SAT problem.
    - `q_min` - <float> a threshold value to avoid overcroweded plots.
    - `prob_min` - <float> a threshold value to avoid overcrowded plots.

    The components of an example output statevector will be shown.
    All components whos squared values lies below `prob_min` will be cut.
    The lower `q_min`-quantile will be cut.
    '''
    print('Quantumcircuit for Grover Iterator:');
    grit = grover_iterator_from_sat(problem=problem);
    display(grit.draw(output=DRAW_MODE.COLOUR.value, cregbundle=False, initial_state=False));
    Nc = problem.number_of_clauses;
    n = grit.num_qubits - Nc - 1;
    final = n + Nc;
    circuit = QuantumCircuit(n + Nc + 1);
    circuit.x(final);
    circuit.h(final);
    circuit.h(range(n));
    circuit.append(grit.decompose(), range(n + Nc + 1));
    plot_ouput_state_of_circuit(
        circuit = circuit.decompose(),
        title = 'Example resulting state after one iteration upon appropriate inputs',
        mode = PLOT_VALUES.POWER,
        sort_by = lambda key, value: (-abs(value), key),
        filter_by = lambda key, value: (abs(value)**2 >= prob_min),
        figsize = (10, 4),
        q_min = q_min,
    );
    return;
