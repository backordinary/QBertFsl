# https://github.com/MasLiang/Quantum-Adder/blob/b3e128525d124b6cb32203e84c140dd4896d0725/py/BQFA/BQFA_in_Biswas.py
from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit
from qiskit.providers.aer import QasmSimulator
from qiskit import transpile
import sys
sys.path.append("..")
from Basic_Gates.init_state import bit2state
from Basic_Gates.sqrt_root_CNOT_Hermitian_gate import *

def BQFA_in_Biswas(circ, q_A, q_B, q_C, q_0):
    '''
    This circuit is binary quantum full adder proposed in (Biswas, et al. 2008). 
        If user wants to add it in their circuits, they need to pass their 
        circuit and the qubits that will be used in this circuit. 

    input:
        circ        :       circuit
        q_A         :       input data A 
        q_B         :       input data B
        q_C         :       input carry 
        q_0         :       auxiliary qubit whose initial state is |0>
    output:
        circ        :       circuit
    
    **Example:**

    circ = BQFA_in_Biswas(circ, q[0], q[1], q[2], q[3])
    
    A BQFA_in_Biswas is added to the circuit. q[0]-q[2] correspond to input data A,B and input carry. 
        q[3] is initiated as |0>.

    **Circuit symbol:**

    .. parsed-literal::      
                                
                  
          q_A  ─────────────■───────■─────────────────────────────  garbage
                            │     ┌─┴─┐       
          q_B  ─────■───────│─────┤ X ├────────────■──────────────  garbage
                    │       │     └───┘          ┌─┴─┐          
          q_C  ─────┤───────├──────────────■─────┤ X ├─────■──────  |Sum>
                  ┌─┴──┐  ┌─┴──┐         ┌─┴──┐  └───┘  ┌──┴───┐ 
          q_0  ───┤ √X ├──┤ √X ├─────────┤ √X ├─────────┤ √X^T ├──  |Carry>
                  └────┘  └────┘         └────┘         └──────┘
                  
    '''
    circ.csx(q_B,q_0)
    circ.csx(q_A,q_0)
    circ.cx(q_A,q_B)
    circ.csx(q_C,q_0)
    circ.cx(q_B,q_C)
    circ = sqrt_root_CNOT_Hermitian(circ, q_C, q_0)
    return circ

if __name__ == "__main__":
    # initiate 3 qubits
    q = QuantumRegister(4,'q')
    # initiate 2 traditional bits
    c = ClassicalRegister(2,'c')
    # initiate quantum circuit
    circ = QuantumCircuit(q,c)
    # input
    data_A = 1
    data_B = 1
    Carry = 1
    # transform custom bit to quantum state vector
    initial_state = bit2state(str(data_A)+str(data_B)+str(Carry)+'0')
    # initial input qubit state
    circ.set_statevector(initial_state)
    # build the quantum circuit
    circ = BQFA_in_Biswas(circ, q[0], q[1], q[2], q[3])
    circ.measure(q[2],c[0])
    circ.measure(q[3],c[1])
    print(circ.draw())

    # Build a simulator to exert the quantum circuit
    backend = QasmSimulator()

    # First we have to transpile the quantum circuit
    # to the low-level QASM instructions used by the
    # backend
    circ_compiled = transpile(circ, backend)

    # Execute the circuit on the qasm simulator.
    # We've set the number of repeats of the circuit
    # to be 1, because each state of each qubit is |0> or |1> 
    # rather than superposition state.
    job_sim = backend.run(circ_compiled, shots=1)

    # Grab the results from the job.
    result_sim = job_sim.result()
    counts = result_sim.get_counts(circ_compiled)
    print(counts)