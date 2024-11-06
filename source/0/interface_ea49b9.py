# https://github.com/ohadlev77/sat-circuits-engine/blob/6b913e2ef91190c929a77d03f9a959cbbb214193/sat_circuits_engine/interface/interface.py
#    Copyright 2022-2023 Ohad Lev.

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0,
#    or in the root directory of this package("LICENSE.txt").

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
`SATInterface` class.
"""

import os
import json
from typing import List, Tuple, Union, Optional, Dict, Any
from sys import stdout
from datetime import datetime
from hashlib import sha256

from qiskit import transpile, QuantumCircuit, qpy
from qiskit.result.counts import Counts
from qiskit.visualization.circuit.text import TextDrawing
from qiskit.providers.backend import Backend
from qiskit.transpiler.passes import RemoveBarriers
from IPython import display
from matplotlib.figure import Figure

from sat_circuits_engine.util import timer_dec, timestamp
from sat_circuits_engine.util.settings import DATA_PATH, TRANSPILE_KWARGS
from sat_circuits_engine.circuit import GroverConstraintsOperator, SATCircuit
from sat_circuits_engine.constraints_parse import ParsedConstraints
from sat_circuits_engine.interface.circuit_decomposition import decompose_operator
from sat_circuits_engine.interface.counts_visualization import plot_histogram
from sat_circuits_engine.interface.translator import ConstraintsTranslator
from sat_circuits_engine.classical_processing import (
    find_iterations_unknown,
    calc_iterations,
    ClassicalVerifier
)
from sat_circuits_engine.interface.interactive_inputs import (
    interactive_operator_inputs,
    interactive_solutions_num_input,
    interactive_run_input,
    interactive_backend_input,
    interactive_shots_input
)

# Local globlas for visualization of charts and diagrams
IFRAME_WIDTH = "100%"
IFRAME_HEIGHT = "500"

class SATInterface:
    """
    An interface for building, running and mining data from n-SAT problems quantum circuits.
    There are 2 options to use this class:

        (1) Using an interactive interface (intuitive but somewhat limited) - for this
        just initiate a bare instance of this class: `SATInterface()`.

        (2) Using the API defined by this class, that includes the following methods:
            * The following descriptions are partial, for full annotations see the methods' docstrings.
            - `__init__`: an instance of `SATInterface must be initiated with exactly 1 combination:
                (a) (high_level_constraints_string + high_level_vars) - for constraints
                in a high-level format.
                (b) (num_input_qubits + constraints_string) - for constraints
                in a low-level foramt.
                * For formats annotations see `constriants_format.ipynb` in the main directory.
            - `obtain_grover_operator`: obtains the suitable grover operator for the constraints.
            - `save_display_grover_operator`: saves and displays data generated
            by the `obtain_grover_operator` method.
            - `obtain_overall_circuit`: obtains the suitable overall SAT circuit.
            - `save_display_overall_circuit: saves and displays data generated
            by the `obtain_overall_circuit` method.
            - `run_overall_circuit`: executes the overall SAT circuit.
            - `save_display_results`: saves and displays data generated
            by the `run_overall_circuit` method.
    
    It is very recommended to go through `demos.ipynb` that demonstrates the various optional uses
    of this class, in addition to reading `constraints_format.ipynb`, which is a must for using
    this package properly. Both notebooks are in ther main directory.
    """

    def __init__(
        self,
        num_input_qubits: Optional[int] = None,
        constraints_string: Optional[str] = None,
        high_level_constraints_string: Optional[str] = None,
        high_level_vars: Optional[Dict[str, int]] = None,
        name: Optional[str] = None,
        save_data: Optional[bool] = True
    ) -> None:
        """
        Accepts the combination of paramters:
        (high_level_constraints_string + high_level_vars) or (num_input_qubits + constraints_string).
        Exactly one combination is accepted.
        In other cases either an iteractive user interface will be called to take user's inputs,
        or an exception will be raised due to misuse of the API.

        Args:
            num_input_qubits (Optional[int] = None): number of input qubits.
            constraints_string (Optional[str] = None): a string of constraints in a low-level format.

            high_level_constraints_string (Optional[str] = None): a string of constraints in a
            high-level format.
            high_level_vars (Optional[Dict[str, int]] = None): a dictionary that configures
            the high-level variables - keys are names and values are bits-lengths.

            name (Optional[str] = None): a name for this object, if None than the
            generic name "SAT" is given automatically.
            save_data (Optional[bool] = True): if True, saves all data and metadata generated by this
            class to a unique data folder (by using the `save_XXX` methods of this class).

        Raises:
            SyntaxError - if a forbidden combination of arguments has been provided.
        """

        if name is None:
            name = "SAT"
        self.name = name

        # Creating a directory for data to be saved
        if save_data:
            self.time_created = timestamp(datetime.now())
            self.dir_path = f"{DATA_PATH}{self.time_created}_{self.name}/"
            os.mkdir(self.dir_path)
            print(f"Data will be saved into '{self.dir_path}'.")

            # Initial metadata, more to be added by this class' `save_XXX` methods
            self.metadata = {
                "name": self.name,
                "datetime": self.time_created,
                "num_input_qubits": num_input_qubits,
                "constraints_string": constraints_string,
                "high_level_constraints_string": high_level_constraints_string,
                "high_level_vars": high_level_vars
            }
            self.update_metadata()

        # Identifying user's platform, for visualization purposes
        self.identify_platform()

        # Case A - interactive interface
        if (
            (num_input_qubits is None or constraints_string is None)
            and
            (high_level_constraints_string is None or high_level_vars is None)
        ):
            self.interactive_interface()

        # Case B - API
        else:
            self.high_level_constraints_string = high_level_constraints_string
            self.high_level_vars = high_level_vars

            # Case B.1 - high-level format constraints inputs
            if num_input_qubits is None or constraints_string is None:
                self.num_input_qubits = sum(self.high_level_vars.values())
                self.constraints_string = ConstraintsTranslator(
                    self.high_level_constraints_string,
                    self.high_level_vars
                ).translate()

            # Case B.2 - low-level format constraints inputs
            elif num_input_qubits is not None and constraints_string is not None:
                self.num_input_qubits = num_input_qubits
                self.constraints_string = constraints_string

            # Misuse
            else:
                raise SyntaxError(
                    "SATInterface accepts the combination of paramters:" \
                    "(high_level_constraints_string + high_level_vars) or " \
                    "(num_input_qubits + constraints_string). "\
                    "Exactly one combination is accepted, not both."
                )

            self.parsed_constraints = ParsedConstraints(
                self.constraints_string,
                self.high_level_constraints_string
            )

    def update_metadata(self, update_metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Updates the metadata file (in the unique data folder of a given `SATInterface` instance).

        Args:
            update_metadata (Optional[Dict[str, Any]] = None):
                - If None - just dumps `self.metadata` into the metadata JSON file.
                - If defined - updates the `self.metadata` attribute and then dumps it.
        """

        if update_metadata is not None:
            self.metadata.update(update_metadata)    

        with open(f"{self.dir_path}metadata.json", "w") as metadata_file:
            json.dump(self.metadata, metadata_file, indent=4)

    def identify_platform(self) -> None:
        """
        Identifies user's platform.
        Writes True to `self.jupyter` for Jupyter notebook, False for terminal.
        """
        
        # If True then the platform is a terminal/command line/shell
        if stdout.isatty():
            self.jupyter = False

        # If False, we assume the platform is a Jupyter notebook
        else:
            self.jupyter = True

    def output_to_platform(
        self,
        *,
        title: str,
        output_terminal: Union[TextDrawing, str],
        output_jupyter: Union[Figure, str],
        display_both_on_jupyter: Optional[bool] = False
    ) -> None:
        """
        Displays output to user's platform.

        Args:
            title (str): a title for the output.
            output_terminal (Union[TextDrawing, str]): text to print for a terminal platform.
            output_jupyter: (Union[Figure, str]): objects to display for a Jupyter notebook platform.
            can handle `Figure` matplotlib objects or strings of paths to IFrame displayable file,
            e.g PDF files.
            display_both_on_jupyter (Optional[bool] = False): if True, displays both
            `output_terminal` and `output_jupyter` in a Jupyter notebook platform.

        Raises:
            TypeError - in the case of misusing the `output_jupyter` argument.
        """

        print()
        print(title)

        if self.jupyter:
            if isinstance(output_jupyter, str):
                display.display(
                    display.IFrame(output_jupyter, width=IFRAME_WIDTH, height=IFRAME_HEIGHT)
                )
            elif isinstance(output_jupyter, Figure):
                display.display(output_jupyter)
            else:
                raise TypeError(
                    "output_jupyter must be an str (path to image file) or a Figure object."
                )

            if display_both_on_jupyter:
                print(output_terminal)
        else:
            print(output_terminal)

    def interactive_interface(self) -> None:
        """
        An interactive CLI that allows exploiting most (but not all) of the package's features.
        Uses functions of the form `interactive_XXX_inputs` from the `interactive_inputs.py` module.

        Divided into 3 main stages:
            1. Obtaining Grover's operator for the SAT problem.
            2. Obtaining the overall SAT cirucit.
            3. Executing the circuit and parsing the results.

        The interface is built in a modular manner such that a user can halt at any stage.

        The defualt settings for the interactive user intreface are:
            1. `name = "SAT"`.
            2. `save_data = True`.
            3. `display = True`.
            4. `transpile_kwargs = {'basis_gates': ['u', 'cx'], 'optimization_level': 3}`.
            5. Backends are limited to those defined in the global-constant-like function `BACKENDS`:
                - Those are the local `aer_simulator` and the remote `ibmq_qasm_simulator` for now.

        Due to these default settings the interactive CLI is somewhat restrictive,
        for full flexibility a user should use the API and not the CLI.
        """

        # Handling operator part
        operator_inputs = interactive_operator_inputs()
        self.num_input_qubits = operator_inputs['num_input_qubits']
        self.constraints_string = operator_inputs['constraints_string']
        self.high_level_constraints_string = operator_inputs['high_level_constraints_string']
        self.high_level_vars = operator_inputs['high_level_vars']

        self.parsed_constraints = ParsedConstraints(
            self.constraints_string,
            self.high_level_constraints_string
        )
        
        self.update_metadata({
            "num_input_qubits": self.num_input_qubits,
            "constraints_string": self.constraints_string,
            "high_level_constraints_string": self.high_level_constraints_string,
            "high_level_vars": self.high_level_vars
        })

        obtain_grover_operator_output = self.obtain_grover_operator()
        self.save_display_grover_operator(obtain_grover_operator_output)

        # Handling overall circuit part
        solutions_num = interactive_solutions_num_input()

        if solutions_num is not None:
            backend = None
            if solutions_num == -1:
                backend = interactive_backend_input()

            overall_circuit_data = self.obtain_overall_sat_circuit(
                obtain_grover_operator_output['operator'],
                solutions_num,
                backend
            )
            self.save_display_overall_circuit(overall_circuit_data)

            # Handling circuit execution part
            if interactive_run_input():
                if backend is None:
                    backend = interactive_backend_input()

                shots = interactive_shots_input()

                counts_parsed = self.run_overall_sat_circuit(
                    overall_circuit_data['circuit'],
                    backend,
                    shots
                )
                self.save_display_results(counts_parsed)

        print()
        print(f"Done saving data into '{self.dir_path}'.")

    def obtain_grover_operator(
        self,
        transpile_kwargs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Union[GroverConstraintsOperator, QuantumCircuit]]:
        """
        Obtains the suitable `GroverConstraintsOperator` object for the constraints,
        decomposes it using the `circuit_decomposition.py` module and transpiles it
        according to `transpile_kwargs`.
        
        Args:
            transpile_kwargs (Optional[Dict[str, Any]]): keyword arguments for Qiskit's transpile function.
            The defualt is set to the global constant `TRANSPILE_KWARGS`.

        Returns:
            (Dict[str, Union[GroverConstraintsOperator, QuantumCircuit]]):
                - 'operator' - the high-level bloks operator.
                - 'decomposed_operator' - decomposed to building-blocks operator.
                    * For annotations regarding the decomposition method see the
                    `circuit_decomposition` module.
                - 'transpiled_operator' - the transpiled operator.
                *** The high-level operator and the decomposed operator are generated with barriers
                between constraints as default for visualizations purposes. The barriers are stripped
                off before transpiling so the the transpiled operator object contains no barriers. ***
        """

        print()
        print(
            "The system synthesizes and transpiles a Grover's " \
            "operator for the given constraints. Please wait.."
        )

        if transpile_kwargs is None:
            transpile_kwargs = TRANSPILE_KWARGS
        self.transpile_kwargs = transpile_kwargs

        operator = GroverConstraintsOperator(
            self.parsed_constraints,
            self.num_input_qubits,
            insert_barriers=True
        )
        decomposed_operator = decompose_operator(operator)
        no_baerriers_operator = RemoveBarriers()(operator)
        transpiled_operator = transpile(no_baerriers_operator, **transpile_kwargs)

        print("Done.")

        return {
            'operator': operator,
            'decomposed_operator': decomposed_operator,
            'transpiled_operator': transpiled_operator,
        }

    def save_display_grover_operator(
        self,
        obtain_grover_operator_output: Dict[str, Union[GroverConstraintsOperator, QuantumCircuit]],
        display: Optional[bool] = True
    ) -> None:
        """
        Handles saving and displaying data generated by the `self.obtain_grover_operator` method.

        Args:
            obtain_grover_operator_output(Dict[str, Union[GroverConstraintsOperator, QuantumCircuit]]):
            the dictionary returned upon calling the `self.obtain_grover_operator` method.
            display (Optional[bool] = True) - If true, displays objects to user's platform.
        """

        # Creating a directory to save operator's data
        operator_dir_path = f"{self.dir_path}grover_operator/"
        os.mkdir(operator_dir_path)

        # Titles for displaying objects, by order of `obtain_grover_operator_output`
        titles = [
            "The operator diagram - high level blocks:",
            "The operator diagram - decomposed:",
            f"The transpiled operator diagram saved into '{operator_dir_path}'.\n" \
            f"It's not presented here due to its complexity.\n" \
            f"Please note that barriers appear in the high-level diagrams above only for convenient\n" \
            f"visual separation between constraints.\n" \
            f"Before transpilation all barriers are removed to avoid redundant inefficiencies."
        ]

        for index, (op_name, op_obj) in enumerate(obtain_grover_operator_output.items()):

            # Generic path and name for files to be saved
            files_path = f"{operator_dir_path}{op_name}"

            # Generating a circuit diagrams figure
            figure_path = f"{files_path}.pdf"
            op_obj.draw('mpl', filename=figure_path, fold=-1)

            # Generating a QPY serialization file for the circuit object
            qpy_file_path = f"{files_path}.qpy"
            with open(qpy_file_path, "wb") as qpy_file:
                qpy.dump(op_obj, qpy_file)

            # Original high-level operator and decomposed operator
            if index < 2 and display:

                # Displaying to user
                self.output_to_platform(
                    title=titles[index],
                    output_terminal=op_obj.draw('text'),
                    output_jupyter=figure_path
                )

            # Transpiled operator
            elif index == 2:

                # Output to user, not including the circuit diagram
                print()
                print(titles[index])

                print()
                print(f"The transpilation kwargs are: {self.transpile_kwargs}.")
                transpiled_operator_depth = op_obj.depth()
                transpiled_operator_gates_count = op_obj.count_ops()
                print(f"Transpiled operator depth: {transpiled_operator_depth}.")
                print(f"Transpiled operator gates count: {transpiled_operator_gates_count}.")
                print(f"Total number of qubits: {op_obj.num_qubits}.")

                # Generating QASM 2.0 file only for the tranpsiled operator
                qasm_file_path = f"{files_path}.qasm"
                op_obj.qasm(filename=qasm_file_path)
            
        print()
        print(
            f"Saved into '{operator_dir_path}':\n",
            f"  Circuit diagrams for all levels.\n",
            f"  QPY serialization exports for all levels.\n",
            f"  QASM 2.0 export only for the transpiled level."
        )

        with open(f"{operator_dir_path}operator.qpy", "rb") as qpy_file:
            operator_qpy_sha256 = sha256(qpy_file.read()).hexdigest()

        self.update_metadata({
            "transpile_kwargs": self.transpile_kwargs,
            "transpiled_operator_depth": transpiled_operator_depth,
            "transpiled_operator_gates_count": transpiled_operator_gates_count,
            "operator_qpy_sha256": operator_qpy_sha256,
        })

    def obtain_overall_sat_circuit(
        self,
        grover_operator: GroverConstraintsOperator,
        solutions_num: int,
        backend: Optional[Backend] = None
    ) -> Dict[str, SATCircuit]:
        """
        Obtains the suitable `SATCircuit` object (= the overall SAT circuit) for the SAT problem.
        
        Args:
            grover_operator (GroverConstraintsOperator): Grover's operator for the SAT problem.
            solutions_num (int): number of solutions for the SAT problem. In the case the number
            of solutions is unknown, specific negative values are accepted:
                * '-1' - for launching a classical iterative stochastic process that finds an adequate
                number of iterations - by calling the `find_iterations_unknown` function (see its
                docstrings for more information).
                * '-2' - for generating a dynamic circuit that iterates over Grover's iterator until
                a solution is obtained, using weak measurements. TODO - this feature isn't ready yet.
            backend (Optional[Backend] = None): in the case of a '-1' value given to `solutions_num`,
            a backend object to execute the depicted iterative prcess upon should be provided.

        Returns:
            (Dict[str, SATCircuit]):
                - 'circuit' key for the overall SAT circuit.
                - 'concise_circuit' key for the overall SAT circuit, with only 1 iteration over Grover's
                iterator (operator + diffuser). Useful for visualization purposes.
                *** The concise circuit is generated with barriers between segments as default
                for visualizations purposes. In the actual circuit there no barriers. ***
        """

        # -1 = Unknown number of solutions - iterative stochastic process
        print()
        if solutions_num == -1:
            assert backend is not None, "Need to specify a backend if `solutions_num == -1`."

            print("Please wait while the system checks various solutions..")
            circuit, iterations = find_iterations_unknown(
                self.num_input_qubits,
                grover_operator,
                self.parsed_constraints,
                precision=10,
                backend=backend
            )
            print()
            print(f"An adequate number of iterations found = {iterations}.")
        
        # -2 = Unknown number of solutions - implement a dynamic circuit
        # TODO this feature isn't fully implemented yet
        elif solutions_num == -2:
            print("The system builds a dynamic circuit..")

            circuit = SATCircuit(self.num_input_qubits, grover_operator, iterations=None)
            circuit.add_input_reg_measurement()

            iterations = None

        # Known number of solutions
        else:
            print("The system builds the overall circuit..")

            iterations = calc_iterations(self.num_input_qubits, solutions_num)
            print(f"\nFor {solutions_num} solutions, {iterations} iterations needed.")

            circuit = SATCircuit(
                self.num_input_qubits,
                grover_operator,
                iterations,
                insert_barriers=False
            )
            circuit.add_input_reg_measurement()

        self.iterations = iterations

        # Obtaining a SATCircuit object with one iteration for concise representation
        concise_circuit = SATCircuit(
            self.num_input_qubits,
            grover_operator,
            iterations=1,
            insert_barriers=True
        )
        concise_circuit.add_input_reg_measurement()

        return {'circuit': circuit, 'concise_circuit': concise_circuit}

    def save_display_overall_circuit(
        self,
        obtain_overall_sat_circuit_output: Dict[str, SATCircuit],
        display: Optional[bool] = True
    ) -> None:
        """
        Handles saving and displaying data generated by the `self.obtain_overall_sat_circuit` method.

        Args:
            obtain_overall_sat_circuit_output(Dict[str, SATCircuit]):
            the dictionary returned upon calling the `self.obtain_overall_sat_circuit` method.
            display (Optional[bool] = True) - If true, displays objects to user's platform.
        """

        circuit = obtain_overall_sat_circuit_output['circuit']
        concise_circuit = obtain_overall_sat_circuit_output['concise_circuit']

        # Creating a directory to save overall circuit's data
        overall_circuit_dir_path = f"{self.dir_path}overall_circuit/"
        os.mkdir(overall_circuit_dir_path)

        # Generating a figure of the overall SAT circuit with just 1 iteration (i.e "concise")
        concise_circuit_fig_path = f"{overall_circuit_dir_path}overall_circuit_1_iteration.pdf"
        concise_circuit.draw('mpl', filename=concise_circuit_fig_path ,fold=-1)

        # Displaying the concise circuit to user
        if display:
            if self.iterations:
                self.output_to_platform(
                    title= (
                        f"The high level circuit contains {self.iterations}" \
                        f" iterations of the following form:"
                    ),
                    output_terminal=concise_circuit.draw("text"),
                    output_jupyter=concise_circuit_fig_path
                )
            
            # Dynamic circuit case - TODO NOT FULLY IMPLEMENTED YET
            else:
                dynamic_circuit_fig_path = f"{overall_circuit_dir_path}overall_circuit_dynamic.pdf"
                circuit.draw('mpl', filename=dynamic_circuit_fig_path ,fold=-1)

                self.output_to_platform(
                    title="The dynamic circuit diagram:",
                    output_terminal=circuit.draw("text"),
                    output_jupyter=dynamic_circuit_fig_path
                )

        print()
        print("Exporting the full high-level overall SAT circuit object to a QPY file..")
        qpy_file_path = f"{overall_circuit_dir_path}overall_circuit.qpy"
        with open(qpy_file_path, "wb") as qpy_file:
            qpy.dump(circuit, qpy_file)

        print()
        print(
            f"Saved into '{overall_circuit_dir_path}':\n",
            f"  A concised (1 iteration) circuit diagram of the high-level overall SAT circuit.\n",
            f"  QPY serialization export for the full overall SAT circuit object."
        )

        self.update_metadata({
            "num_total_qubits": circuit.num_qubits,
            "num_iterations": circuit.iterations,
        })
        
    @timer_dec("Circuit simulation execution time = ")
    def run_overall_sat_circuit(
        self,
        circuit: QuantumCircuit,
        backend: Backend,
        shots: int
    ) -> Dict[str, Union[Counts, List[Tuple[Union[str, int]]], List[str], List[Dict[str, int]]]]:
        """
        Executes a `circuit` on `backend` transpiled w.r.t backend, `shots` times.

        Args:
            circuit (QuantumCircuit): `QuantumCircuit` object or child-object (a.k.a `SATCircuit`)
            to execute.
            backend (Backend): backend to execute `circuit` upon.
            shots (int): number of execution shots.

        Returns:
            (Dict[str, Union[Counts, List[Tuple[Union[str, int]]], List[str], List[Dict[str, int]]]]):
            dict object returned by `self.parse_counts` - see this method's docstrings for annotations.
        """

        # Defines also instance attributes to use in other methods
        self.backend = backend
        self.shots = shots

        print()
        print(f"The system is running the circuit {shots} times on {backend}, please wait..")
        print("This process might take a while.")

        job = backend.run(transpile(circuit, backend), shots=shots)
        counts = job.result().get_counts()
        print("Done.")

        parsed_counts = self.parse_counts(counts)
        return parsed_counts

    def parse_counts(
        self,
        counts: Counts
    ) -> Dict[str, Union[Counts, List[Tuple[Union[str, int]]], List[str], List[Dict[str, int]]]]:
        """
        Parses a `Counts` object into several desired datas (see 'Returns' section).

        Args:
            counts (Counts): the `Counts` object to parse.

        Returns:
            (Dict[str, Union[Counts, List[Tuple[Union[str, int]]], List[str], List[Dict[str, int]]]]):
                'counts' (Counts) - the original `Counts` object.
                'counts_sorted' (List[Tuple[Union[str, int]]]) - results sorted in a descending order.
                'distilled_solutions' (List[str]): list of solutions (bitstrings).
                'high_level_vars_values' (List[Dict[str, int]]): list of solutions (dictionaries of
                variable-names and their integer values).
        """

        # Sorting results in an a descending order
        counts_sorted = sorted(counts.items(), key=lambda x: x[1], reverse=True)

        # Generating a set of distilled verified-only solutions
        verifier = ClassicalVerifier(self.parsed_constraints)
        distilled_solutions = set()
        for count_item in counts_sorted:
            if not verifier.verify(count_item[0]):
                break
            distilled_solutions.add(count_item[0])

        # In the case of high-level format in use, translating `distilled_solutions` into integer values
        high_level_vars_values = None
        if self.high_level_constraints_string and self.high_level_vars:

            # Container for dictionaries with variables integer values
            high_level_vars_values = []

            for solution in distilled_solutions:

                # Keys are variable-names and values are their integer values
                solution_vars = {}
                for index, (var, size) in enumerate(self.high_level_vars.items()):

                    # Defining the first and last bits
                    start_index = sum(list(self.high_level_vars.values())[:index])
                    end_index = start_index + size

                    # Translating to integer value while sticking to little-endian convention
                    solution_vars[var] = int(solution[::-1][start_index:end_index][::-1], 2)

                high_level_vars_values.append(solution_vars)

        return {
            'counts': counts,
            'counts_sorted': counts_sorted,
            'distilled_solutions': distilled_solutions,
            'high_level_vars_values': high_level_vars_values
        }
    
    def save_display_results(
        self,
        run_overall_sat_circuit_output: Dict[
            str, Union[Counts, List[Tuple[Union[str, int]]], List[str], List[Dict[str, int]]]
        ],
        display: Optional[bool] = True
    ) -> None:
        """
        Handles saving and displaying data generated by the `self.run_overall_sat_circuit` method.

        Args:
            run_overall_sat_circuit_output (Dict[str, Union[Counts, List[Tuple[Union[str, int]]],
            List[str], List[Dict[str, int]]]]): the dictionary returned upon calling
            the `self.run_overall_sat_circuit` method.
            display (Optional[bool] = True) - If true, displays objects to user's platform.
        """
        
        counts = run_overall_sat_circuit_output['counts']
        counts_sorted = run_overall_sat_circuit_output['counts_sorted']
        distilled_solutions = run_overall_sat_circuit_output['distilled_solutions']
        high_level_vars_values = run_overall_sat_circuit_output['high_level_vars_values']

        # Creating a directory to save results data
        results_dir_path = f"{self.dir_path}results/"
        os.mkdir(results_dir_path)

        # Defining custom dimensions for the custom `plot_histogram` of this package
        histogram_fig_width = max((len(counts) * self.num_input_qubits * (10 / 72)), 7)
        histogram_fig_height = 5
        histogram_figsize = (histogram_fig_width, histogram_fig_height)

        histogram_path = f"{results_dir_path}histogram.pdf"
        plot_histogram(
            counts,
            figsize=histogram_figsize,
            sort='value_desc',
            filename=histogram_path
        )

        if display:

            # Basic output text
            output_text = f"All counts:\n{counts_sorted}\n" \
                          f"\nDistilled solutions ({len(distilled_solutions)} total):\n" \
                          f"{distilled_solutions}"

            # For a high-level constraints format, actual integer solutions will be displayed as well
            if high_level_vars_values:

                additional_text = ""
                for solution_index, solution in enumerate(high_level_vars_values):
                    additional_text += f"Solution {solution_index + 1}: "

                    for var_index, (var, value) in enumerate(solution.items()):
                        additional_text += f"{var} = {value}"

                        if var_index != len(solution) - 1:
                            additional_text += ", "
                        else:
                            additional_text += "\n"

                output_text += f"\n\nHigh-level format solutions: \n{additional_text}"
                          
            self.output_to_platform(
                title=f"The results for {self.shots} shots are:",
                output_terminal=output_text,
                output_jupyter=histogram_path,
                display_both_on_jupyter=True
            )

        results_dict = {
            'solutions': list(distilled_solutions),
            'high_level_solutions': high_level_vars_values,
            'counts': counts_sorted
        }
        with open(f"{results_dir_path}results.json", "w") as results_file:
            json.dump(results_dict, results_file, indent=4)

        self.update_metadata({
            "num_solutions": len(distilled_solutions),
            "backend": self.backend.__str__(),
            "shots": self.shots
        })