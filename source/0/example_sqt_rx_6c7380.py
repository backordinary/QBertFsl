# https://github.com/baidu/QCompute/blob/209fc1f7d1862cfaae7ae7242f09f366b61f0065/Extensions/QuantumErrorProcessing/examples/tomography/example-sqt-rx.py
#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Baidu, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Example to demonstrate Spectral Quantum Tomography on the two-qubit CNOT gate.
Spectral Quantum Tomography is a simple method to extract the eigenvalues of a noisy few-qubit gate
in a SPAM-resistant fashion, using low resources in terms of gate sequence length. See

.. [HBT19] Helsen, Jonas, Francesco Battistel, and Barbara M. Terhal.
        "Spectral quantum tomography."
        npj Quantum Information 5.1 (2019): 1-11.
"""
import qiskit
from qiskit.providers.fake_provider import FakeSantiago
import pickle
import os
import matplotlib.pyplot as plt
from cmath import *
import numpy as np

import sys
sys.path.append('../..')

from QCompute import *
import qcompute_qep.tomography as tomography
import qcompute_qep.quantum.pauli as pauli
import qcompute_qep.utils.circuit


# Set the token. You must set your VIP token in order to access the hardware.
Define.hubToken = "Token"

#######################################################################################################################
# Set the quantum hardware for Spectral Quantum Tomography.
#######################################################################################################################
# For numeric test on the ideal simulator, change qc to BackendName.LocalBaiduSim2
qc = BackendName.LocalBaiduSim2

# For experiment on the real quantum device, change qc to BackendName.CloudBaiduQPUQian
# qc = BackendName.CloudBaiduQPUQian

# For numeric test on the noisy simulator, change qc to Qiskit's FakeSantiago
# qc = qiskit.providers.aer.AerSimulator.from_backend(FakeSantiago())

##########################################################################################
# Set the quantum program for the CNOT gate in Spectral Quantum Tomography.
##########################################################################################
# Apply Ry gate in qubit [1]
qp = QEnv()  # qp is short for "quantum program", instance of QProgram
qp.Q.createList(2)
RX(np.math.pi / 4)(qp.Q[1])

# Compute numerically the ideal CNOT for reference
ideal_cnot = qcompute_qep.utils.circuit.circuit_to_unitary(qp)
ideal_ptm = pauli.unitary_to_ptm(ideal_cnot).data
# Calculate the eigenvalues of PTM representation
ideal_eigvals, _ = np.linalg.eig(ideal_ptm)

# Initialize a SpectralTomography instance
st = tomography.SpectralTomography()
# Call the tomography procedure and estimate the eigenvalues of the noisy RX gate
noisy_eigvals = st.fit(qp, qc, k=50, l=30, qubits=[1])

print("The ideal eigenvalues of the PTM representation are: \n", ideal_eigvals)
print("The noisy eigenvalues of the PTM representation are: \n", noisy_eigvals)

##########################################################################################
# Visualize the ideal and noisy eigenvalues obtained in Spectral Quantum Tomography.
##########################################################################################

ax = plt.subplot(polar=True)

ax.set_rlim(0.99, 1.01)
noisy_data = np.zeros((2, np.size(noisy_eigvals)), dtype=float)
ideal_data = np.zeros((2, np.size(ideal_eigvals)), dtype=float)

for i, val in enumerate(noisy_eigvals):
    noisy_data[:, i] = np.asarray(polar(val))

for i, val in enumerate(ideal_eigvals):
    ideal_data[:, i] = np.asarray(polar(val))

ax.scatter(noisy_data[1, :], noisy_data[0, :], c='blue', label='noisy')
ax.scatter(ideal_data[1, :], ideal_data[0, :], c='red', label='ideal')
plt.legend()
plt.show()
