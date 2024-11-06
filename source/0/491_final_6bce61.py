# https://github.com/FehintolaObafemi/Shor-s-Algorithm/blob/629837eb5987b8d6ebf9469397529684b6478724/491_final.py
# -*- coding: utf-8 -*-
"""491-Final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gslOpE_i7_lJ5dlxqx4vtMwbn-5A9f3q

Name: Taofeek Obafemi-Babatunde
Course: Computer Science 491 - Quantum Computing
Fall 2020 - Final Project

Import all the required libraries
"""

from qiskit import IBMQ
from qiskit.aqua import QuantumInstance
from qiskit.aqua.algorithms import Shor

"""Connect IBM Quantum Computer"""

# Enter your API token here
IBMQ.enable_account('ENTER API TOKEN HERE')
provider = IBMQ.get_provider(hub='ibm-q')

# Specifies the quantum device
backend = provider.get_backend('ibmq_qasm_simulator')

"""Factorize first number"""

first_factors = Shor(571)

result_dict = first_factors.run(QuantumInstance(backend, shots=1, skip_qobj_validation=False))

# Get factors from results
first_result = result_dict['first_factors']

print(first_result)

"""Factorize second number"""

second_factors = Shor(757) 

result_dict = second_factors.run(QuantumInstance(backend, shots=1, skip_qobj_validation=False))

# Get factors from results
second_result = result_dict['second_factors']

print(second_result)