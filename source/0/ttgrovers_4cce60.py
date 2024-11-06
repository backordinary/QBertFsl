# https://github.com/mcoggins96/Quantum-Computing-UK-Repository/blob/0925ffe7c06ee0efa7ae609d59b0cc2e1e3cf1c0/Advanced/TTGrovers.py
from qiskit import IBMQ
from qiskit.aqua.algorithms import Grover
from qiskit.aqua.components.oracles import TruthTableOracle

IBMQ.enable_account('ENTER API KEY HERE')
provider = IBMQ.get_provider(hub='ibm-q')

backend = provider.get_backend('ibmq_qasm_simulator')

expression = '11000001'

oracle = TruthTableOracle(expression)

print(oracle)

grover = Grover(oracle)

result = grover.run(backend, shots=1024)
           
counts = result['measurement']

print('\nTruth tables with Grovers Search')
print('--------------------------------\n')
print('Bit string is ', expression)
print('\nResults ',counts)
print('\nPress any key to close')
input()