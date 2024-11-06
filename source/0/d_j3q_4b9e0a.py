# https://github.com/brunojulia/quantumlabUB/blob/bd3d3a6cf37fbbc6b20b2594b105dbc5b653a760/QuantumComputation/demos/d-j3q.py
from qiskit import * 
from qiskit.quantum_info import Statevector 
import numpy as np 
from numpy import pi 
import matplotlib.pyplot as plt 

def GetStatevector():
    backend = Aer.get_backend('statevector_simulator')
    qr = QuantumRegister(4) 
    cr = ClassicalRegister(4) 
    circuit = QuantumCircuit(qr) 
 
    circuit.x(qr[3]) 
    circuit.h(qr[0]) 
    circuit.h(qr[1]) 
    circuit.h(qr[2]) 
    circuit.h(qr[3]) 
    circuit.cx(qr[0], qr[3]) 
    circuit.cx(qr[1], qr[3]) 
    circuit.cx(qr[2], qr[3]) 
    circuit.h(qr[0]) 
    circuit.h(qr[1]) 
    circuit.h(qr[2]) 
    circuit.h(qr[3]) 

    plotresults = execute(circuit,backend).result().get_statevector()
    circuit.u3(-0, -0, 0, qr[0])
    circuit.u3(-0, -0, 0, qr[1])
    circuit.u3(-0, -0, 0, qr[2])
    circuit.u3(-0, -0, 0, qr[3])
    results = execute(circuit,backend).result().get_statevector()

    return results, plotresults

def gatesmatrix():
    matrix=[
    ['', 'H', '', 'CX', '', '', '', 'H', '', '', '', ''],
    ['', 'H', '', '', 'CX', '', '', 'H', '', '', '', ''],
    ['', 'H', '', '', '', 'CX', '', 'H', '', '', '', ''],
    ['X', 'H', '', 'CX', 'CX', 'CX', '', 'H', '', '', '', '']]

    shape=(4, 12)

    multigates=[[3, 0, 3], [3, 1, 4], [3, 2, 5]]

    return shape, matrix, multigates

def name():
    return "DEUTSCH-JOZSA ALGORITHM (3 QUBITS)"


def img_num():
    return 8


def highlight(page):
    grid=np.zeros((4,12))
    if page==5:
        grid[:,0:2]=1   
    elif page==6 or page==7:
        grid[:,3:6]=1
    elif page==8:
        grid[:,7]=1
    
    return(grid)
    
def customize(screen):
    screen.title.text='Deutsh-Jozsa Agorithm (3 Qubits)'
