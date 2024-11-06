# https://github.com/WBanner/Test-VQE-Repository/blob/73df829d1de56a41e2b2af5491dc9ca44c15bfb0/reconstruct_eigs.py
import numpy as np
import pandas as pd
import math
from qiskit.aqua import QuantumInstance
from qiskit.aqua.algorithms import ExactEigensolver
from qiskit.aqua.operators import WeightedPauliOperator, MatrixOperator
from qiskit.providers.aer import Aer
from qiskit.aqua.operators.op_converter import to_weighted_pauli_operator
from qiskit.quantum_info.operators import Pauli
from qiskit import IBMQ
from qisresearch.adapt.operator_pool import OperatorPool, PauliPool

adapt_data_df = pd.read_csv('load_adapt_data_df.csv')
adapt_data_dict = adapt_data_df.to_dict()
Ham_list = adapt_data_dict['hamiltonian']

counter = 0
counter2 = 0
num_hams = 10
pauli_meta_list = [0]*num_hams
weight_meta_list = [0]*num_hams
Exact_energy_dict = {'Ham_1':[],'Ham_2':[],'Ham_3':[],'Ham_4':[],'Ham_5':[],'Ham_6':[],'Ham_7':[],'Ham_8':[],'Ham_9':[]}

for counter in range(0,num_hams,1):
	Ham = Ham_list[counter]
	single_ham_list = Ham.split('\n')
	pauli_list = [0]*(len(single_ham_list)-1)
	weight_list = [0]*(len(single_ham_list)-1)
	for counter2 in range(0, len(single_ham_list)-1,1):
		pauli_list[counter2] = Pauli.from_label(single_ham_list[counter2][:4])
		weight_list[counter2] = complex(single_ham_list[counter2][6:-1])
	pauli_meta_list[counter] = pauli_list
	weight_meta_list[counter] = weight_list
	qubit_op = WeightedPauliOperator.from_list(pauli_list,weight_list)
	Exact_result = ExactEigensolver(qubit_op, k = 16).run()
	Exact_energy_dict['Ham_{}'.format(counter)] = Exact_result['energies']
	print('E', Exact_result)

Exact_energy_df = pd.DataFrame(Exact_energy_dict)
Exact_energy_df_file = open("exact_energy_df.csv", "w+")
Exact_energy_df.to_csv('exact_energy_df.csv')
Exact_energy_df_file.close()
