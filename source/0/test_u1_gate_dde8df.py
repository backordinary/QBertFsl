# https://github.com/qudoor/qutrunk/blob/6d4b564c18d7a79ca6edcd2ad0ced1c1e385fe9a/qutrunk/test/gate/local/test_u1_gate.py
import numpy as np
import pytest
from qiskit import QuantumCircuit, assemble, Aer

from qutrunk.circuit.gates import H, All, U1
from qutrunk.circuit import QCircuit
from qutrunk.circuit.gates import Matrix
from qutrunk.test.gate.local.backend_fixture import backend, backend_type


class TestU1:
    @pytest.fixture
    def result_qutrunk(self, backend):
        # local backend
        circuit = QCircuit(backend=backend)
        qr = circuit.allocate(1)
        All(H) * qr
        U1(np.pi / 2) * qr[0]
        result_q = np.array(circuit.get_statevector()).reshape(-1, 1)
        return result_q

    def test_matrix(self, result_qutrunk):
        """Test U1 gate with Matrix."""
        circuit = QCircuit()
        qr = circuit.allocate(1)
        Matrix(H.matrix.tolist()) * qr[0]
        Matrix(U1(np.pi / 2).matrix.tolist()) * qr[0]
        result_m = circuit.get_statevector()
        result_m = np.array(result_m).reshape(-1, 1)
        assert np.allclose(result_qutrunk, result_m)

    def test_qiskit(self, result_qutrunk):
        """Test U1 gate with qiskit."""
        qc = QuantumCircuit(1)
        initial_state = [1, 0]
        qc.initialize(initial_state, 0)
        # apply gate
        qc.h(0)
        qc.u1(np.pi / 2, 0)
        # run
        sim = Aer.get_backend("aer_simulator")
        qc.save_statevector()
        q_obj = assemble(qc)
        result_qiskit = sim.run(q_obj).result()
        result_qiskit = np.array(result_qiskit.get_statevector()).reshape(-1, 1)

        assert np.allclose(result_qutrunk, result_qiskit)

    def test_gate_inverse(self):
        """Test the inverse of U1 gate."""
        # local backend
        circuit = QCircuit()
        qr = circuit.allocate(1)
        All(H) * qr
        # initial state
        result_init = np.array(circuit.get_statevector()).reshape(-1, 1)

        U1(np.pi / 2) * qr[0]
        U1(np.pi / 2).inv() * qr[0]
        result_expect = circuit.get_statevector()
        result_expect = np.array(result_expect).reshape(-1, 1)

        assert np.allclose(result_init, result_expect)

    def test_matrix_inverse(self):
        """Test the inverse of U1 gate with Matrix."""
        circuit = QCircuit()
        qr = circuit.allocate(1)

        Matrix(H.matrix.tolist()) * qr[0]
        # initial state
        result_init = np.array(circuit.get_statevector()).reshape(-1, 1)

        Matrix(U1(np.pi / 2).matrix.tolist()) * qr[0]
        Matrix(U1(np.pi / 2).matrix.tolist()).inv() * qr[0]
        result_m = circuit.get_statevector()
        result_m = np.array(result_m).reshape(-1, 1)

        assert np.allclose(result_init, result_m)
