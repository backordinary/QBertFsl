# https://github.com/vivekkatial/HAQC/blob/e5d87531e26a4bfe0e414840879021f81255838a/maxcut_qaoa.py
"""
Solving different instance classes with QAOA and VQE in `qiskit`

Consider an $n$-node undirected graph $G = (V, E)$ where $|V| = n$ with edge weights $w_{ij} \geq 0$, $w_{ij} = w_{ji}$ for $(i, j) \in E$. A cut is defined as a partition of the original set $V$ into two subsets. The cost function to be optimized is in this case the sum of weights of edges connecting points in the two different subsets, crossing the cut.

Author: Vivek Katial
"""

import pylab
import numpy as np
import json
import networkx as nx
import random
import copy
import os

# useful additional packages
import numpy as np
import networkx as nx
import seaborn as sns
import time
import argparse
import mlflow

# Qiskit Imports
from qiskit import Aer
from qiskit.tools.visualization import plot_histogram
from qiskit.circuit.library import TwoLocal, EfficientSU2
from qiskit_optimization.applications import Maxcut, Tsp
from qiskit.algorithms import VQE, NumPyMinimumEigensolver, QAOA
from qiskit.algorithms.optimizers import SPSA
from qiskit.utils import algorithm_globals, QuantumInstance
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization.problems import QuadraticProgram
from qiskit.algorithms.optimizers import COBYLA, L_BFGS_B, SLSQP, SPSA, NELDER_MEAD

# Custom Imports
from qaoa_vrp.features.graph_features import *
from qaoa_vrp.exp_utils import (
    str2bool,
    make_temp_directory,
    to_snake_case,
    clean_parameters_for_logging,
)
from qaoa_vrp.generators.graph_instance import GraphInstance
from qaoa_vrp.plot.draw_networks import draw_graph

sns.set_theme()

import qiskit

print(qiskit.__version__)


