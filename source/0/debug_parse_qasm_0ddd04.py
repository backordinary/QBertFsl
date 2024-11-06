# https://github.com/latticesurgery-com/lattice-surgery-compiler/blob/68438058099b5fd99a6a338d5ca7940d6e1038ef/debug/debug_parse_qasm.py
import lattice_surgery_computation_composer as ls

# Import django file rendering
import sys
sys.path.append("..")
sys.path.append("../web")
from web.lattice_main.render_to_file import render_to_file


from qiskit import circuit as qkcirc
import qiskit.visualization as qkvis


import segmented_qasm_parser


class CondtitionOnMeasurement(ls.EvaluationCondition):
    def __init__(self,reference_measurement : ls.Measurement, required_value : int):
        self.reference_measurement = reference_measurement
        self.required_value = required_value

    def does_evaluate(self):
        return self.reference_measurement.get_outcome()==self.required_value


EXAMPLE_FILE="../assets/demo_circuits/bell_pair.qasm"


if __name__ == "__main__":
    compilation_text = ""

    I = ls.PauliOperator.I
    X = ls.PauliOperator.X
    Y = ls.PauliOperator.Y
    Z = ls.PauliOperator.Z

    c = qkcirc.QuantumCircuit.from_qasm_file(EXAMPLE_FILE)
    print(qkvis.circuit_drawer(c).single_string())


    c = segmented_qasm_parser.parse_file(EXAMPLE_FILE)
    print(c.render_ascii())

    render_to_file(EXAMPLE_FILE,'index.html',False)




