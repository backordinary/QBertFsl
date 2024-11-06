# https://github.com/SupertechLabs/qiskit-superstaq/blob/a585a5be3e1604133a5571dbee9b07a4b14b4818/qiskit_superstaq/compiler_output.py
import importlib
import json
from typing import Any, Dict, List, Optional, Set, Union

import general_superstaq as gss
import qiskit

import qiskit_superstaq as qss

try:
    import qtrl.sequence_utils.readout
except ModuleNotFoundError:
    pass


def active_qubit_indices(circuit: qiskit.QuantumCircuit) -> List[int]:
    """Returns the indices of the non-idle qubits in a quantum circuit."""

    qubit_indices: Set[int] = set()

    for inst, qubits, _ in circuit:
        if inst.name != "barrier":
            indices = [circuit.find_bit(q).index for q in qubits]
            qubit_indices.update(indices)

    return sorted(qubit_indices)


def measured_qubit_indices(circuit: qiskit.QuantumCircuit) -> List[int]:
    """Returns the indices of the measured qubits in a quantum circuit."""

    measured_qubits: Set[qiskit.circuit.Qubit] = set()

    for inst, qubits, clbits in circuit:
        if isinstance(inst, qiskit.circuit.Measure):
            measured_qubits.update(qubits)

        # Recurse into definition if it involves classical bits
        elif clbits and inst.definition is not None:
            measured_qubits.update(qubits[i] for i in measured_qubit_indices(inst.definition))

    return sorted(circuit.find_bit(qubit).index for qubit in measured_qubits)


class CompilerOutput:  # pylint: disable=missing-class-docstring
    def __init__(
        self,
        circuits: Union[
            qiskit.QuantumCircuit, List[qiskit.QuantumCircuit], List[List[qiskit.QuantumCircuit]]
        ],
        pulse_sequences: Union[qiskit.pulse.Schedule, List[qiskit.pulse.Schedule]] = None,
        seq: Optional["qtrl.sequencer.Sequence"] = None,
        jaqal_programs: Optional[Union[str, List[str]]] = None,
        pulse_lists: Optional[Union[List[List[List[Any]]], List[List[List[List[Any]]]]]] = None,
    ) -> None:
        if isinstance(circuits, qiskit.QuantumCircuit):
            self.circuit = circuits
            self.pulse_sequence = pulse_sequences
            self.pulse_list = pulse_lists
            self.jaqal_program = jaqal_programs
        else:
            self.circuits = circuits
            self.pulse_sequences = pulse_sequences
            self.pulse_lists = pulse_lists
            self.jaqal_programs = jaqal_programs

        self.seq = seq

    def has_multiple_circuits(self) -> bool:
        """Returns True if this object represents multiple circuits.

        If so, this object has .circuits and .pulse_lists attributes. Otherwise, this object
        represents a single circuit, and has .circuit and .pulse_list attributes.
        """
        return hasattr(self, "circuits")

    def __repr__(self) -> str:
        if not self.has_multiple_circuits():
            return (
                f"CompilerOutput({self.circuit!r}, {self.seq!r}, {self.jaqal_program!r}, "
                f"{self.pulse_list!r})"
            )
        return (
            f"CompilerOutput({self.circuits!r}, {self.seq!r}, {self.jaqal_programs!r}, "
            f"{self.pulse_lists!r})"
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CompilerOutput):
            return False

        if self.has_multiple_circuits() != other.has_multiple_circuits():
            return False
        elif self.has_multiple_circuits():
            return (
                self.circuits == other.circuits
                and self.pulse_sequences == other.pulse_sequences
                and self.jaqal_programs == other.jaqal_programs
                and self.pulse_lists == other.pulse_lists
                and self.seq == other.seq
            )

        return (
            self.circuit == other.circuit
            and self.pulse_sequence == other.pulse_sequence
            and self.jaqal_program == other.jaqal_program
            and self.pulse_list == other.pulse_list
            and self.seq == other.seq
        )


