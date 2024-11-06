# https://github.com/yunseo-kim/Qlassifier/blob/867e0e036264f48bd94b1954e85d15c7131f9af8/Hojun%20Lee/PQC.py
import numpy as np
import matplotlib.pyplot as plt

import torch
from torch.autograd import Function
from torchvision import datasets, transforms
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F

import qiskit
from qiskit import transpile, assemble
from qiskit.visualization import *

class QuantumCircuit:
    def __init__(self, n_qubits=9, backend=None, shots=1024):
        self.qr = qiskit.QuantumRegister(n_qubits)
        self.cr = qiskit.ClassicalRegister(1)
        self.circuit = qiskit.QuantumCircuit(self.qr,self.cr)
        self.params = qiskit.circuit.ParameterVector('θ',3*n_qubits)
        self.n_qubits = n_qubits
        self.output_channels = n_qubits

        ## circuit
        for i in range(n_qubits):
            self.circuit.rx(self.params[i],i)
        for i in range(n_qubits):
            self.circuit.rz(self.params[i+n_qubits],i)
        for i in range(n_qubits-1):
            self.circuit.crx(self.params[i+2*n_qubits],i,i+1)
        self.circuit.crx(self.params[3*n_qubits-1],n_qubits-1,0)

        self.backend = backend
        self.shots = shots
    def encoded_circuit(self,data,option='RY'):
        en_circ = qiskit.QuantumCircuit(self.qr,self.cr)
        # data range: 0 ~ 1
        if option == 'RY':
            for i, th in enumerate(data):
                # print(i,th)
                en_circ.ry(th.item()*2*np.pi,i)
        elif option == 'threshold':
            for i, th in enumerate(data):
                if th > 0.5:
                    en_circ.x(i)
        else:
            pass
        # print(en_circ)
        return en_circ
    def run(self,data,params_tensor):
        output = []
        params = params_tensor.tolist()
        # print({self.params:params})
        if data is None:
            new_circ = self.circuit
        else:
            new_circ = self.encoded_circuit(data)
            new_circ.append(self.circuit,qargs=self.qr,cargs=self.cr)
        circ = new_circ.bind_parameters({self.params: params})
        circ.measure(0,0)
        # circ.measure(range(self.output_channels),range(self.output_channels))
        job = qiskit.execute(circ, backend=self.backend,shots=self.shots)
        result = job.result().get_counts()
        # print(result)
        counts = np.array(list(result.values()))
        states = np.array(list(result.keys())).astype(float)
        # Compute probabilities for each state
        probabilities = counts / self.shots
        # Get state expectation
        expectation = np.sum(states * probabilities)
        output.append(expectation)
        
        return output