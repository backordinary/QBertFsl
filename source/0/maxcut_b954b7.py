# https://github.com/ProvideQ/toolbox-server/blob/129f879d958843fc965462473c40fb9553ba6d8c/qiskit/maxcut/maxcut.py
# Hippity hoppity your code is now my property!
# https://qiskit.org/documentation/optimization/tutorials/06_examples_max_cut_and_tsp.html
# https://pypi.org/project/pygmlparser/


# useful additional packages
import numpy as np
import networkx as nx
import sys

import pygmlparser as pygmlparser

# gml parsing
from pygmlparser.Parser import Parser
from pygmlparser.Graph import Graph
from pygmlparser.Edge import Edge
from pygmlparser.Node import Node

# Qiskit
from qiskit import Aer
from qiskit.circuit.library import TwoLocal
from qiskit_optimization.applications import Maxcut, Tsp
from qiskit.algorithms import VQE, NumPyMinimumEigensolver
from qiskit.algorithms.optimizers import SPSA
from qiskit.utils import algorithm_globals, QuantumInstance


if len(sys.argv) != 3:
    raise TypeError('This script expects exactly 2 arguments. Input file (argument 1) and output file (argument 2).')

input_path = sys.argv[1]
output_path = sys.argv[2]

# Instantiate a parser, load a file, and parse it!
parser: Parser = Parser()
parser.loadGML(input_path)
parser.parse()

# Retrieve the graph nodes
nodes: Graph.Nodes = parser.graph.graphNodes  # a map of id -> Node objects

# Retrieve the graph edges
edges: Graph.Edges = parser.graph.graphEdges  # list of Edge objects

# Generating a graph
n = len(nodes)  # Number of nodes in graph
G = nx.Graph()
G.add_nodes_from(np.arange(0, n, 1))
elist = []

for e in edges:
    elist.append((e.source_node.id, e.target_node.id, 1))  # TODO: extract edge weight

# tuple is (i,j,weight) where (i,j) is the edge
G.add_weighted_edges_from(elist)

# Computing the weight matrix from the graph
w = np.zeros([n, n])
for i in range(n):
    for j in range(n):
        temp = G.get_edge_data(i, j, default=0)
        if temp != 0:
            w[i, j] = temp["weight"]

max_cut = Maxcut(w)
qp = max_cut.to_quadratic_program()
qubitOp, offset = qp.to_ising()

algorithm_globals.random_seed = 123
seed = 10598
backend = Aer.get_backend("aer_simulator_statevector")
quantum_instance = QuantumInstance(backend, seed_simulator=seed, seed_transpiler=seed)

# construct VQE
spsa = SPSA(maxiter=300)
ry = TwoLocal(qubitOp.num_qubits, "ry", "cz", reps=5, entanglement="linear")
vqe = VQE(ry, optimizer=spsa, quantum_instance=quantum_instance)

# run VQE
result = vqe.compute_minimum_eigenvalue(qubitOp)

# save results
x = max_cut.sample_most_likely(result.eigenstate)
f = open(output_path, 'a')
f.write("energy:" + str(result.eigenvalue.real) + "\n")
f.write("time:" + str(result.optimizer_time) + "\n")
f.write("max-cut objective:" + str(result.eigenvalue.real + offset) + "\n")
f.write("solution:" + str(x) + "\n")
f.write("solution objective:" + str(qp.objective.evaluate(x)) + "\n")
f.close()
