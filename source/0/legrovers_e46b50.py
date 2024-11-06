# https://github.com/mcoggins96/Quantum-Computing-UK-Repository/blob/f891d631886784e115f380e0c9c985fd511818c3/Advanced/LEGrovers.py
from qiskit import IBMQ
from qiskit.aqua.algorithms import Grover
from qiskit.aqua.components.oracles import LogicalExpressionOracle
from qiskit.visualization import plot_histogram

IBMQ.enable_account('ENTER API KEY HERE')
provider = IBMQ.get_provider(hub='ibm-q')

backend = provider.get_backend('ibmq_qasm_simulator')

expression = '(a & b)& ~(c)'

oracle = LogicalExpressionOracle(expression)
grover = Grover(oracle)

result = grover.run(backend, shots=1024)
           
counts = result['measurement']

print(counts)
print('Press any key to close')
input()
