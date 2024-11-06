# https://github.com/it-security-kassel-nordhessen/meetup/blob/aed0b0d111438b9479fafb6c387d103f2e35dd02/2019_06_12_38th/quantum_computing/code/qiskit/hadamard/hadamard.py
from qiskit import (
        QuantumCircuit,
        ClassicalRegister,
        QuantumRegister,
        execute,
        Aer)
from qiskit.visualization import plot_histogram, plot_bloch_multivector

# Build a quantum circuit

n = 1  # number of qubits
q = QuantumRegister(n)
c = ClassicalRegister(1)

circuit = QuantumCircuit(q,c)
#circuit.x(q[0])
circuit.h(q[0])

circuit.measure(q,c);
# Matplotlib Drawing
colors = {'id': '#ffca64',
  'u0': '#f69458',
  'u1': '#f69458',
  'u2': '#f69458',
  'u3': '#f69458',
  'x': '#a6ce38',
  'y': '#a6ce38',
  'z': '#a6ce38',
  'h': '#00bff2',
  's': '#00bff2',
  'sdg': '#00bff2',
  't': '#ff6666',
  'tdg': '#ff6666',
  'rx': '#ffca64',
  'ry': '#ffca64',
  'rz': '#ffca64',
  'reset': '#d7ddda',
  'target': '#00bff2',
  'meas': '#f070aa'}

style = {'displaycolor':colors}
circuit.draw(output='mpl',filename='hadamard.pdf',style=style)

simulator = Aer.get_backend('qasm_simulator')
job = execute(circuit, simulator, shots=1000)
result = job.result()
counts = result.get_counts(circuit)
plot_histogram(counts).savefig('hadamard_histo.pdf')

#psi = result.get_statevector(circuit)
#plot_bloch_multivector(psi).savefig('hadamard_bloch.pdf')
