# https://github.com/AndersHR/quantum_error_mitigation/blob/8aa0806b1433ad420251bc9b6dd25f47f8e08e15/zero_noise_extrapolation_cnot.py
from qiskit import QuantumCircuit, execute, Aer, transpile

from qiskit.transpiler import PassManager, PassManagerConfig, CouplingMap
from qiskit.transpiler.passes import Unroller, Optimize1qGates
from qiskit.transpiler.preset_passmanagers.level3 import level_3_pass_manager

from numpy import asarray, ndarray, shape, zeros, empty, average, transpose, dot
from numpy.linalg import solve

import random


"""
-- ZERO NOISE EXTRAPOLATION for CNOT-gates --

This implemention does quantum error mitigation using the method of zero noise extrapolation, by amplifying noise in
a quantum circuit by a set of noise amplification factors, then using Richardson extrapolation to extrapolate the
expectation value to the zero-noise limit.

The noise amplified and mitigated is specifically noise in CNOT-gates. The noise is amplified by n amplification
factors c=1, 3, 5, ..., 2n + 1 by repeating each CNOT gates c times. E.g. c=1 corresponds to the bare circuit and
c=3 corresponds to each CNOT gate replaced by CNOT*CNOT*CNOT. Each CNOT acting on the same control- and target-qubits
as the original CNOT-gate.

As CNOT*CNOT = Id, the identity, in the noise-free case the amplified CNOT (eqaul to CNOT^c) have the same action as a
single CNOT. In the noise-afflicted case, the action will be close to that of a single CNOT for a weak noise, but with
the CNOT-noise applied c times to the qubit throughout the process.

"""


