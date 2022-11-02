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
    'get_ouput_state_of_circuit',
    'plot_ouput_state_of_circuit',
    'PLOT_VALUES',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - compute output state for test purposes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@connect_to_backend(option=BACKEND_SIMULATOR.QASM)
def get_ouput_state_of_circuit(
    option: BACKEND | BACKEND_SIMULATOR,
    backend: QkBackend,
    circuit: QuantumCircuit,
    state: Optional[list[Literal[0]|Literal[1]]] = None,
) -> dict[str, complex]:
    '''
    Extends the circuit, so that an initial state is forced
    and captures the output state as a vector (without measuring it).

    @inputs
    - `ciruit` - the quantum circuit.
    - `state` - (optional) desired input (basis) state. Defaults to `[0, 0, ..., 0]`.

    @returns
    The output state as a vector represented as a dictionary.
    '''
    # clone circuit and extract shape:
    circuit = circuit.copy().decompose();
    m = circuit.num_qubits;
    n = circuit.num_clbits;
    a = circuit.num_ancillas;

    # set input state if not set:
    if state is None:
        state = [0]*m;

    # extend the circuit with initialisation + state capture.
    test_circuit = QuantumCircuit(m, n);
    for index, value in zip(range(m), state):
        if value == 1:
            test_circuit.x(index);
    test_circuit.append(circuit, range(m), range(n));
    test_circuit.save_statevector();
    test_circuit = test_circuit.decompose();

    # create and run a single job in the simulator
    job = backend.run(circuits=test_circuit, shots=1);

    # extract results as a vector
    result = job.result();
    vector = result.get_statevector(test_circuit);

    # store state as a dictionary for ease of use:
    state_out = convert_state_to_dictionary(vector, sort=True, clean=True);

    return state_out;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - plot output state for test purposes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def plot_ouput_state_of_circuit(
    circuit: QuantumCircuit,
    state: Optional[list[Literal[0]|Literal[1]]] = None,
    sort_by: Optional[Callable[[str, complex], Any]] = None,
    filter_by: Optional[Callable[[str, complex], bool]] = None,
    # options for plots:
    mode: PLOT_VALUES = PLOT_VALUES.POWER,
    title: str = 'State of output under input {state} \n ({part})',
    figsize: tuple[int, int] = (10, 4),
    dpi: int = 360,
    q_min: float = 0.05,
) -> mpltFigure:
    '''
    Extends the circuit, so that an initial state is forced
    and captures the output state as a vector (without measuring it).
    Creates and displays a plot of output state.

    @inputs
    - `ciruit` - the quantum circuit.
    - `state` - (optional) desired input (basis) state. Defaults to `[0, 0, ..., 0]`.
    - `sort_by` - <function> sort components of output state by key/value.
    - `filter_by` - <function> filter components of output state by key/value.

    options for plots:

    - `mode` - <enum> how the values are to be plotted. Particularly useful options are:
        - `PLOT_VALUES.POWER` - show state vector components as probabilities
        - `PLOT_VALUES.REAL` - show real parts of components
        - `PLOT_VALUES.IMAG` - show imaginary parts of components
    - `title` - <string> (optional) title of plot.
    - `figsize` - <(integer, integer)> Size of figure.
    - `dpi` - <integer> resolution of image.
    - `q_min` - all keys of component values below this quantile will be cut out.

    @returns
    The figure handle of the plot.
    '''
    # clone circuit and extract shape:
    m = circuit.num_qubits;
    n = circuit.num_clbits;
    a = circuit.num_ancillas;

    # set input state if not set:
    if state is None:
        state = [0]*m;

    # get state and optionally sort:
    state_out = get_ouput_state_of_circuit(circuit=circuit, state=state);

    # optionally filter / sort output:
    if filter_by is not None:
        state_out = dict(list(filter(
            lambda item: filter_by(item[0], item[1]),
            state_out.items(),
        )));
    if mode == PLOT_VALUES.LOG_POWER:
        state_out = dict(list(filter(
            lambda item: abs(item[1]) > 0,
            state_out.items(),
        )));
    if sort_by is not None:
        state_out = dict(sorted(
            state_out.items(),
            key = lambda item: sort_by(item[0], item[1])
        ));

    # create data to plot - components of output state:
    X, Y = list(state_out.keys()), np.asarray(list(state_out.values()));
    values = np.abs(Y);
    th = np.quantile(values, q=q_min);
    X = [ x if abs(y) >= th else '—' for x, y in zip(X, Y) ];
    match mode:
        case PLOT_VALUES.ABSOLUTE:
            Y = np.abs(Y);
            part = 'absolute values';
        case PLOT_VALUES.REAL:
            Y = Y.real;
            part = 'real parts';
        case PLOT_VALUES.IMAG:
            Y = Y.imag;
            part = 'imaginary parts';
        case PLOT_VALUES.LOG_POWER:
            Y = np.abs(Y)**2;
            Y = -np.log(Y);
            part = 'as log-probabilities';
        case PLOT_VALUES.ENTROPY:
            Y = np.abs(Y)**2;
            Y = -Y * np.log2(Y + 1*(Y == 0));
            part = 'as entropy values';
        # case PLOT_VALUES.POWER:
        case _:
            Y = np.abs(Y)**2;
            part = 'as probabilities';

    # create stem plot:
    fig, ax = mplt.subplots(1, 1, constrained_layout=True, figsize=figsize, dpi=dpi);
    state_str = ''.join(map(str, state));
    title = title.format(
        state = f'$\| {state_str} \\rangle$',
        part = part,
    );
    mplt.title(label=title, fontdict={'size': 12});
    mplt.xticks(rotation=-75, ha='right', fontsize=10);

    N = len(X);
    ax.stem(Y);
    ax.set_xticks(list(range(N)));
    ax.set_xticklabels(X);

    return fig;
