# https://github.com/thetronjohnson/Quantum/blob/64199c386f5877a0a5fe54d7f3d74a5fe3784da3/Qiskit/Getting-Started/basic.py
import numpy as np
from qiskit import(
  QuantumCircuit,
  execute,
  Aer)
from qiskit.visualization import plot_histogram


circuit = QuantumCircuit(2,2)

circuit.h(0)
circuit.cx(0,1)
circuit.measure([0,1],[0,1])

circuit.draw(output='mpl')

simulator = Aer.get_backend('qasm_simulator')
job = execute(circuit,simulator,shots=1000)

result = job.result()
counts = result.get_counts(circuit)

print("\nTotal count for 00 and 11 are: ",counts)
plot_histogram(counts)