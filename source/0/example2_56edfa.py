# https://github.com/MartianSheep/quantum-ATG/blob/d0c7a9c6b4d09edf931356b7b334e0fc0d544cf9/examples/example2.py
import numpy as np
import qiskit.circuit.library as qGate

from qatg import QATG
from qatg import QATGFault

class myRXFault(QATGFault):
	def __init__(self, param):
		super(myRXFault, self).__init__(qGate.RXGate, 0, f"gateType: RX, qubits: 0, param: {param}")
		self.param = param
	def createOriginalGate(self):
		return qGate.RXGate(self.param)
	def createFaultyGate(self, faultfreeGate):
		return qGate.RXGate(faultfreeGate.params[0] - 0.1*np.pi) # bias fault
	
class myRZFault(QATGFault):
	def __init__(self, param):
		super(myRZFault, self).__init__(qGate.RZGate, 0, f"gateType: RZ, qubits: 0, param: {param}")
		self.param = param
	def createOriginalGate(self):
		return qGate.RZGate(self.param)
	def createFaultyGate(self, faultfreeGate):
		return qGate.RZGate(faultfreeGate.params[0] - 0.1*np.pi) # bias fault

generator = QATG(circuitSize = 1, basisGateSet = [qGate.RXGate, qGate.RZGate], circuitInitializedStates = {1: [1, 0]}, minRequiredEffectSize = 2)
configurationList = generator.createTestConfiguration([myRXFault(np.pi), myRZFault(np.pi)])

for configuration in configurationList:
    print(configuration)
    configuration.circuit.draw('mpl')
input()
