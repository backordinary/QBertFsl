# https://github.com/mcoggins96/Quantum-Computing-UK-Repository/blob/760dd7d38ba32778d043562f6082c925bb1b1580/Basic/Controlled%20Hadamard%20gate.py
from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, execute,IBMQ
from qiskit.tools.monitor import job_monitor

IBMQ.enable_account('Enter API KEY HERE')
provider = IBMQ.get_provider(hub='ibm-q')

backend = provider.get_backend('ibmq_qasm_simulator')

    
q = QuantumRegister(2,'q')
c = ClassicalRegister(2,'c')

circuit = QuantumCircuit(q,c)

circuit.x(q[0])
circuit.ch(q[0], q[1]);
circuit.measure(q,c)

print(circuit)

job = execute(circuit, backend, shots=8192)

job_monitor(job)
counts = job.result().get_counts()

print(counts)



