# https://github.com/mmetcalf14/Hamiltonian_Downfolding_IBM/blob/43a9ad2e092c9af7a71f55c35c80886e3e394409/DownfoldedHam_ED_060319.py
from qiskit_chemistry import FermionicOperator, QMolecule
from qiskit_chemistry.aqua_extensions.components.initial_states import HartreeFock
from qiskit_chemistry.aqua_extensions.components.variational_forms import UCCSD
from qiskit_chemistry import QMolecule as qm

from qiskit_aqua.components.optimizers import COBYLA
from qiskit_aqua import Operator
from qiskit_aqua.algorithms import VQE, ExactEigensolver
from qiskit import Aer

from scipy import linalg as la
import numpy as np
import yaml as yml
from yaml import SafeLoader as Loader
import os

import Load_Hamiltonians as lh

#################### WALK ROOT DIR ############################
root_dir = 'IntegralData/vqe-data-master/Li2_cc-pVTZ/4_ORBITALS'
data_file_list = []
data_file_list_oe = []
for dirName, subdirList, fileList in os.walk(root_dir):
    print('Found directory: %s' % dirName)
    for fname in sorted(fileList):
        if fname.endswith('.yaml'):
            data_file_list.append(fname)


#I added an x in front of the 10s for distance to force the sorting, else it sees 13 as 1
#If any distance is in the 100s (unlikely) then add a 'y' in front of dist in file name
###############################################################
############# Output Files to Plot stuff ###############

Fout = open('Li2_ExactEnergies_wMP2_4-orbitals_060319.dat',"w")
#Fout = open('Li2_ExactEnergiesG&FE_wMP2_4-orbitals_052919.dat',"w")
###########################################################

#Variables that can be assigned outside of Loop
map_type = str('jordan_wigner')
truncation_threshold = 0.01

################# IBM BACKEND #####################
backend1 = Aer.get_backend('statevector_simulator')
backend2 = Aer.get_backend('qasm_simulator')
###################################################

output_data = []
#Looping over all of the yaml files in a particular directory and saving the energies from VQE and Exact
ind = 0
for key, file in enumerate(data_file_list):

    NW_data_file = str(os.path.join(root_dir,file))
    print(NW_data_file)
    try:
        doc = open(NW_data_file, 'r')
        data = yml.load(doc, Loader)
    finally:
        doc.close()

    #Import all the data from a yaml file
    n_spatial_orbitals = data['integral_sets'][0]['n_orbitals']
    nuclear_repulsion_energy = data['integral_sets'][0]['coulomb_repulsion']['value']
    n_orbitals = 2 * n_spatial_orbitals
    n_particles = data['integral_sets'][0]['n_electrons']
    dist = 2 * data['integral_sets'][0]['geometry']['atoms'][1]['coords'][2]
    print('Bond distance is {}'.format(dist))
    if map_type == 'parity':
        # For two-qubit reduction
        n_qubits = n_orbitals - 2
    else:
        n_qubits = n_orbitals

    # Populating the QMolecule class with the data to make calculations easier
    qm.num_orbitals = n_spatial_orbitals
    qm.num_alpha = n_particles // 2
    qm.num_beta = n_particles // 2
    qm.core_orbitals = 0
    qm.nuclear_repulsion_energy = nuclear_repulsion_energy
    qm.hf_energy = data['integral_sets'][0]['scf_energy']['value']

    #Importing the integrals
    one_electron_import = data['integral_sets'][0]['hamiltonian']['one_electron_integrals']['values']
    two_electron_import = data['integral_sets'][0]['hamiltonian']['two_electron_integrals']['values']

    #Getting spatial integrals and spin integrals to construct Hamiltonian
    one_electron_spatial_integrals, two_electron_spatial_integrals = lh.get_spatial_integrals(one_electron_import,
                                                                                              two_electron_import,
                                                                                              n_spatial_orbitals)
    one_electron_spatial_integrals, two_electron_spatial_integrals = lh.trunctate_spatial_integrals(
        one_electron_spatial_integrals, two_electron_spatial_integrals, .001)
    h1, h2 = lh.convert_to_spin_index(one_electron_spatial_integrals, two_electron_spatial_integrals,
                                                  n_spatial_orbitals, truncation_threshold)
    #For the MP2 Calculation
    qm.mo_eri_ints = two_electron_spatial_integrals
    #Constructing the fermion operator and qubit operator from integrals data
    fop = FermionicOperator(h1, h2)
    qop_paulis = fop.mapping(map_type)
    qop = Operator(paulis=qop_paulis.paulis)


    ################### EXACT RESULT ##################################
    exact_eigensolver = ExactEigensolver(qop, k=12)
    ret = exact_eigensolver.run()
    print('The electronic energy is: {:.12f}'.format(ret['eigvals'][0].real))
    print('The total FCI energy is: {:.12f}'.format(ret['eigvals'][0].real + nuclear_repulsion_energy))
    exact_energy = ret['eigvals'][0].real + nuclear_repulsion_energy
    exact_energy_fe = ret['eigvals'][1].real + nuclear_repulsion_energy
    # qop.to_matrix()
    # #print(qop)
    # eigval, eigvec = np.linalg.eigh(qop.matrix.toarray())
    # exact_energy = eigval[0].real + nuclear_repulsion_energy
    # exact_energy_fe = eigval[1].real + nuclear_repulsion_energy
    # print('{} is the groundstate energy and {} is the first excited state'.format(eigval[0].real,eigval[1].real))

    ###################################################################
    # my_info = [dist, exact_energy,eigval[1].real + nuclear_repulsion_energy, eigval[2].real + nuclear_repulsion_energy, eigval[3].real\
    #            + nuclear_repulsion_energy, eigval[4].real + nuclear_repulsion_energy, eigval[5].real + nuclear_repulsion_energy, \
    #            eigval[6].real + nuclear_repulsion_energy, eigval[7].real + nuclear_repulsion_energy,  eigval[8].real + nuclear_repulsion_energy, eigval[9].real + nuclear_repulsion_energy, \
    #             eigval[10].real + nuclear_repulsion_energy, eigval[11].real + nuclear_repulsion_energy]
    my_info = [dist, ret['eigvals'][0].real + nuclear_repulsion_energy, exact_energy,ret['eigvals'][1].real + nuclear_repulsion_energy, ret['eigvals'][2].real + nuclear_repulsion_energy, ret['eigvals'][3].real\
               + nuclear_repulsion_energy, ret['eigvals'][4].real + nuclear_repulsion_energy, ret['eigvals'][5].real + nuclear_repulsion_energy, \
               ret['eigvals'][6].real + nuclear_repulsion_energy, ret['eigvals'][7].real + nuclear_repulsion_energy,  ret['eigvals'][8].real + nuclear_repulsion_energy, ret['eigvals'][9].real + nuclear_repulsion_energy, \
                ret['eigvals'][10].real + nuclear_repulsion_energy, ret['eigvals'][11].real + nuclear_repulsion_energy]
    output_data.append(my_info)
    my_info_to_str = " ".join(str(e) for e in my_info)
    Fout.write(my_info_to_str + "\n")
print(output_data)
Fout.close()


# output_data[:,0] = np.sort(output_data[:,0],axis=0)
# print(output_data)