def main(track_mlflow=False):
    if track_mlflow:
        # Configure MLFlow Stuff
        tracking_uri = os.environ["MLFLOW_TRACKING_URI"]
        experiment_name = "QAOA-Parameter"
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

    # Max Number of nodes
    MAX_N = 13
    # Min number of nodes
    MIN_N = 8
    # Number of repeated layers QAOA
    N_LAYERS = 3
    # Max iterations
    MAX_ITERATIONS = 2000
    # Number of restarts
    N_RESTARTS = 3

    for instance_size in range(MIN_N, MAX_N + 1):
        N = instance_size
        print("Running job on instance size of N={instance_size}")
        G_instances = []
        # Generating a graph of erdos renyi graph
        G_unif = GraphInstance(nx.erdos_renyi_graph(N, p=0.5), "Uniform Random")
        G_instances.append(G_unif)

        # Power-Law Tree
        G_pl_tree = GraphInstance(
            nx.random_powerlaw_tree(N, gamma=3, seed=None, tries=1000), "Power Law Tree"
        )
        G_instances.append(G_pl_tree)

        # Wattz-Strogatz Graph
        G_wattz = GraphInstance(
            nx.connected_watts_strogatz_graph(N, k=4, p=0.5),
            "Watts-Strogatz small world",
        )
        G_instances.append(G_wattz)

        # Geometric Graphs
        connected = False
        geom_guess = 0
        while connected is False:
            geom_guess += 1
            # Use a radius that is connected 95% of the time
            random_radius = random.uniform(0.24, np.sqrt(2))
            g_geom = nx.random_geometric_graph(N, radius=random_radius)
            connected = nx.algorithms.components.is_connected(g_geom)
            print(
                f"Guess {geom_guess} for producing a connected Geometric Graph with r={random_radius} - connected: {connected}"
            )

        G_geom = GraphInstance(g_geom, "Geometric")
        G_instances.append(G_geom)

        # Create a nearly compelte bi partite graph
        # Randomly generate the size of one partiton
        n_part_1 = random.randint(1, N - 1)
        n_part_2 = N - n_part_1
        G_nc_bipart = GraphInstance(
            nx.complete_bipartite_graph(n_part_1, n_part_2), "Nearly Complete BiPartite"
        )
        G_nc_bipart.nearly_complete()
        G_instances.append(G_nc_bipart)

        # Create a 3-regular graph (based on https://arxiv.org/pdf/2106.10055.pdf)
        if instance_size % 2 == 0:
            G_three_regular = GraphInstance(
                nx.random_regular_graph(d=3, n=N), graph_type="3-Regular Graph"
            )
            G_instances.append(G_three_regular)

        # Create a 4-regular graph (based on https://arxiv.org/pdf/1908.08862.pdf)
        G_four_regular = GraphInstance(
            nx.random_regular_graph(d=4, n=N), graph_type="4-Regular Graph"
        )
        G_instances.append(G_four_regular)

        for i, graph_instance in enumerate(G_instances):
            print(
                f"\n{'-'*50}\nRunning Experiment for {graph_instance.graph_type} of size {instance_size}\n{'-'*50}\n"
            )
            print(
                f"Instance Features for {graph_instance.graph_type} of size {instance_size}\n{'-'*50}\n"
            )
            # Show instance features
            graph_features = get_graph_features(graph_instance.G)
            instance_type_logging = to_snake_case(graph_instance.graph_type)
            graph_features = {
                f"{instance_type_logging}_{str(key)}_size_{instance_size}": val
                for key, val in graph_features.items()
            }
            if track_mlflow:
                mlflow.log_params(graph_features)
            print(f"Solving Brute Force for {graph_instance.graph_type}\n{'-'*50}\n")
            G = graph_instance

            print(G)
            G.allocate_random_weights()
            G.compute_weight_matrix()
            print(G.weight_matrix)
            G = graph_instance.G
            w = graph_instance.weight_matrix
            n = len(G.nodes())

            best_cost_brute = 0
            for b in range(2**n):
                x = [int(t) for t in reversed(list(bin(b)[2:].zfill(n)))]
                cost = 0
                for i in range(n):
                    for j in range(n):
                        cost = cost + w[i, j] * x[i] * (1 - x[j])
                if best_cost_brute < cost:
                    best_cost_brute = cost
                    xbest_brute = x

            colors = ["r" if xbest_brute[i] == 0 else "c" for i in range(n)]
            try:
                if graph_instance.graph_type == "Nearly Complete BiPartite":
                    pos = {}
                    bottom_nodes, top_nodes = nx.algorithms.bipartite.sets(G)
                    bottom_nodes = list(bottom_nodes)
                    top_nodes = list(top_nodes)
                    pos.update(
                        (i, (i - bottom_nodes[-1] / 2, 1))
                        for i in range(bottom_nodes[-1])
                    )
                    pos.update(
                        (i, (i - bottom_nodes[-1] - top_nodes[-1] / 2, 0))
                        for i in range(
                            bottom_nodes[-1], bottom_nodes[-1] + top_nodes[-1]
                        )
                    )
                    draw_graph(G, colors, pos)
            except:
                pos = nx.spring_layout(G)
                draw_graph(G, colors, pos)
            print(
                "\nBest solution = "
                + str(xbest_brute)
                + " cost = "
                + str(best_cost_brute)
            )

            max_cut = Maxcut(graph_instance.weight_matrix)
            qp = max_cut.to_quadratic_program()
            print(qp.prettyprint())

            qubitOp, offset = qp.to_ising()
            print("Offset:", offset)
            print("Ising Hamiltonian:")
            print(str(qubitOp))

            # solving Quadratic Program using exact classical eigensolver
            exact = MinimumEigenOptimizer(NumPyMinimumEigensolver())
            result = exact.solve(qp)
            print(result.prettyprint())
            print(
                "\nBest solution BRUTE FORCE = "
                + str(xbest_brute)
                + " cost = "
                + str(best_cost_brute)
            )

            # Check that the Hamiltonian gives the right cost
            print(
                f"\n{'-'*10} Checking that current Hamiltonian gives right cost {'-'*10}\n"
            )

            ee = NumPyMinimumEigensolver()

            # Calculate the min eigenvalue
            optimal_result = ee.compute_minimum_eigenvalue(qubitOp)

            ground_state = max_cut.sample_most_likely(optimal_result.eigenstate)
            print("ground state energy:", optimal_result.eigenvalue.real)
            print("optimal max-cut objective:", optimal_result.eigenvalue.real + offset)
            print("ground state solution:", ground_state)
            print("ground state objective:", qp.objective.evaluate(x))

            colors = ["r" if x[i] == 0 else "c" for i in range(n)]

            ################################
            # Quantum Runs
            ################################
            quant_alg = "QAOA"
            print(
                f"\n{'-'*10} Simulating Instance on Quantum using {quant_alg} {'-'*10}\n"
            )

            # Run optimisation code
            optimizer = COBYLA(maxiter=MAX_ITERATIONS)
            num_qubits = qubitOp.num_qubits

            init_state = np.random.rand(num_qubits) * 2 * np.pi
            print(f"The initial state is {init_state}")
            optimizer_results = []

            result = {"algo": None, "result": None}

            ## Setting parameters for a run (Simulator Backend etc)
            algorithm_globals.random_seed = 12321
            seed = 10598
            backend = Aer.get_backend("aer_simulator_statevector")
            quantum_instance = QuantumInstance(
                backend, seed_simulator=seed, seed_transpiler=seed
            )

            print(f"The initial state is {init_state}")
            print(f"Testing Optimizer {i+1}: {type(optimizer).__name__}")

            counts = []
            values = []

            # Callback definition
            def store_intermediate_result(eval_count, parameters, mean, std):
                if track_mlflow:
                    mlflow.log_metric(
                        f"energy_{quant_alg}_{instance_type_logging}",
                        mean,
                        step=len(counts),
                    )
                if eval_count % 100 == 0:
                    print(
                        f"{type(optimizer).__name__} iteration {eval_count} \t cost function {mean}"
                    )
                counts.append(eval_count)
                values.append(mean)

            for restart in range(N_RESTARTS):
                print(f"Running Optimization at n_restart={restart}")
                init_state = np.random.rand(4) * 2 * np.pi

                qaoa = QAOA(
                    optimizer=optimizer,
                    reps=N_LAYERS,
                    initial_point=list(2 * np.pi * np.random.random(2 * N_LAYERS)),
                    callback=store_intermediate_result,
                    quantum_instance=quantum_instance,
                )
                algo_result = qaoa.compute_minimum_eigenvalue(qubitOp)
            # Convergence array
            total_counts = np.arange(0, len(counts))
            values = np.asarray(values)

            if track_mlflow:
                logged_parameters = clean_parameters_for_logging(
                    algo_result=algo_result,
                    instance_size=instance_size,
                    graph_type=instance_type_logging,
                )
                print(json.dumps(logged_parameters, indent=3))
                mlflow.log_metrics(logged_parameters)

            print(f"\n{'-'*10} Optimization Complete {'-'*10}\n")

            pylab.rcParams["figure.figsize"] = (12, 8)
            pylab.plot(total_counts, values, label=type(optimizer).__name__)
            pylab.xlabel("Eval count")
            pylab.ylabel("Energy")
            pylab.title("Energy convergence for various optimizers")
            pylab.legend(loc="upper right")

            # Sample most liklely eigenstate
            x = max_cut.sample_most_likely(algo_result.eigenstate)
            # Energy Gap = E_{g} / E_{opt}
            energy_gap = (
                1 - algo_result.eigenvalue.real / optimal_result.eigenvalue.real
            )
            print("Final energy:", algo_result.eigenvalue.real)
            print("time:", algo_result.optimizer_time)
            print("max-cut objective:", algo_result.eigenvalue.real + offset)
            print("solution:", x)
            print("solution objective:", qp.objective.evaluate(x))
            print("energy_gap:", energy_gap)

            if track_mlflow:
                print(
                    f"\n{'-'*50}\n Logging Results for {instance_type_logging} of size {instance_size}\n{'-'*50}\n"
                )
                mlflow.log_metric(
                    f"energy_gap_{quant_alg}_{instance_type_logging}_{instance_size}",
                    energy_gap,
                )
                mlflow.log_metric(
                    f"final_energy_{quant_alg}_{instance_type_logging}_{instance_size}",
                    algo_result.eigenvalue.real,
                )
                mlflow.log_metric(
                    f"maxcut_objective_{quant_alg}_{instance_type_logging}_{instance_size}",
                    algo_result.eigenvalue.real + offset,
                )
                mlflow.log_metric(
                    f"solution_objective_{quant_alg}_{instance_type_logging}_{instance_size}",
                    qp.objective.evaluate(x),
                )

                with make_temp_directory() as temp_dir:
                    # Plot Network Graph
                    pylab.clf()
                    graph_plot_fn = f"network_plot_{quant_alg}_{instance_type_logging}_{instance_size}.png"
                    graph_plot_fn = os.path.join(temp_dir, graph_plot_fn)
                    colors = ["r" if x[i] == 0 else "c" for i in range(n)]
                    try:
                        if graph_instance.graph_type == "Nearly Complete BiPartite":
                            pos = {}
                            bottom_nodes, top_nodes = nx.algorithms.bipartite.sets(G)
                            bottom_nodes = list(bottom_nodes)
                            top_nodes = list(top_nodes)
                            pos.update(
                                (i, (i - bottom_nodes[-1] / 2, 1))
                                for i in range(bottom_nodes[-1])
                            )
                            pos.update(
                                (i, (i - bottom_nodes[-1] - top_nodes[-1] / 2, 0))
                                for i in range(
                                    bottom_nodes[-1], bottom_nodes[-1] + top_nodes[-1]
                                )
                            )
                            draw_graph(G, colors, pos)
                            pylab.savefig(graph_plot_fn)
                            mlflow.log_artifact(graph_plot_fn)
                        else:
                            pos = nx.spring_layout(G)
                            draw_graph(G, colors, pos)
                            pylab.savefig(graph_plot_fn)
                            mlflow.log_artifact(graph_plot_fn)
                    except:
                        pos = nx.spring_layout(G)
                        draw_graph(G, colors, pos)
                        pylab.savefig(graph_plot_fn)
                        mlflow.log_artifact(graph_plot_fn)
                    finally:
                        print("Unable to load artifacts to MLFLOW")

                    # Plot convergence
                    try:
                        convergence_plot_fn = f"convergence_plot_{quant_alg}_{instance_type_logging}_{instance_size}.png"
                        convergence_plot_fn = os.path.join(
                            temp_dir, convergence_plot_fn
                        )
                        pylab.clf()
                        pylab.rcParams["figure.figsize"] = (12, 8)
                        pylab.plot(total_counts, values, label=type(optimizer).__name__)
                        pylab.xlabel("Eval count")
                        pylab.ylabel("Energy")
                        pylab.title("Energy convergence for various optimizers")
                        pylab.legend(loc="upper right")
                        pylab.savefig(convergence_plot_fn)
                        pylab.axhline(y=algo_result.eigenvalue.real, ls="--", c="red")
                        mlflow.log_artifact(convergence_plot_fn)
                    except:
                        print("Unable to load artifact to MLFLOW")

    print(f"\n{'-'*50}\n{'-'*50}\n{' '*18} Run Complete \n{'-'*50}\n{'-'*50}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-T",
        "--track_mlflow",
        type=str2bool,
        nargs="?",
        const=True,
        default=False,
        help="Activate MlFlow Tracking.",
    )

    args = vars(parser.parse_args())
    print(args)
    t1 = time.time()
    main(track_mlflow=args["track_mlflow"])
    t2 = time.time()
    print("Result found in: {} seconds".format(round(t2 - t1, 3)))