class ZeroNoiseExtrapolation:

    def __init__(self, qc: QuantumCircuit, exp_val_func, backend=None, noise_model=None,
                 n_amp_factors: int = 3, pauli_twirl: bool = False, shots: int = 8192,
                 pass_manager: PassManager = None):
        """ CONSTRUCTOR
        :param qc: The circuit to be mitigated
        :param exp_val_func: A function which computes the observed expectation value of some operator as a function of
                             the measurement counts from the circuit qc
        :param backend: The backend on which to execute the circuit
        :param noise_model: Optinal custom noise model for execution on a simulator backend
        :param n_amp_factors: Number of amplification factors to be used. For n amplification factors, the
                              amplification factors will be 1,3,5,...,2n + 1
        :param pauli_twirl: Do pauli twirl True / False
        :param shots: Number of shots of the circuit to execute
        :param pass_manager: Optional custom pass manager to use when transpiling the circuit
        """

        if backend == None:
            self.backend = Aer.get_backend("qasm_simulator")
            self.is_simulator = True
        else:
            self.backend = backend
            self.is_simulator = backend.configuration().simulator

        # Do an initial optimization of the quantum circuit. If no custom pass manager is passer, the optimizaiton is
        # done with the optimization_level=3 preset for the qiskit transpiler (heaviest optimization)
        self.qc = self.transpile_circuit(qc, custom_pass_manager=pass_manager)

        self.exp_val_func = exp_val_func

        self.noise_model = noise_model

        self.n_amp_factors = n_amp_factors
        self.noise_amplification_factors = asarray([(1 + 2*i) for i in range(0, n_amp_factors)])

        self.pauli_twirl = pauli_twirl

        # Max number of shots for one circuit execution on IBMQ devices is 8192.
        # To do more shots, we have to partition them up into several executions.
        if shots <= 8192:
            self.num_executions = 1
            self.shots = shots
        else:
            self.num_executions = (shots // 8192) + 1
            self.shots = int(shots / self.num_executions)

        # Initialization of variables for later use:

        self.counts = []

        self.depths = empty(n_amp_factors)

        self.bare_exp_vals = zeros(0)
        self.all_exp_vals = zeros(0)
        self.mitigated_exp_vals = zeros(0)

        self.measurement_results = []

    def set_shots(self, shots: int):
        if shots <= 8192:
            self.num_executions = 1
            self.shots = shots
        else:
            self.num_executions = (shots // 8192) + 1
            self.shots = int(shots / self.num_executions)

    def noise_amplify_and_pauli_twirl_cnots(self, qc: QuantumCircuit, amp_factor: int,
                                            pauli_twirl: bool) -> QuantumCircuit:
        """
        Amplify CNOT-noise by extending each CNOT-gate as CNOT^amp_factor and possibly Pauli-twirl all CNOT-gates

        Using CNOT*CNOT = I, the identity, and an amp_factor = (2*n + 1) for an integer n, then the
        extended CNOT will have the same action as a single CNOT, but with the noise amplified by
        a factor amp_factor.

        :param qc: Quantum circuit for which to Pauli twirl all CNOT gates and amplify CNOT-noise
        :param amp_factor: The noise amplification factor, must be (2n + 1) for n = 0,1,2,3,...
        :param pauli_twirl: Add pauli twirling True / False
        :return: Noise-amplified and possibly Pauli-twirled Quantum Circuit
        """

        if (amp_factor - 1) % 2 != 0:
            raise Exception("Invalid amplification factors", amp_factor)

        # The circuit may be expressed in terms of various types of gates.
        # The 'Unroller' transpiler pass 'unrolls' (decomposes) the circuit gates to be expressed in terms of the
        # physical gate set [u1,u2,u3,cx]

        # The cz, cy (controlled-Z and -Y) gates can be constructed from a single cx-gate and sinlge-qubit gates.
        # For backends with native gate sets consisting of some set of single-qubit gates and either the cx, cz or cy,
        # unrolling the circuit to the ["u3", "cx"] basis, amplifying the cx-gates, then unrolling back to the native
        # gate set and doing a single-qubit optimization transpiler pass, is thus still general.

        unroller_ugatesandcx = Unroller(["u1","u2","u3","cx"])
        pm = PassManager(unroller_ugatesandcx)

        unrolled_qc = pm.run(qc)

        circuit_qasm = unrolled_qc.qasm()
        new_circuit_qasm_str = ""

        qreg_name = find_qreg_name(circuit_qasm)

        for i, line in enumerate(circuit_qasm.splitlines()):
            if line[0:2] == "cx":
                for j in range(amp_factor):
                    if pauli_twirl:
                        new_circuit_qasm_str += pauli_twirl_cnot_gate(qreg_name, line)
                    else:
                        new_circuit_qasm_str += (line + "\n")
            else:
                new_circuit_qasm_str += line + "\n"

        new_qc = QuantumCircuit.from_qasm_str(new_circuit_qasm_str)

        # The "Optimize1qGates" transpiler pass optimizes adjacent single-qubit gates, for a native gate set with the
        # u3 gates it collapses any chain of adjacent single-qubit gates into a single, equivalent u3-gate.
        # We want to collapse unnecessary single-qubit gates to minimize circuit depth, but not CNOT-gates
        # as these give us the noise amplification.
        unroller_backendspecific = Unroller(self.backend.configuration().basis_gates)
        optimize1qates = Optimize1qGates()

        pm = PassManager([unroller_backendspecific, optimize1qates])

        return pm.run(new_qc)

    def transpile_circuit(self, qc: QuantumCircuit, custom_pass_manager: PassManager = None) -> QuantumCircuit:
        """
        Transpile and optimize the input circuit, optionally using a custom pass manager.
        If no custom pass manager is given, use the optimization_level 3 preset for the qiskit transpiler,
        which gives heaviest circuit optimization.

        As we want to add additional CNOTs for noise amplification and possibly additional single qubit gates
        for Pauli twirling, we need to transpile the circuit before both the noise amplification is applied and
        before circuit execution. This is to avoid the additional CNOT-gates beinng removed by the transpiler.

        The Optimize1qGates transpiler pass will be used later to optimize single qubit gates added during
        the Pauli-twirling, as well as the Unroller pass which merely decomposes the given circuit gates into
        the given set of basis gates.

        :return: The transpiled circuit
        """

        if custom_pass_manager == None:
            pass_manager_config = PassManagerConfig(basis_gates=["id", "u1", "u2", "u3", "cx"],
                                                    backend_properties=self.backend.properties())
            if not self.is_simulator:
                pass_manager_config.coupling_map = CouplingMap(self.backend.configuration().coupling_map)

            pass_manager = level_3_pass_manager(pass_manager_config)
        else:
            pass_manager = custom_pass_manager

        self.passes = pass_manager.passes() # Saves the list of passes used for transpiling

        return pass_manager.run(qc)

    def execute_circuits(self, circuits: list) -> list:
        """
        Execute all circuits and return measurement counts. If shots > 8192, we need to partition the execution
        into several sub-executions.

        Circuits are transpiled and optimized beforehand, thus we pass an empty PassManager to qiskit.execute
        to avoid unnecessary time spent on transpiling.

        :param circuits: All circuits to be executed
        :return: A list of count-dictionaries
        """

        # The max number of shots on a single execution on the IBMQ devices is 8192.
        # If shots > 8192, we have to partition the execution into several sub-executions.
        execution_circuits = []
        for qc in circuits:
            execution_circuits += [qc.copy() for i in range(self.num_executions)]

        # non-simulator backends throws unexpected argument when passing noise_model argument to them
        if self.is_simulator:
            result = execute(execution_circuits, backend=self.backend, noise_model=self.noise_model,
                             pass_manager=PassManager(), shots=self.shots).result()
        else:
            result = execute(execution_circuits, backend=self.backend,
                             pass_manager=PassManager(), shots=self.shots).result()

        self.measurement_results.append(result)    # Saving the result in a member variable. Might remove.

        return result.get_counts()

    def compute_exp_vals(self, counts: list) -> ndarray:
        """
        From the given exp_val_func, which computes the expectation value as a function of measurement counts, we
        compute the exp val of all executed circuits taking into account that we might have partitioned up circuit
        executions due to IBMQ's restriction of shots<=8192 per execution.

        :param counts: A list of measurement counts-dictionaries
        :return: A list of computed expectation values
        """

        n_distinct_circuits = int(len(counts) / self.num_executions)
        exp_vals = zeros(n_distinct_circuits, dtype=float)

        for i in range(n_distinct_circuits):
            exp_val_k = 0
            for k in range(self.num_executions):
                exp_val_k += self.exp_val_func(counts[i*self.num_executions + k])
            exp_vals[i] = exp_val_k / self.num_executions
        return exp_vals


    def mitigate(self, repeats: int = 1, verbose: bool = False) -> float:
        """


        :param repeats: Number of repeats of the extrapolation to perform. The result is averaged over all repeats.
        :param verbose: Prints during the computation, True / False
        :return: The mitigated expectation value
        """

        n_amp_factors = shape(self.noise_amplification_factors)[0]

        if verbose:
            print("repeats=", repeats ,", shots per repats=", self.shots, ", n_amp_factors=", self.n_amp_factors,
                  ", paulitwirl=", self.pauli_twirl, sep="")
            print("noise amplification factors=", self.noise_amplification_factors, sep="")

        if verbose:
            print("Constructing circuits")

        circuits = []

        for j, amp_factor in enumerate(self.noise_amplification_factors):
            circuits.append(self.noise_amplify_and_pauli_twirl_cnots(qc=self.qc, amp_factor=amp_factor,
                                                                     pauli_twirl=self.pauli_twirl))
            self.depths[j] = circuits[-1].depth()

        if repeats != 1:
            circuits = circuits * repeats

        if verbose:
            print("Depths=",self.depths, sep="")

            print("Executing circuits")

        counts = self.execute_circuits(circuits)

        self.counts = counts

        exp_vals = self.compute_exp_vals(counts)

        # Process the resulting expectation values:

        self.bare_exp_vals = zeros((repeats,))
        self.all_exp_vals = zeros((repeats,n_amp_factors))
        self.mitigated_exp_vals = zeros((repeats,))

        if verbose:
            print("Processing results")

        if repeats == 1:
            self.bare_exp_vals[0] = exp_vals[0]
            self.all_exp_vals[0,:] = exp_vals

            self.result = richardson_extrapolate(self.all_exp_vals[0,:], self.noise_amplification_factors)

            self.mitigated_exp_vals[0] = self.result
        else:
            for i in range(repeats):
                self.bare_exp_vals[i] = exp_vals[i*n_amp_factors]

                for j in range(n_amp_factors):
                    self.all_exp_vals[i, j] = exp_vals[i*n_amp_factors + j]

                mitigation_results = richardson_extrapolate(self.all_exp_vals[i, :], self.noise_amplification_factors)
                self.mitigated_exp_vals[i] = mitigation_results

            self.result = sum(self.mitigated_exp_vals) / shape(self.mitigated_exp_vals)[0]

        if verbose:
            print("Mitigation done. Result:")
            print("Bare exp val =", average(self.bare_exp_vals))
            print("Mitigated exp val =",self.result)

        return self.result


# PAULI TWIRLING AND NOISE AMPLIFICATION HELP FUNCTIONS

# Conversion from pauli x/y/z-gates to physical u1/u3-gates in correct OpenQASM-format
PHYSICAL_GATE_CONVERSION = {"X": "u3(pi,0,pi)", "Z": "u1(pi)", "Y": "u3(pi,pi/2,pi/2)"}


def find_qreg_name(circuit_qasm: str) -> str:
    """
    Finds the name of the quantum register in the circuit.

    :param circuit_qasm: OpenQASM string with instructions for the entire circuit
    :return: Name of the quantum register
    """
    for line in circuit_qasm.splitlines():
        if line[0:5] == "qreg ":
            qreg_name = ""
            for i in range(5,len(line)):
                if line[i] == "[" or line[i] == ";":
                    break
                elif line[i] != " ":
                    qreg_name += line[i]
            return qreg_name


def find_cnot_control_and_target(qasm_line: str) -> (int, int):
    """
    Find indices of control and target qubits for the CNOT-gate in question

    :param qasm_line: OpenQASM line containing the CNOT
    :return: Indices of control and target qubits
    """
    qubits = []
    for i, c in enumerate(qasm_line):
        if c == "[":
            qubit_nr = ""
            for j in range(i+1, len(qasm_line)):
                if qasm_line[j] == "]":
                    break
                qubit_nr += qasm_line[j]
            qubits.append(int(qubit_nr))
    return qubits[0], qubits[1]


def propagate(control_in: str, target_in: str):
    """
    Finds the c,d gates such that (a x b) CNOT (c x d) = CNOT for an ideal CNOT-gate, based on the a (control_in)
    and b (target_in) pauli gates by "propagating" the a,b gates over a CNOT-gate by the following identities:

    (X x I) CNOT = CNOT (X x X)
    (I x X) CNOT = CNOT (I x X)
    (Z x I) CNOT = CNOT (I x Z)
    (I x Z) CNOT = XNOT (Z x Z)

    Note that instead of Pauli-twirling with [X,Z,Y] we use [X,Z,XZ] where XZ = -i*Y.
    The inverse of XZ is ZX = -XZ = i*Y. The factors of plus minus i are global phase factors which can be ignored.

    :param control_in: Pauli gates on control qubit before CNOT
    :param target_in: Pauli gates on target qubit before CNOT
    :return: Equivalent Pauli gates on control and target qubits after CNOT
    """

    control_out, target_out = '', ''
    if 'X' in control_in:
        control_out += 'X'
        target_out += 'X'
    if 'X' in target_in:
        target_out += 'X'
    if 'Z' in control_in:
        control_out += 'Z'
    if 'Z' in target_in:
        control_out += 'Z'
        target_out += 'Z'

    # Pauli gates square to the identity, i.e. XX = I, ZZ = I
    # Remove all such occurences from the control & target out Pauli gate strings
    if 'ZZ' in control_out:
        control_out = control_out[:-2]
    if 'ZZ' in target_out:
        target_out = target_out[:-2]
    if 'XX' in control_out:
        control_out = control_out[2:]
    if 'XX' in target_out:
        target_out = target_out[2:]

    # If no Pauli gates remain then we have the identity gate I
    if control_out == '':
        control_out = 'I'
    if target_out == '':
        target_out = 'I'

    # The inverse of XZ is ZX, therefore we reverse the gate order to obtain the correct pauli gates c,d
    # such that (a x b) CNOT (c x d) = CNOT (c^-1 x d^-1) (c x d) = CNOT
    return control_out[::-1], target_out[::-1]


def apply_qasm_pauli_gate(qreg_name: str, qubit: int, pauli_gates: str):
    """
    Construct a OpenQASM-string with the instruction to apply the given pauli gates to
    the given qubit

    :param qreg_name: Name of quantum register
    :param qubit: Index of qubit
    :param pauli_gates: The Pauli gates to be applied
    :return: The OpenQASM-string with the instruction
    """
    new_qasm_line = ''
    for gate in pauli_gates:
        if gate != 'I':
            u_gate = PHYSICAL_GATE_CONVERSION[gate]
            new_qasm_line += u_gate + ' ' + qreg_name + '[' + str(qubit) + '];' + '\n'
    return new_qasm_line


def pauli_twirl_cnot_gate(qreg_name: str, qasm_line_cnot: str) -> str:
    """
    Pauli-twirl a CNOT-gate from the given OpenQASM string line containing the CNOT.
    This will look something like: cx q[0],q[1];

    :param qreg_name: Name of quantum register
    :param qasm_line_cnot: OpenQASM-line containing the CNOT to pauli twirl
    :return:
    """
    control, target = find_cnot_control_and_target(qasm_line_cnot)

    # Note: XZ = -i*Y, with inverse (XZ)^-1 = ZX = i*Y. This simplifies the propagation of gates a,b over the CNOT
    pauli_gates = ["I", "X", "Z", "XZ"]

    a = random.choice(pauli_gates)
    b = random.choice(pauli_gates)

    # Find gates such that:
    # (a x b) CNOT (c x d) = CNOT for an ideal CNOT-gate,
    # by propagating the Pauli gates through the CNOT

    c, d = propagate(a, b)

    new_qasm_line = apply_qasm_pauli_gate(qreg_name, control, a)
    new_qasm_line += apply_qasm_pauli_gate(qreg_name, target, b)
    new_qasm_line += qasm_line_cnot + '\n'
    new_qasm_line += apply_qasm_pauli_gate(qreg_name, target, d)
    new_qasm_line += apply_qasm_pauli_gate(qreg_name, control, c)

    return new_qasm_line


def pauli_twirl_cnots(qc: QuantumCircuit) -> QuantumCircuit:
    """
    General function for Pauli-twirling all CNOT-gates in a quantum circuit.
    Included for completeness.

    :param qc: quantum circuit for which to Pauli twirl all CNOT gates
    :return: Pauli twirled quantum circuit
    """

    # The circuit may be expressed in terms of various types of gates.
    # The 'Unroller' transpiler pass 'unrolls' the circuit to be expressed in terms of the
    # physical gate set [u1,u2,u3,cx]
    unroller = Unroller(["u1", "u2", "u3", "cx"])
    pm = PassManager(unroller)

    unrolled_qc = pm.run(qc)

    circuit_qasm = unrolled_qc.qasm()
    new_circuit_qasm_str = ""

    qreg_name = find_qreg_name(circuit_qasm)

    for i, line in enumerate(circuit_qasm.splitlines()):
        if line[0:2] == "cx":
            new_circuit_qasm_str += pauli_twirl_cnot_gate(qreg_name, line)
        else:
            new_circuit_qasm_str += line + "\n"

    new_qc = QuantumCircuit.from_qasm_str(new_circuit_qasm_str)

    # The "Optimize1qGates" transpiler pass optimizes chains of single-qubit gates by collapsing them into
    # a single, equivalent u3-gate

    # We want to avoid that the transpiler optimizes CNOT-gates, as the ancillary CNOT-gates must be kept
    # to keep the noise amplification

    optimize1qates = Optimize1qGates()
    pm = PassManager(optimize1qates)

    return pm.run(new_qc)


# Richardson extrapolation:
def richardson_extrapolate(E: ndarray, c: ndarray) -> float:
    """
    Code taken from github.com/OpenQuantumComputing/error_mitigation/ -> zero_noise_extrapolation.py and slightly modified
    :param E: Expectation values
    :param c: Noise amplification factors
    :return: Extrapolation to the zero-limit
    """
    if isinstance(E, list):
        E = asarray(E)
    if isinstance(E, list):
        c = asarray(c)

    n = E.shape[0]
    if c.shape[0] != n:
        raise ValueError('E and c must have the same dimension.')
    if n <= 1:
        raise ValueError('the dimension of E and c must be larger than 1.')
    A = zeros((n, n))
    b = zeros((n, 1))
    # must sum to 1
    A[0, :] = 1
    b[0] = 1
    for k in range(1, n):
        A[k, :] = c ** k
    x = solve(A, b)
    return dot(transpose(E), x)[0]