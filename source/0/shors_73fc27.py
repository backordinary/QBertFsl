# https://github.com/thetronjohnson/Quantum/blob/64199c386f5877a0a5fe54d7f3d74a5fe3784da3/Qiskit/shors.py
from qiskit import BasicAer
from qiskit.aqua import QuantumInstance, run_algorithm
from qiskit.aqua.algorithms import Shor

n = int(input("Enter the number: "))
shor = Shor(n)
backend = BasicAer.get_backend('qasm_simulator')
quantum_instance = QuantumInstance(backend,shots=2000)
res =  shor.run(quantum_instance)
fact = res['factors'][0]
print(f" Factors of { n } using Shor's Algorithm is: {fact}")