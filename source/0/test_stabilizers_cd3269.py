# https://github.com/nlaanait/qcdenoise/blob/e4f364389e345d236f1b1993c2025b1b1394370e/tests/test_stabilizers.py
import os

import pytest
from qiskit import circuit
from qiskit.result.counts import Counts
import qcdenoise as qcd
from qiskit.test.mock import FakeMontreal

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


@pytest.fixture()
def n_qubits():
    return 4


@pytest.fixture()
def graph_state(n_qubits):
    graph_db = qcd.GraphDB()
    graph_state = qcd.GraphState(graph_db=graph_db, n_qubits=n_qubits)
    return graph_state.sample()


@pytest.fixture()
def stabilizer_circuits(n_qubits, graph_state):
    stabilizer = qcd.TothStabilizer(graph_state, n_qubits=n_qubits)
    return stabilizer.build()


@pytest.fixture()
def graph_circuit(n_qubits, graph_state):
    circ_builder = qcd.CXGateCircuit(n_qubits=n_qubits)
    return circ_builder.build(graph_state)["circuit"]


@pytest.mark.dependency()
def test_TothStabilizer(graph_state, n_qubits):
    stabilizer = qcd.TothStabilizer(graph_state, n_qubits=n_qubits)
    _ = stabilizer.find_stabilizers()
    circuit_dict = stabilizer.build()
    assert(len(circuit_dict.values()) == n_qubits + 1)


@pytest.mark.dependency(depends=["test_TothStabilizer"])
def test_StabilizerSampler(stabilizer_circuits, graph_circuit):
    sampler = qcd.StabilizerSampler(
        backend=FakeMontreal(), n_shots=1024)
    counts = sampler.sample(stabilizer_circuits=stabilizer_circuits,
                            graph_circuit=graph_circuit)
    assert len(counts) == len(stabilizer_circuits.values())
    for cnt in counts:
        assert isinstance(cnt, Counts)