def read_json_aqt(  # pylint: disable=missing-param-doc
    json_dict: Dict[str, str], circuits_is_list: bool, num_eca_circuits: int = 0
) -> CompilerOutput:
    """Reads out returned JSON from SuperstaQ API's AQT compilation endpoint.

    Args:
        json_dict: a JSON dictionary matching the format returned by /aqt_compile endpoint
        circuits_is_list: bool flag that controls whether the returned object has a .circuits
            attribute (if True) or a .circuit attribute (False)
    Returns:
        a CompilerOutput object with the compiled circuit(s). If qtrl is available locally,
        the returned object also stores the pulse sequence in the .seq attribute and the
        list(s) of cycles in the .pulse_list(s) attribute.
    """

    compiled_circuits: Union[List[qiskit.QuantumCircuit], List[List[qiskit.QuantumCircuit]]]
    compiled_circuits = qss.serialization.deserialize_circuits(json_dict["qiskit_circuits"])

    seq = None
    pulse_lists = None

    if importlib.util.find_spec(
        "qtrl"
    ):  # pragma: no cover, b/c qtrl is not open source so it is not in qiskit-superstaq reqs

        def _sequencer_from_state(state: Dict[str, Any]) -> "qtrl.sequencer.Sequence":
            seq = qtrl.sequencer.Sequence(n_elements=1)
            seq.__setstate__(state)
            seq.compile()
            return seq

        pulse_lists = gss.serialization.deserialize(json_dict["pulse_lists_jp"])
        state = gss.serialization.deserialize(json_dict["state_jp"])

        if "readout_jp" in json_dict:
            readout_state = gss.serialization.deserialize(json_dict["readout_jp"])
            readout_seq = _sequencer_from_state(readout_state)

            if "readout_qubits" in json_dict:
                readout_qubits = json.loads(json_dict["readout_qubits"])
                readout_seq._readout = qtrl.sequence_utils.readout._ReadoutInfo(
                    readout_seq, readout_qubits, n_readouts=len(compiled_circuits)
                )

            state["_readout"] = readout_seq

        seq = _sequencer_from_state(state)

    if num_eca_circuits:
        compiled_circuits = [
            compiled_circuits[i : i + num_eca_circuits]
            for i in range(0, len(compiled_circuits), num_eca_circuits)
        ]

        pulse_lists = pulse_lists and [
            pulse_lists[i : i + num_eca_circuits]
            for i in range(0, len(pulse_lists), num_eca_circuits)
        ]

    if circuits_is_list:
        return CompilerOutput(circuits=compiled_circuits, seq=seq, pulse_lists=pulse_lists)

    pulse_lists = pulse_lists[0] if pulse_lists is not None else None
    return CompilerOutput(circuits=compiled_circuits[0], seq=seq, pulse_lists=pulse_lists)


def read_json_qscout(
    json_dict: Dict[str, Union[str, List[str]]], circuits_is_list: bool
) -> CompilerOutput:
    """Reads out returned JSON from SuperstaQ API's QSCOUT compilation endpoint.

    Args:
        json_dict: a JSON dictionary matching the format returned by /qscout_compile endpoint
        circuits_is_list: bool flag that controls whether the returned object has a .circuits
            attribute (if True) or a .circuit attribute (False)
    Returns:
        a CompilerOutput object with the compiled circuit(s) and a list of
        jaqal programs in a string representation.
    """
    qiskit_circuits = json_dict["qiskit_circuits"]
    jaqal_programs = json_dict["jaqal_programs"]
    assert isinstance(qiskit_circuits, str)
    assert isinstance(jaqal_programs, list)
    compiled_circuits = qss.serialization.deserialize_circuits(qiskit_circuits)
    if circuits_is_list:
        return CompilerOutput(circuits=compiled_circuits, jaqal_programs=jaqal_programs)

    return CompilerOutput(circuits=compiled_circuits[0], jaqal_programs=jaqal_programs[0])


def read_json_only_circuits(json_dict: Dict[str, str], circuits_is_list: bool) -> CompilerOutput:
    """Reads JSON returned from SuperstaQ API's CQ compilation endpoint.

    Args:
        json_dict: a JSON dictionary matching the format returned by /cq_compile endpoint
        circuits_is_list: bool flag that controls whether the returned object has a .circuits
            attribute (if True) or a .circuit attribute (False)
    Returns:
        a CompilerOutput object with the compiled circuit(s)
    """
    compiled_circuits = qss.serialization.deserialize_circuits(json_dict["qiskit_circuits"])
    if circuits_is_list:
        return CompilerOutput(circuits=compiled_circuits)

    return CompilerOutput(circuits=compiled_circuits[0])