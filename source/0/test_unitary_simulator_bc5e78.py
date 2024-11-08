# https://github.com/frevson/Qiskit-Aer/blob/dac153d6730e4de9d7787b0de8540855a26b81e6/test/terra/test_unitary_simulator.py
# -*- coding: utf-8 -*-

# Copyright 2018, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

"""
UnitarySimulator Integration Tests
"""

import unittest
from test.terra.utils import common
from test.terra.utils import ref_1q_clifford
from test.terra.utils import ref_2q_clifford
from test.terra.utils import ref_non_clifford
from test.terra.utils import ref_unitary_gate

from qiskit import execute
from qiskit.providers.aer import UnitarySimulator


class TestUnitarySimulator(common.QiskitAerTestCase):
    """UnitarySimulator tests."""

    # ---------------------------------------------------------------------
    # Test h-gate
    # ---------------------------------------------------------------------
    def test_h_gate_deterministic_default_basis_gates(self):
        """Test h-gate circuits compiling to backend default basis_gates."""
        circuits = ref_1q_clifford.h_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.h_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_h_gate_deterministic_waltz_basis_gates(self):
        """Test h-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_1q_clifford.h_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.h_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_h_gate_deterministic_minimal_basis_gates(self):
        """Test h-gate gate circuits compiling to U,CX"""
        circuits = ref_1q_clifford.h_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.h_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_h_gate_nondeterministic_default_basis_gates(self):
        """Test h-gate circuits compiling to backend default basis_gates."""
        circuits = ref_1q_clifford.h_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_1q_clifford.h_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_h_gate_nondeterministic_waltz_basis_gates(self):
        """Test h-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_1q_clifford.h_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_1q_clifford.h_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_h_gate_nondeterministic_minimal_basis_gates(self):
        """Test h-gate gate circuits compiling to U,CX"""
        circuits = ref_1q_clifford.h_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_1q_clifford.h_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    # ---------------------------------------------------------------------
    # Test x-gate
    # ---------------------------------------------------------------------
    def test_x_gate_deterministic_default_basis_gates(self):
        """Test x-gate circuits compiling to backend default basis_gates."""
        circuits = ref_1q_clifford.x_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.x_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_x_gate_deterministic_waltz_basis_gates(self):
        """Test x-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_1q_clifford.x_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.x_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_x_gate_deterministic_minimal_basis_gates(self):
        """Test x-gate gate circuits compiling to U,CX"""
        circuits = ref_1q_clifford.x_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.x_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    # ---------------------------------------------------------------------
    # Test z-gate
    # ---------------------------------------------------------------------
    def test_z_gate_deterministic_default_basis_gates(self):
        """Test z-gate circuits compiling to backend default basis_gates."""
        circuits = ref_1q_clifford.z_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.z_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_z_gate_deterministic_waltz_basis_gates(self):
        """Test z-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_1q_clifford.z_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.z_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_z_gate_deterministic_minimal_basis_gates(self):
        """Test z-gate gate circuits compiling to U,CX"""
        circuits = ref_1q_clifford.z_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.z_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    # ---------------------------------------------------------------------
    # Test y-gate
    # ---------------------------------------------------------------------
    def test_y_gate_deterministic_default_basis_gates(self):
        """Test y-gate circuits compiling to backend default basis_gates."""
        circuits = ref_1q_clifford.y_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.y_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_y_gate_deterministic_waltz_basis_gates(self):
        """Test y-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_1q_clifford.y_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.y_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_y_gate_deterministic_minimal_basis_gates(self):
        """Test y-gate gate circuits compiling to U,CX
        DISABLED until transpiler bug is fixed.
        """
        circuits = ref_1q_clifford.y_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.y_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    # ---------------------------------------------------------------------
    # Test s-gate
    # ---------------------------------------------------------------------
    def test_s_gate_deterministic_default_basis_gates(self):
        """Test s-gate circuits compiling to backend default basis_gates."""
        circuits = ref_1q_clifford.s_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.s_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_s_gate_deterministic_waltz_basis_gates(self):
        """Test s-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_1q_clifford.s_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.s_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_s_gate_deterministic_minimal_basis_gates(self):
        """Test s-gate gate circuits compiling to U,CX"""
        circuits = ref_1q_clifford.s_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.s_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_s_gate_nondeterministic_default_basis_gates(self):
        """Test s-gate circuits compiling to backend default basis_gates."""
        circuits = ref_1q_clifford.s_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_1q_clifford.s_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_s_gate_nondeterministic_waltz_basis_gates(self):
        """Test s-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_1q_clifford.s_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_1q_clifford.s_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_s_gate_nondeterministic_minimal_basis_gates(self):
        """Test s-gate gate circuits compiling to U,CX"""
        circuits = ref_1q_clifford.s_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_1q_clifford.s_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    # ---------------------------------------------------------------------
    # Test sdg-gate
    # ---------------------------------------------------------------------
    def test_sdg_gate_deterministic_default_basis_gates(self):
        """Test sdg-gate circuits compiling to backend default basis_gates."""
        circuits = ref_1q_clifford.sdg_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.sdg_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_sdg_gate_deterministic_waltz_basis_gates(self):
        """Test sdg-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_1q_clifford.sdg_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.sdg_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_sdg_gate_deterministic_minimal_basis_gates(self):
        """Test sdg-gate gate circuits compiling to U,CX"""
        circuits = ref_1q_clifford.sdg_gate_circuits_deterministic(final_measure=False)
        targets = ref_1q_clifford.sdg_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_sdg_gate_nondeterministic_default_basis_gates(self):
        """Test sdg-gate circuits compiling to backend default basis_gates."""
        circuits = ref_1q_clifford.sdg_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_1q_clifford.sdg_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_sdg_gate_nondeterministic_waltz_basis_gates(self):
        """Test sdg-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_1q_clifford.sdg_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_1q_clifford.sdg_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_sdg_gate_nondeterministic_minimal_basis_gates(self):
        """Test sdg-gate gate circuits compiling to U,CX"""
        circuits = ref_1q_clifford.sdg_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_1q_clifford.sdg_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    # ---------------------------------------------------------------------
    # Test cx-gate
    # ---------------------------------------------------------------------
    def test_cx_gate_deterministic_default_basis_gates(self):
        """Test cx-gate circuits compiling to backend default basis_gates."""
        circuits = ref_2q_clifford.cx_gate_circuits_deterministic(final_measure=False)
        targets = ref_2q_clifford.cx_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_cx_gate_deterministic_waltz_basis_gates(self):
        """Test cx-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_2q_clifford.cx_gate_circuits_deterministic(final_measure=False)
        targets = ref_2q_clifford.cx_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_cx_gate_deterministic_minimal_basis_gates(self):
        """Test cx-gate gate circuits compiling to U,CX"""
        circuits = ref_2q_clifford.cx_gate_circuits_deterministic(final_measure=False)
        targets = ref_2q_clifford.cx_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_cx_gate_nondeterministic_default_basis_gates(self):
        """Test cx-gate circuits compiling to backend default basis_gates."""
        circuits = ref_2q_clifford.cx_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_2q_clifford.cx_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_cx_gate_nondeterministic_waltz_basis_gates(self):
        """Test cx-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_2q_clifford.cx_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_2q_clifford.cx_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_cx_gate_nondeterministic_minimal_basis_gates(self):
        """Test cx-gate gate circuits compiling to U,CX"""
        circuits = ref_2q_clifford.cx_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_2q_clifford.cx_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    # ---------------------------------------------------------------------
    # Test cz-gate
    # ---------------------------------------------------------------------
    def test_cz_gate_deterministic_default_basis_gates(self):
        """Test cz-gate circuits compiling to backend default basis_gates."""
        circuits = ref_2q_clifford.cz_gate_circuits_deterministic(final_measure=False)
        targets = ref_2q_clifford.cz_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_cz_gate_deterministic_waltz_basis_gates(self):
        """Test cz-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_2q_clifford.cz_gate_circuits_deterministic(final_measure=False)
        targets = ref_2q_clifford.cz_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_cz_gate_deterministic_minimal_basis_gates(self):
        """Test cz-gate gate circuits compiling to U,CX"""
        circuits = ref_2q_clifford.cz_gate_circuits_deterministic(final_measure=False)
        targets = ref_2q_clifford.cz_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_cz_gate_nondeterministic_default_basis_gates(self):
        """Test cz-gate circuits compiling to backend default basis_gates."""
        circuits = ref_2q_clifford.cz_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_2q_clifford.cz_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_cz_gate_nondeterministic_waltz_basis_gates(self):
        """Test cz-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_2q_clifford.cz_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_2q_clifford.cz_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_cz_gate_nondeterministic_minimal_basis_gates(self):
        """Test cz-gate gate circuits compiling to U,CX"""
        circuits = ref_2q_clifford.cz_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_2q_clifford.cz_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    # ---------------------------------------------------------------------
    # Test swap-gate
    # ---------------------------------------------------------------------
    def test_swap_gate_deterministic_default_basis_gates(self):
        """Test swap-gate circuits compiling to backend default basis_gates."""
        circuits = ref_2q_clifford.swap_gate_circuits_deterministic(final_measure=False)
        targets = ref_2q_clifford.swap_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_swap_gate_deterministic_waltz_basis_gates(self):
        """Test swap-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_2q_clifford.swap_gate_circuits_deterministic(final_measure=False)
        targets = ref_2q_clifford.swap_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_swap_gate_deterministic_minimal_basis_gates(self):
        """Test swap-gate gate circuits compiling to U,CX"""
        circuits = ref_2q_clifford.swap_gate_circuits_deterministic(final_measure=False)
        targets = ref_2q_clifford.swap_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_swap_gate_nondeterministic_default_basis_gates(self):
        """Test swap-gate circuits compiling to backend default basis_gates."""
        circuits = ref_2q_clifford.swap_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_2q_clifford.swap_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_swap_gate_nondeterministic_waltz_basis_gates(self):
        """Test swap-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_2q_clifford.swap_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_2q_clifford.swap_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_swap_gate_nondeterministic_minimal_basis_gates(self):
        """Test swap-gate gate circuits compiling to U,CX"""
        circuits = ref_2q_clifford.swap_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_2q_clifford.swap_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    # ---------------------------------------------------------------------
    # Test t-gate
    # ---------------------------------------------------------------------
    def test_t_gate_deterministic_default_basis_gates(self):
        """Test t-gate circuits compiling to backend default basis_gates."""
        circuits = ref_non_clifford.t_gate_circuits_deterministic(final_measure=False)
        targets = ref_non_clifford.t_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_t_gate_deterministic_waltz_basis_gates(self):
        """Test t-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_non_clifford.t_gate_circuits_deterministic(final_measure=False)
        targets = ref_non_clifford.t_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_t_gate_deterministic_minimal_basis_gates(self):
        """Test t-gate gate circuits compiling to U,CX"""
        circuits = ref_non_clifford.t_gate_circuits_deterministic(final_measure=False)
        targets = ref_non_clifford.t_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_t_gate_nondeterministic_default_basis_gates(self):
        """Test t-gate circuits compiling to backend default basis_gates."""
        circuits = ref_non_clifford.t_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_non_clifford.t_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_t_gate_nondeterministic_waltz_basis_gates(self):
        """Test t-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_non_clifford.t_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_non_clifford.t_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_t_gate_nondeterministic_minimal_basis_gates(self):
        """Test t-gate gate circuits compiling to U,CX"""
        circuits = ref_non_clifford.t_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_non_clifford.t_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    # ---------------------------------------------------------------------
    # Test tdg-gate
    # ---------------------------------------------------------------------
    def test_tdg_gate_deterministic_default_basis_gates(self):
        """Test tdg-gate circuits compiling to backend default basis_gates."""
        circuits = ref_non_clifford.tdg_gate_circuits_deterministic(final_measure=False)
        targets = ref_non_clifford.tdg_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_tdg_gate_deterministic_waltz_basis_gates(self):
        """Test tdg-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_non_clifford.tdg_gate_circuits_deterministic(final_measure=False)
        targets = ref_non_clifford.tdg_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_tdg_gate_deterministic_minimal_basis_gates(self):
        """Test tdg-gate gate circuits compiling to U,CX"""
        circuits = ref_non_clifford.tdg_gate_circuits_deterministic(final_measure=False)
        targets = ref_non_clifford.tdg_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_tdg_gate_nondeterministic_default_basis_gates(self):
        """Test tdg-gate circuits compiling to backend default basis_gates."""
        circuits = ref_non_clifford.tdg_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_non_clifford.tdg_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_tdg_gate_nondeterministic_waltz_basis_gates(self):
        """Test tdg-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_non_clifford.tdg_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_non_clifford.tdg_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_tdg_gate_nondeterministic_minimal_basis_gates(self):
        """Test tdg-gate gate circuits compiling to U,CX"""
        circuits = ref_non_clifford.tdg_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_non_clifford.tdg_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    # ---------------------------------------------------------------------
    # Test ccx-gate
    # ---------------------------------------------------------------------
    def test_ccx_gate_deterministic_default_basis_gates(self):
        """Test ccx-gate circuits compiling to backend default basis_gates."""
        circuits = ref_non_clifford.ccx_gate_circuits_deterministic(final_measure=False)
        targets = ref_non_clifford.ccx_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_ccx_gate_deterministic_waltz_basis_gates(self):
        """Test ccx-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_non_clifford.ccx_gate_circuits_deterministic(final_measure=False)
        targets = ref_non_clifford.ccx_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_ccx_gate_deterministic_minimal_basis_gates(self):
        """Test ccx-gate gate circuits compiling to U,CX"""
        circuits = ref_non_clifford.ccx_gate_circuits_deterministic(final_measure=False)
        targets = ref_non_clifford.ccx_gate_unitary_deterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_ccx_gate_nondeterministic_default_basis_gates(self):
        """Test ccx-gate circuits compiling to backend default basis_gates."""
        circuits = ref_non_clifford.ccx_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_non_clifford.ccx_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_ccx_gate_nondeterministic_waltz_basis_gates(self):
        """Test ccx-gate gate circuits compiling to u1,u2,u3,cx"""
        circuits = ref_non_clifford.ccx_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_non_clifford.ccx_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='u1,u2,u3,cx')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_ccx_gate_nondeterministic_minimal_basis_gates(self):
        """Test ccx-gate gate circuits compiling to U,CX"""
        circuits = ref_non_clifford.ccx_gate_circuits_nondeterministic(final_measure=False)
        targets = ref_non_clifford.ccx_gate_unitary_nondeterministic()
        job = execute(circuits, UnitarySimulator(), shots=1, basis_gates='U,CX')
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    # ---------------------------------------------------------------------
    # Test unitary gate qobj instruction
    # ---------------------------------------------------------------------
    def test_unitary_gate_real(self):
        """Test unitary qobj instruction with real matrices."""
        qobj = ref_unitary_gate.unitary_gate_circuits_real_deterministic(final_measure=False)
        circuits = [experiment.header.name for experiment in qobj.experiments]
        targets = ref_unitary_gate.unitary_gate_unitary_real_deterministic()
        job = UnitarySimulator().run(qobj)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)

    def test_unitary_gate_complex(self):
        """Test unitary qobj instruction with complex matrices."""
        qobj = ref_unitary_gate.unitary_gate_circuits_complex_deterministic(final_measure=False)
        circuits = [experiment.header.name for experiment in qobj.experiments]
        targets = ref_unitary_gate.unitary_gate_unitary_complex_deterministic()
        job = UnitarySimulator().run(qobj)
        result = job.result()
        self.is_completed(result)
        self.compare_unitary(result, circuits, targets)


if __name__ == '__main__':
    unittest.main()
