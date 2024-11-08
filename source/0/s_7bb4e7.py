# https://github.com/niefermar/CuanticaProgramacion/blob/cf066149b4bd769673e83fd774792e9965e5dbc0/qiskit/extensions/standard/s.py
# -*- coding: utf-8 -*-

# Copyright 2017, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

# pylint: disable=invalid-name

"""
S=diag(1,i) Clifford phase gate or its inverse.
"""
from qiskit import CompositeGate
from qiskit import InstructionSet
from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit.qasm import pi
from qiskit.extensions.standard import header  # pylint: disable=unused-import


class SGate(CompositeGate):
    """S=diag(1,i) Clifford phase gate or its inverse."""

    def __init__(self, qubit, circ=None):
        """Create new S gate."""
        super().__init__("s", [], [qubit], circ)
        self.u1(pi / 2, qubit)

    def reapply(self, circ):
        """Reapply this gate to corresponding qubits in circ."""
        self._modifiers(circ.s(self.arg[0]))

    def qasm(self):
        """Return OPENQASM string."""
        qubit = self.data[0].arg[0]
        phi = self.data[0].param[0]
        if phi > 0:
            return self.data[0]._qasmif("s %s[%d];" % (qubit[0].name, qubit[1]))

        return self.data[0]._qasmif("sdg %s[%d];" % (qubit[0].name, qubit[1]))


def s(self, q):
    """Apply S to q."""
    if isinstance(q, QuantumRegister):
        instructions = InstructionSet()
        for j in range(q.size):
            instructions.add(self.s((q, j)))
        return instructions

    self._check_qubit(q)
    return self._attach(SGate(q, self))


def sdg(self, q):
    """Apply Sdg to q."""
    return self.s(q).inverse()


QuantumCircuit.s = s
QuantumCircuit.sdg = sdg
CompositeGate.s = s
CompositeGate.sdg = sdg
