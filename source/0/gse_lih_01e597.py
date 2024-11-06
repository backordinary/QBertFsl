# https://github.com/SamirFarhat17/quantum-computer-programming-ibm/blob/eeb446026f480cdb48e4dc9c6d23b825300493c9/nature-experiments/gse_lih.py
from qiskit_nature.drivers import UnitsType, Molecule
from qiskit_nature.drivers.second_quantization import ElectronicStructureDriverType, ElectronicStructureMoleculeDriver
from qiskit_nature.problems.second_quantization import ElectronicStructureProblem
from qiskit_nature.converters.second_quantization import QubitConverter
from qiskit_nature.mappers.second_quantization import JordanWignerMapper


# Define molecule
molecule = Molecule(geometry=[['H', [0., 0., 0.]],
                              ['H', [0., 0., 0.735]]],
                            charge=0, multiplicity=1)
# Definedriver
driver = ElectronicStructureMoleculeDriver(molecule, basis='sto3g', 
                    driver_type=ElectronicStructureDriverType.PYSCF)
# Problem type
es_problem = ElectronicStructureProblem(driver)
# Qubit mapper
qubit_converter = QubitConverter(JordanWignerMapper())

# Solver definition
from qiskit_nature.algorithms import NumPyEigensolverFactory
numpy_solver = NumPyEigensolverFactory(use_default_filter_criterion=True)

from qiskit import Aer
from qiskit.utils import QuantumInstance
from qiskit_nature.algorithms import GroundStateEigensolver, QEOM, VQEUCCFactory

# This first part sets the ground state solver
# see more about this part in the ground state calculation tutorial
quantum_instance = QuantumInstance(Aer.get_backend('aer_simulator_statevector'))
solver = VQEUCCFactory(quantum_instance)
gsc = GroundStateEigensolver(qubit_converter, solver)

# The qEOM algorithm is simply instantiated with the chosen ground state solver
qeom_excited_states_calculation = QEOM(gsc, 'sd')

from qiskit_nature.algorithms import ExcitedStatesEigensolver

numpy_excited_states_calculation = ExcitedStatesEigensolver(qubit_converter, numpy_solver)
numpy_results = numpy_excited_states_calculation.solve(es_problem)

qeom_results = qeom_excited_states_calculation.solve(es_problem)

#print(numpy_results)
#print('\n\n')
#print(qeom_results)

# Add spin filter
import numpy as np

def filter_criterion(eigenstate, eigenvalue, aux_values):
    return np.isclose(aux_values[0][0], 2.)

new_numpy_solver = NumPyEigensolverFactory(filter_criterion=filter_criterion)
new_numpy_excited_states_calculation = ExcitedStatesEigensolver(qubit_converter, new_numpy_solver)
new_numpy_results = new_numpy_excited_states_calculation.solve(es_problem)

print(new_numpy_results)
