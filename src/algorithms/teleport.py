#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.maths import *;
from src.thirdparty.quantum import *;
from src.thirdparty.types import *;

from src.core.log import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'teleportation_protocol',
    'teleportation_protocol_test',
    'random_unitary_parameters',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def teleportation_protocol_test() -> tuple[QuantumCircuit, list[QkParameter]]:
    '''
    Constructs a Quantum-Circuit for the entire teleportation protocoll
    including at the start the generation via a random unitary U
    of a state to be teleported, and at the end the inversion of U,
    to test that the state was teleported accurately.
    '''
    theta1 = QkParameter('$\\theta_{1}$');
    theta2 = QkParameter('$\\theta_{2}$');
    theta3 = QkParameter('$\\theta_{3}$');
    u, u_inv = qk_unitary_gate_pair(theta1, theta2, theta3);

    q_state = QuantumRegister(1, 'state');
    q_alice = QuantumRegister(1, 'alice');
    q_bob = QuantumRegister(1, 'bob');
    m = ClassicalRegister(3, 'm');
    circuit = QuantumCircuit(q_state, q_alice, q_bob, m);

    # PRE-PROCESSING:
    circuit.append(entangle_pair(), [1,2]);
    circuit.barrier([0,1,2]);
    circuit.append(u, [0]);
    # TELEPORTATION:
    circuit.barrier([0,1,2]);
    circuit.append(teleportation_protocol(include_entanglement=False), [0,1,2], [0,1]);
    circuit.barrier([0,1,2]);
    # POST-PROCESSING:
    circuit.append(u_inv, [2]);
    circuit.measure(2, 2);

    circuit.name = 'Teleport-Test';
    return circuit, circuit.parameters;

def teleportation_protocol(include_entanglement: bool = True) -> QuantumCircuit:
    '''
    Constructs a Quantum-Circuit for the entire teleportation protocoll.
    '''
    q_state = QuantumRegister(1, 'state');
    q_alice = QuantumRegister(1, 'alice');
    q_bob = QuantumRegister(1, 'bob');
    m = ClassicalRegister(2, 'm');
    circuit = QuantumCircuit(q_state, q_alice, q_bob, m);
    if include_entanglement:
        circuit.append(entangle_pair(), [1, 2]);
        circuit.barrier([0,1,2]);
    circuit.cx(0, 1);
    circuit.h(0);
    circuit.barrier([0,1,2]);
    circuit.measure(0, 0);
    circuit.measure(1, 1);
    circuit.barrier([0,1,2]);
    circuit.cx(1, 2);
    circuit.cz(0, 2);
    circuit.name = 'Teleport';
    return circuit;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def entangle_pair() -> QkGate:
    circuit = QuantumCircuit(2);
    circuit.h(0);
    circuit.cx(0, 1);
    gate = circuit.to_gate();
    gate.name = 'EPR';
    return gate;

def random_unitary_parameters(n: int) -> list[QkOperator]:
    '''
    @inputs
    - `n` - <integer> the number of desired unitaries

    @returns
    a list of parameter values to generate random unitaries.
    '''
    return 2 * np.pi * np.random.rand(n, 3);
