# https://github.com/epiqc/PartialCompilation/blob/50d80f56efdf754e40a0b1dd00404788a03fdf3d/qiskit-terra/test/python/converters/test_ast_to_dag.py
# -*- coding: utf-8 -*-

# Copyright 2018, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

"""Tests for the converters."""

import unittest

from qiskit.converters import ast_to_dag, circuit_to_dag
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import qasm
from qiskit.test import QiskitTestCase, Path


class TestAstToDag(QiskitTestCase):
    """Test AST to DAG."""

    def setUp(self):
        qr = QuantumRegister(3)
        cr = ClassicalRegister(3)
        self.circuit = QuantumCircuit(qr, cr)
        self.circuit.ccx(qr[0], qr[1], qr[2])
        self.circuit.measure(qr, cr)
        self.dag = circuit_to_dag(self.circuit)

    def test_from_ast_to_dag(self):
        """Test Unroller.execute()"""
        ast = qasm.Qasm(filename=self._get_resource_path('example.qasm',
                                                         Path.QASMS)).parse()
        dag_circuit = ast_to_dag(ast)
        expected_result = """\
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
qreg r[3];
creg c[3];
creg d[3];
h q[0];
h q[1];
h q[2];
cx q[0],r[0];
cx q[1],r[1];
cx q[2],r[2];
barrier q[0],q[1],q[2];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure r[0] -> d[0];
measure r[1] -> d[1];
measure r[2] -> d[2];
"""
        expected_dag = circuit_to_dag(QuantumCircuit.from_qasm_str(expected_result))
        self.assertEqual(dag_circuit, expected_dag)


if __name__ == '__main__':
    unittest.main(verbosity=2)
