# https://github.com/simonjriddix/quantumpp/blob/cc5763e69ae20e4a59f4d0e6df4adafc090d5df8/stress_tests/python/qft_qiskit.py
#!/usr/bin/env python3

# Qiskit QFT stress tests

from qiskit import *

import math
import os
import sys
import timeit

if len(sys.argv) != 3:
    sys.exit("Please specify the maximum number of cores and qubits!")

num_cores = int(sys.argv[1])  # max number of cores
n = int(sys.argv[2])          # number of qubits

os.environ['OPENBLAS_NUM_THREADS'] = str(num_cores)
os.environ['MKL_NUM_THREADS'] = str(num_cores)

q = QuantumRegister(n)
qc = QuantumCircuit(q)

# start timing
start_time = timeit.default_timer()

for i in range(n):
    qc.h(q[i])
    for j in range(2, n - i + 1):
        qc.crz(2 * math.pi / 2 ** j, q[i + j - 1], q[i])

for i in range(n // 2):
    qc.swap(q[i], q[n - 1 - i])

# Compile and run the Quantum circuit on a simulator backend


all_local_backends = Aer.backends(
    local=True)  # returns a list of local backends
qasm_simulator = all_local_backends[0]
statevector_simulator = all_local_backends[1]
job_sim = execute(qc, backend=statevector_simulator, shots=1)
result = job_sim.result()

elapsed = timeit.default_timer() - start_time
# end timing

print("{0}, {1}, {2}".format(num_cores, n, elapsed))
