# https://github.com/Tomev/QEL/blob/d715293d6d2924ef095de8f0cfb1957985b9ae2f/Teleportation/teleportation.py
import os
import sys

import numpy as np
import qiskit

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from methods import test_locally

# Create a Quantum Register called "qr" with 2 qubits.
qr = qiskit.QuantumRegister(3)
# Create a Classical Register called "cr" with 2 bits.
cr = qiskit.ClassicalRegister(3)


# Prepare a state rotated by theta on the qubit 0.
def prepare_state(t):
    circuit = qiskit.QuantumCircuit(qr, cr)
    circuit.ry(t, qr[0])
    return circuit


# A circuit to measure i-th qubit to i-th bit.
def measure(i):
    circuit = qiskit.QuantumCircuit(qr, cr)
    circuit.measure(qr[i], cr[i])
    return circuit


def get_teleportation_circuits():
    # A circuit to teleport state from qubit 0 to qubit 2.
    teleport = qiskit.QuantumCircuit(qr, cr)

    # Prepare bell state on qubits 1 and 2.
    teleport.h(qr[1])
    teleport.cx(qr[1], qr[2])

    teleport.measure(qr[0], cr[0])
    teleport.measure(qr[1], cr[1])

    # Prepare circuits
    circuits = []

    for theta in np.linspace(0, np.pi, 10):
        qc_test = prepare_state(theta) + measure(0) + measure(1) + measure(2)
        circuits.append(qc_test)
        qc_teleport = prepare_state(theta) + teleport + measure(2)
        circuits.append(qc_teleport)

    return circuits


# Execute
test_locally(get_teleportation_circuits())
