# https://github.com/tenplayers/Vqe_and_Measurement/blob/2547e1b13a0202c7e7c298605d8518fbec522a65/read_hamiltonian.py
from qiskit import *
import numpy as np

#Operator Imports
from qiskit.opflow import Z, X, I, Y
# from qiskit.opflow.operator_globals import Y

#Circuit imports
from qiskit import Aer
from qiskit.tools.visualization import circuit_drawer
import qiskit.quantum_info as qi
from  qiskit.opflow.primitive_ops import PauliSumOp
from qiskit.quantum_info.operators import Operator, Pauli
from functools import reduce


def read(num_qubits):
    with open("test.txt", "r") as f:
        data = f.readlines()
        for i in range(len(data)):
            # Split the string with space
            str_list = data[i].split()
            for j in range(num_qubits):
                if str_list[j+1] == 'I':
                    str_list[j+1] = I
                elif str_list[j+1] == 'X':
                    str_list[j+1] = X
                elif str_list[j+1] == 'Y':
                    str_list[j+1] = Y
                else:
                    str_list[j+1] = Z
            if i == 0:
                qubit_op = float(str_list[0]) * reduce(lambda x, y: x ^ y, str_list[1:])
            else:
                qubit_op += float(str_list[0]) * reduce(lambda x, y: x ^ y, str_list[1:])
    
    return qubit_op


