# https://github.com/UST-QuAntiL/QuantME-UseCases/blob/9403b0a896ad55676416c001539c7589f8efe5fb/2020-ucc/simon/circuits/oracle1.py
from qiskit import QuantumRegister, QuantumCircuit

# Truth table:
# q[1] | q[0] ||| q[3] | q[2]
#   0  |   0  |||   0  |   1
#   0  |   1  |||   0  |   1
#   1  |   0  |||   1  |   1
#   1  |   1  |||   1  |   1
# --> searched bit string: s = 01

qc = QuantumCircuit()

q = QuantumRegister(4, 'q')

qc.add_register(q)

qc.x(q[2])
qc.cx(q[1], q[3])

def get_circuit(**kwargs):
    """Get oracle circuit."""
    return qc