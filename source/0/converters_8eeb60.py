# https://github.com/ArlineQ/arline_quantum/blob/8fa31271f4882c4c1a92ff500a86daa03a9cfae2/arline_quantum/gate_chain/converters.py
# Arline Quantum
# Copyright (C) 2019-2022 Turation Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import os
import tempfile

from arline_quantum.gate_chain.gate_chain import GateChain

from qiskit import QuantumCircuit
from cirq.contrib.qasm_import import circuit_from_qasm
import pytket.qasm as pyqasm
from cirq import NamedQubit


class GateChainConverter:
    format_id = None  #: format identifier (str)

    @staticmethod
    def from_gate_chain(gate_chain):
        raise NotImplementedError()

    @staticmethod
    def to_gate_chain(circuit_object):
        raise NotImplementedError()


class QiskitGateChainConverter(GateChainConverter):
    format_id = "qiskit"

    @staticmethod
    def from_gate_chain(gate_chain):
        qasm = gate_chain.to_qasm(qreg_name="q")
        circuit_object = QuantumCircuit.from_qasm_str(qasm)
        return circuit_object

    @staticmethod
    def to_gate_chain(circuit_object, **kwargs):
        qasm_data = circuit_object.qasm()
        lines = qasm_data.split("\n")
        gate_chain = GateChain.from_qasm_list_of_lines(lines, **kwargs)
        # Saving Qiskit circuit layout dictionary to qreg_mapping
        assert len(gate_chain.qreg_mapping) == 1, "Only one quantum register is supported in Qiskit converter"
        qreg_name = list(gate_chain.qreg_mapping.keys())[0]
        mapping_dict = gate_chain.qreg_mapping[qreg_name]
        # The circuit_object._layout is None by default
        # When running Qiskit's transpile() _layout is assigned
        if circuit_object._layout is not None:
            for i, qreg in enumerate(mapping_dict.keys()):
                mapping_dict[qreg] = circuit_object._layout[i].index
        return gate_chain


class CirqGateChainConverter(GateChainConverter):
    format_id = "cirq"

    @staticmethod
    def from_gate_chain(gate_chain):
        # TODO fix it
        # qasm = gate_chain.to_qasm(qreg_name="q")
        # qasm = f"creg c[{gate_chain.quantum_hardware.num_qubits}];\n" + qasm

        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = os.path.join(tmpdirname, "target.qasm")
            gate_chain.save_to_qasm(fname, qreg_name="q")
            with open(fname) as file:
                qasm_data = file.read()
        circuit_object = circuit_from_qasm(qasm_data)
        return circuit_object

    @staticmethod
    def to_gate_chain(circuit_object, **kwargs):
        qubit_order = {NamedQubit(f'q_{n}'): NamedQubit(f'q_{n}') for n in range(len(circuit_object.all_qubits()))}

        # TODO: Check how to pass qubit order
        # Expected: Union[cirq.ops.qubit_order.QubitOrder, Iterable[cirq.ops.raw_types.Qid]]
        qasm_data = circuit_object.to_qasm()  # qubit_order=qubit_order
        lines = qasm_data.split("\n")
        gate_chain = GateChain.from_qasm_list_of_lines(lines, quantum_hardware=None)

        return gate_chain


class PytketGateChainConverter(GateChainConverter):
    format_id = "pytket"

    @staticmethod
    def from_gate_chain(gate_chain):
        qasm = gate_chain.to_qasm(qreg_name="q")
        circuit_object = pyqasm.circuit_from_qasm_str(qasm)
        return circuit_object

    @staticmethod
    def to_gate_chain(circuit_object, qmap=None, **kwargs):
        qasm_data = pyqasm.circuit_to_qasm_str(circuit_object)
        lines = qasm_data.split("\n")
        gate_chain = GateChain.from_qasm_list_of_lines(lines, **kwargs)
        assert len(gate_chain.qreg_mapping) == 1, "Only one quantum register is supported in Pytket converter"
        qreg_name = list(gate_chain.qreg_mapping.keys())[0]

        num_qubits = gate_chain.quantum_hardware.num_qubits
        if qmap is not None:
            # Pytket qubit placement Qmap object
            qmap_dict = {k.index[0]: v.index[0] for (k, v) in qmap.items()}
            gate_chain.qreg_mapping[qreg_name] = qmap_dict
        # Default qreg mapping if placement is not provided
        else:
            gate_chain.qreg_mapping[qreg_name] = {q: q for q in range(num_qubits)}
        return gate_chain
