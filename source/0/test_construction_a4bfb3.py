# https://github.com/cda-tum/qcec/blob/6d7de6920993cf0b3845763c17fd210802e2fdc2/test/python/test_construction.py
"""Test the construction of the EquivalenceCheckingManager class."""

from __future__ import annotations

import pytest
from qiskit import QuantumCircuit

from mqt import qcec


@pytest.fixture()
def example_circuit() -> QuantumCircuit:
    """Fixture for a simple circuit."""
    qc = QuantumCircuit(1)
    qc.h(0)
    return qc


def test_default_constructor_with_qiskit(example_circuit: QuantumCircuit) -> None:
    """Test constructing an instance from two qiskit circuits with all default arguments."""
    qcec.EquivalenceCheckingManager(circ1=example_circuit, circ2=example_circuit)


def test_constructor_with_configuration(example_circuit: QuantumCircuit) -> None:
    """Test constructing an instance from circuits and a configuration object."""
    config = qcec.Configuration()
    qcec.EquivalenceCheckingManager(circ1=example_circuit, circ2=example_circuit, config=config)


def test_default_constructor_with_file(example_circuit: QuantumCircuit) -> None:
    """Test constructing an instance from two circuit files with all default arguments."""
    from pathlib import Path

    filename = "test.qasm"
    example_circuit.qasm(filename=filename)
    qcec.EquivalenceCheckingManager(circ1=filename, circ2=filename)
    Path(filename).unlink()
