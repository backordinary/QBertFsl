# https://github.com/UST-QuAntiL/Quokka/blob/87ee9f348422f7af5bd8874e0e34366e3a548d50/services/execution-service/app/circuit_executor.py
# ******************************************************************************
#  Copyright (c) 2020 University of Stuttgart
#
#  See the NOTICE file(s) distributed with this work for additional
#  information regarding copyright ownership.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ******************************************************************************
import codecs
import pickle
import time
import qiskit
from flask import jsonify
from qiskit import IBMQ, transpile, assemble, QuantumCircuit
from qiskit.providers import QiskitBackendNotFoundError, JobError, JobTimeoutError
from qiskit.providers.aer import AerSimulator
from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.ibmq.api.exceptions import RequestsApiError
from qiskit.providers.jobstatus import JOB_FINAL_STATES
from qiskit.providers.ibmq.exceptions import IBMQAccountCredentialsNotFound
from qiskit.utils import circuit_utils
from qiskit.utils.measurement_error_mitigation import get_measured_qubits

from app.model.execution_request import ExecutionRequest
from app.model.execution_response import ExecutionResponse


def execute_circuit(request: ExecutionRequest):
    list_input = True
    if isinstance(request.circuit, str):
        request.circuit = [request.circuit]
        list_input = False

    if request.provider != "ibm":
        return "This service currently only supports the execution of quantum circuits on IBMQ qpus"

    circuits = []

    for c in request.circuit:
        # DEPRECATED: get qiskit circuit object from Json object containing the base64 encoded circuit
        if request.circuit_format == "qiskit":
            loaded_circ = (pickle.loads(codecs.decode(c.encode(), "base64")))
            if request.parameters is not None:
                if len(loaded_circ.parameters.data) != len(request.parameters):
                    needed_params = []
                    # for QAOA parameters, naming must be [beta0,beta1,..., gamma0, gamma1,...] TODO generalize once OPENQASM3 is released
                    for param in loaded_circ.parameters.data:
                        if "beta" in param.name:
                            num = int(param.name[4:])
                            needed_params.append(request.parameters[num])
                        elif "gamma" in param.name:
                            num = int(param.name[5:])
                            needed_params.append(request.parameters[int(len(request.parameters)/2) + num])
                    loaded_circ = loaded_circ.bind_parameters(needed_params)
                else:
                    loaded_circ = loaded_circ.bind_parameters(request.parameters)
            circuits.append(loaded_circ)
        else:
            try:
                circuits.append(QuantumCircuit.from_qasm_str(c))
            except Exception:
                return (
                    "The quantum circuit has to be provided as an OpenQASM 2.0 String"
                )

    if request.noise_model:
        noisy_qpu = get_qpu(request.credentials, request.noise_model)
        noise_model = NoiseModel.from_backend(noisy_qpu)
        properties = noisy_qpu.properties()
        configuration = noisy_qpu.configuration()
        coupling_map = configuration.coupling_map
        basis_gates = noise_model.basis_gates

        transpiled_circuits = [transpile(c, noisy_qpu) for c in circuits]
        measurement_qubits = [
            get_measurement_qubits_from_transpiled_circuit(c)
            for c in transpiled_circuits
        ]

        if request.only_measurement_errors:
            ro_noise_model = NoiseModel()
            for k, v in noise_model._local_readout_errors.items():
                ro_noise_model.add_readout_error(v, k)
            noise_model = ro_noise_model

        backend = AerSimulator()
        job = qiskit.execute(
            transpiled_circuits,
            backend=backend,
            coupling_map=coupling_map,
            basis_gates=basis_gates,
            noise_model=noise_model,
            shots=request.shots,
            optimization_level=0,
        )
        result_counts = job.result().get_counts()
        if isinstance(result_counts, dict):
            result_counts = [result_counts]
    else:
        if "simulator" in request.qpu:
            ibm_qpu = AerSimulator()
            measurement_qubits = [list(range(0, c.num_qubits)) for c in circuits]
            transpiled_circuits = [transpile(c, backend=ibm_qpu) for c in circuits]
        else:
            ibm_qpu = get_qpu(request.credentials, request.qpu)
            transpiled_circuits = [transpile(c, backend=ibm_qpu) for c in circuits]
            measurement_qubits = [
                get_measurement_qubits_from_transpiled_circuit(c)
                for c in transpiled_circuits
            ]
        result_counts = execute(transpiled_circuits, request.shots, ibm_qpu)
        if isinstance(result_counts, dict):
            result_counts = [result_counts]
    transpiled_circuit_depths = [c.depth() for c in transpiled_circuits]

    return jsonify(
        ExecutionResponse(
            result_counts,
            measurement_qubits,
            transpiled_circuit_depths,
            list_input=list_input,
        ).to_json()
    )


def get_qpu(credentials, qpu):
    """Load account from token. Get backend."""
    try:
        try:
            IBMQ.disable_account()
        except IBMQAccountCredentialsNotFound:
            pass
        finally:
            provider = IBMQ.enable_account(**credentials)
            backend = provider.get_backend(qpu)
            return backend
    except (QiskitBackendNotFoundError, RequestsApiError):
        print(
            'Backend could not be retrieved. Backend name or credentials are invalid. Be sure to use the schema credentials: {"token": "YOUR_TOKEN", "hub": "YOUR_HUB", "group": "YOUR GROUP", "project": "YOUR_PROJECT"). Note that "ibm-q/open/main" are assumed as default values for "hub", "group", "project".'
        )
        return None


def execute(transpiled_circuit, shots, backend):
    """Execute the quantum circuit."""
    try:
        job = backend.run(assemble(transpiled_circuit, shots=shots))
        sleep_timer = 0.5
        job_status = job.status()
        while job_status not in JOB_FINAL_STATES:
            print("The execution is still running")
            time.sleep(sleep_timer)
            job_status = job.status()
            if sleep_timer < 10:
                sleep_timer = sleep_timer + 1

        return job.result().get_counts()
    except (JobError, JobTimeoutError):
        return None


def get_measurement_qubits_from_transpiled_circuit(transpiled_circuit):
    qubit_index, qubit_mappings = get_measured_qubits([transpiled_circuit])
    measurement_qubits = [int(i) for i in list(qubit_mappings.keys())[0].split("_")]

    return measurement_qubits
