# https://github.com/BenediktRiegel/quantum-no-free-lunch/blob/059253d5aa7c3f6dcd66fef7d8562d38e6452f97/quantum_backends.py
import enum

import pennylane as qml
from qiskit import IBMQ


class QuantumBackends(enum.Enum):
    qml_default = "qml_default.qubit"
    qml_lightning = "qml_lightning.qubit"
    qml_tensor_tf = "qml_default.tensor.tf"
    custom_ibmq = "custom_ibmq"
    aer_statevector_simulator = "aer_statevector_simulator"
    aer_qasm_simulator = "aer_qasm_simulator"
    ibmq_qasm_simulator = "ibmq_qasm_simulator"
    ibmq_santiago = "ibmq_santiago"
    ibmq_manila = "ibmq_manila"
    ibmq_bogota = "ibmq_bogota"
    ibmq_quito = "ibmq_quito"
    ibmq_belem = "ibmq_belem"
    ibmq_lima = "ibmq_lima"
    ibmq_armonk = "ibmq_armonk"

    def get_max_num_qbits(
            self,
            ibmq_token: str,
            custom_backend_name: str,
    ):
        if self.name.startswith("aer"):
            return None
        elif self.name.startswith("ibmq"):
            # Use IBMQ backend
            provider = IBMQ.enable_account(ibmq_token)
            backend = provider.get_backend(self.name)
            return backend.configuration().n_qubits
        elif self.name.startswith("custom_ibmq"):
            provider = IBMQ.enable_account(ibmq_token)
            backend = provider.get_backend(custom_backend_name)
            return backend.configuration().n_qubits
        elif self.name.startswith("qml"):
            return None

    def get_pennylane_backend(
        self,
        ibmq_token: str,
        custom_backend_name: str,
        qubit_cnt: int,
    ) -> qml.Device:
        if self.name.startswith("aer"):
            # Use local AER backend
            aer_backend_name = self.name[4:]

            return qml.device("qiskit.aer", wires=qubit_cnt, backend=aer_backend_name)
        elif self.name.startswith("ibmq"):
            # Use IBMQ backend
            provider = IBMQ.enable_account(ibmq_token)

            return qml.device(
                "qiskit.ibmq",
                wires=qubit_cnt,
                backend=self.name,
                provider=provider
            )
        elif self.name.startswith("custom_ibmq"):
            provider = IBMQ.enable_account(ibmq_token)

            return qml.device(
                "qiskit.ibmq",
                wires=qubit_cnt,
                backend=custom_backend_name,
                provider=provider,
            )
        elif self.name.startswith("qml"):
            return qml.device(self.value[4:], wires=qubit_cnt)
        else:
            raise ValueError("Unknown pennylane backend specified!")
