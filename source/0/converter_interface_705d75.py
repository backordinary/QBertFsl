# https://github.com/UST-QuAntiL/QuantumTranspiler/blob/a7cf54a83f26da7ef758fe5a17f7b8cf98dcc1a7/conversion/converter/converter_interface.py
from abc import ABC, abstractmethod
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Qubit
from qiskit.circuit import Parameter as qiskit_Parameter
from qiskit.circuit import ParameterExpression as qiskit_Parameter_expression
from qiskit.circuit import parameter
from typing import List

class ConverterInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_control_capable(self) -> bool:
        pass

    @property
    @abstractmethod
    def circuit(self):
        pass

    @abstractmethod
    def import_circuit(self, circuit):
        pass   

    @abstractmethod
    def init_circuit(self):
        pass

    @abstractmethod
    def create_qreg_mapping(self, qreg_mapping, qubit: Qubit, index: int):
        pass

    @abstractmethod
    def create_creg_mapping(self, cregs: List[ClassicalRegister]):
        pass

    @abstractmethod
    def gate(self, is_controlled = False):
        pass

    @abstractmethod
    def custom_gate(self):
        pass

    @abstractmethod
    def parameter_conversion(self, parameter: qiskit_Parameter):
        pass

    @abstractmethod
    def parameter_expression_conversion(self, parameter: qiskit_Parameter_expression):
        pass    

    @abstractmethod
    def barrier(self, qubits):
        pass

    @abstractmethod
    def measure(self):
        pass

    @abstractmethod
    def subcircuit(self, subcircuit, qubits, clbits):
        pass  

    @abstractmethod
    def language_to_circuit(self, language: str):
        pass

    @abstractmethod
    def circuit_to_language(self, circuit) -> str:
        pass