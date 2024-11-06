# https://github.com/ArfatSalman/qc-test/blob/9ec9efff192318b71e8cd06a49abc676196315cb/notebooks/legacy/qconvert_tmp_cache/c44c81c12e92cc2de41881c432c9e0c6e2c7e1df1406202d6ce58e35.py
from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, execute, Aer
import numpy as np

shots = 8192

qc = QuantumCircuit()

q = QuantumRegister(6, 'q')
c = ClassicalRegister(6, 'c')

qc.add_register(q)
qc.add_register(c)

qc.ry(0.9801424781769557, q[0])
qc.rz(1.1424399624340646, q[1])
qc.cx(q[5], q[3])
qc.ry(6.094123332392967, q[0])
qc.cx(q[5], q[3])
qc.cx(q[1], q[3])
qc.rx(1.2545873742863833, q[4])
qc.rx(3.844385118274953, q[1])
qc.rx(0.29185655071471744, q[3])
qc.cx(q[1], q[2])
qc.ry(0.4087312132537349, q[1])
qc.cx(q[0], q[4])
qc.rx(3.1112882860657196, q[0])
qc.cx(q[5], q[1])
qc.ry(3.267683749398383, q[1])
qc.measure(q[0], c[0])
qc.measure(q[1], c[1])
qc.measure(q[2], c[2])
qc.measure(q[3], c[3])
qc.measure(q[4], c[4])
qc.measure(q[5], c[5])

backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend=backend, shots=shots)
job_result = job.result()
print(job_result.get_counts(qc))
