#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from enum import Enum;
import qiskit as qk;
from qiskit import Aer as QkBackendAer;
from qiskit import ClassicalRegister;
from qiskit import IBMQ;
from qiskit import QuantumCircuit;
from qiskit.circuit import Parameter as QkParameter;
from qiskit.circuit.gate import Gate as QkGate;
from qiskit import QuantumRegister;
from qiskit import assemble as qk_assemble;
from qiskit import execute as qk_execute;
from qiskit import transpile as qk_transpile;
from qiskit import visualization as QkVisualisation;
from qiskit.extensions import UnitaryGate as QkUnitaryGate;
from qiskit.providers import ibmq;
from qiskit.providers import Backend as QkBackend;
from qiskit.providers.ibmq.job.ibmqjob import IBMQJob;
from qiskit.providers.ibmq.ibmqbackend import IBMQBackend;
from qiskit.providers.ibmq.ibmqbackend import IBMQSimulator;
from qiskit.providers.ibmq.accountprovider import AccountProvider as QkAccountProvider;
# from qiskit.providers.ibmq import least_busy;
from qiskit.quantum_info import Statevector as QkStatevector;
from qiskit.quantum_info import Operator as QkOperator;
from qiskit.quantum_info import random_unitary as qk_random_unitary;
from qiskit.result.result import Result as QkResult;
from qiskit.tools import jupyter as QkJupyter;
from qiskit_textbook import problems as QkProblems;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODIFICATIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BACKEND(Enum):
    '''
    cf. <https://quantum-computing.ibm.com/lab/docs>
    '''
    LEAST_BUSY = -1;
    BELEM = 'ibmq_belem'
    HANOI = 'ibmq_hanoi';
    LIMA = 'ibmq_lima';
    MANILA = 'ibmq_manila';
    MELBOURNE = 'ibmq_melbourne';
    NAIROBI = 'ibm_nairobi';
    OSLO = 'ibm_oslo';
    QUITO = 'ibmq_quito';

def backend_from_name(name: str) -> BACKEND:
    try:
        e = next( e for e in BACKEND if e.value == name );
    except:
        e = BACKEND.LEAST_BUSY;
    return e;

class BACKEND_SIMULATOR(Enum):
    '''
    cf. <https://quantum-computing.ibm.com/lab/docs/iql/manage/simulator>
    '''
    # General, context-aware
    AER = 'aer_simulator';
    QASM = 'qasm_simulator';
    IBM_QASM = 'ibmq_qasm_simulator';
    UNITARY = 'unitary_simulator';
    # Special
    # Stabiliser - Clifford
    CLIFFORD = 'simulator_stabilizer';
    # Stabiliser - Extended Clifford (e.g., Clifford+T)
    CLIFFORD_EXTENDED = 'simulator_extended_stabilizer';
    # Schrödinger wavefunction
    STATE_VECTOR = 'simulator_statevector';
    # Matrix Product State
    STATE_MATRIXPRODUCT = 'simulator_mps';

class DRAW_MODE(Enum):
    # images with color rendered purely in Python using matplotlib.
    COLOUR = 'mpl';
    # ASCII art TextDrawing that can be printed in the console.
    TEXT = 'text';
    # high-quality images compiled via latex.
    LATEX = 'latex';
    # raw uncompiled latex output.
    LATEX_SOURCE = 'latex_source';

def qk_unitary_gate_pair(
    theta1: float | QkParameter,
    theta2: float | QkParameter,
    theta3: float | QkParameter,
    label: str = 'U'
) -> tuple[QkGate, QkGate]:
    '''
    @inputs
    - `theta1` - <float|Parameter> random angle
    - `theta2` - <float|Parameter> random angle
    - `theta3` - <float|Parameter> random angle
    - `label` - <string> name of operator

    @returns
    a pair of gates for U and its inverse.

    NOTE: upto to a scalar multiple (phase shift)
    unitary operators are parameterised as follows:

    U = (1 0       ) Rotation(θ₂) (1 0       )
        (0 exp(ιθ₁))              (0 exp(ιθ₃))
     = P(θ₁)RY(θ₂)P(θ₃)

    NOTE: Using UGates does not work as expected.
    It also reduced accuracy both in the simulated and non-simulated setting!
    '''
    circuit = QuantumCircuit(1);
    circuit.p(theta3, 0);
    circuit.ry(theta2, 0);
    circuit.p(theta1, 0);
    u = circuit;
    u.name = f'${label}$';
    circuit = QuantumCircuit(1);
    circuit.p(-theta1, 0);
    circuit.ry(-theta2, 0);
    circuit.p(-theta3, 0);
    u_inv = circuit;
    u_inv.name = f'${label}^{{\\dagger}}$';
    return (u, u_inv);

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'backend_from_name',
    'BACKEND',
    'BACKEND_SIMULATOR',
    'ClassicalRegister',
    'DRAW_MODE',
    'ibmq',
    'IBMQ',
    'IBMQBackend',
    'IBMQJob',
    'IBMQSimulator',
    'qk',
    'qk_assemble',
    'qk_execute',
    'qk_unitary_gate_pair',
    'qk_random_unitary',
    'qk_transpile',
    'QkAccountProvider',
    'QkBackend',
    'QkBackendAer',
    'QkGate',
    'QkJupyter',
    'QkOperator',
    'QkParameter',
    'QkProblems',
    'QkResult',
    'QkStatevector',
    'QkUnitaryGate',
    'QkVisualisation',
    'QuantumCircuit',
    'QuantumRegister',
];
