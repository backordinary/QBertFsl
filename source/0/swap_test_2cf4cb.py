# https://github.com/iQuHACK/2021_QryptoQuHackers/blob/de5e6e517f5288613bc9c44bb8766506aafb4053/swap_test.py
from qiskit import *
#from qiskit_ionq_provider import IonQProvider 
from qiskit.providers.jobstatus import JobStatus
#Call provider and set token value

from math import log

def swap_test(qsi, qsj, verbose=False):
    size = int(log(len(qsi), 2))
    q = QuantumRegister(2*size+1)
    c = ClassicalRegister(1)    
    swaptest = QuantumCircuit(q,c)
    swaptest.initialize(qsi, range(1,size+1))
    swaptest.initialize(qsj, range(size+1, 2*size+1))
    swaptest.h(0)
    for i in range(1, size+1):
        swaptest.cx(i+size,i)
        swaptest.toffoli(0,i,i+size)
        swaptest.cx(i+size,i)
    swaptest.h(0)
    swaptest.measure(range(1), range(1))
    
    if verbose:
        print(swaptest.draw())
    
    backend_sim = Aer.get_backend('qasm_simulator')
    job_sim = execute(swaptest, backend_sim, shots=1)
    result_sim = job_sim.result()
    counts = result_sim.get_counts()
    return int('1' in counts)
#print(swaptest([0.8,0.6],[0.8,0.6]))

#swap3=swaptest(3)
#print(swap3.draw())
#backend = provider.get_backend("ionq_simulator")
##backend_sim = Aer.get_backend('qasm_simulator')
##job_sim = execute(circ, backend_sim, shots=1024)
#job_sim = backend.run(swap3, shots=1024)
#result_sim = job_sim.result()
#
#counts = result_sim.get_counts()
#print(counts)
