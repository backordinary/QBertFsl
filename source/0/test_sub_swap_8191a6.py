# https://github.com/hkhetawat/QArithmetic/blob/a9950caf15aeda5cb7d45c327a457d773268bf54/examples/test_sub_swap.py
# Import the Qiskit SDK
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute, Aer
from QArithmetic import sub_swap

# Input N
N = 4

a = QuantumRegister(N+1)
b = QuantumRegister(N+1)

ca = ClassicalRegister(N+1)
cb = ClassicalRegister(N+1)

qc = QuantumCircuit(a, b, ca, cb)


# Input Superposition
# a =  01110
qc.x(a[1])
qc.x(a[2])
qc.x(a[3])
# b = 01011
qc.x(b[0])
qc.x(b[1])
qc.x(b[3])

sub_swap(qc, a, b, N+1)

qc.measure(a, ca)
qc.measure(b, cb)

backend_sim = Aer.get_backend('qasm_simulator')
job_sim = execute(qc, backend_sim)
result_sim = job_sim.result()

print(result_sim.get_counts(qc))
