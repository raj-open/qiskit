#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.maths import *;
from src.thirdparty.quantum import *;

from src.core.log import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'teleportation_protocol',
    'teleportation_protocol_test',
    'random_unitary_gate',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def teleportation_protocol_test() -> QuantumCircuit:
    '''
    Constructs a Quantum-Circuit for the entire teleportation protocoll
    including at the start the generation via a random unitary U
    of a state to be teleported, and at the end the inversion of U,
    to test that the state was teleported accurately.
    '''
    q_state = QuantumRegister(1, 'state');
    q_alice = QuantumRegister(1, 'alice');
    q_bob = QuantumRegister(1, 'bob');
    m = ClassicalRegister(3, 'm');
    circuit = QuantumCircuit(q_state, q_alice, q_bob, m);

    # PRE-PROCESSING:
    u, u_inv = random_unitary_gate();
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
    return circuit;

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

def entangle_pair() -> QkGate:
    circuit = QuantumCircuit(2);
    circuit.h(0);
    circuit.cx(0, 1);
    gate = circuit.to_gate();
    gate.name = 'EPR';
    return gate;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def random_unitary_gate(label: str = 'U') -> tuple[QkGate, QkGate]:
    '''
    Constructs an arbitrary unitary operator and its inverse,
    so that for test purposes one can generate
    an arbtirary state from the 0-state.
    '''
    x = np.exp(2j*np.pi*np.random.rand(4));
    x = x / np.abs(x); # force magnitude = 1
    a, b, c, z = x;

    # random rotation matrix:
    R = np.asarray([[z.real, -z.imag], [z.imag, z.real]]);
    # random unitary matrix:
    U = np.diag([1, b]) @  R @ np.diag([a, c]);

    return [
        QkUnitaryGate(data=U, label=label),
        QkUnitaryGate(data=U.T.conjugate(), label=f'{label}†'),
    ];
