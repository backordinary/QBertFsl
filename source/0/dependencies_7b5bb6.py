# https://github.com/daviyan5/QuantumPerceptron/blob/a5f78bc96159bc544c37b04cded488b5e9b1ec10/src/dependencies.py
from qiskit import *
from qiskit.visualization import *
from qiskit.circuit.library import MCPhaseGate
from qiskit.algorithms.optimizers import SPSA

import qiskit.quantum_info as qi
import numpy as np
import pandas
import matplotlib.pyplot as plt
import os


from random import *
from math import *

sim = Aer.get_backend('aer_simulator')
sim.set_options(device = 'GPU')


def phase_normalize(alfa,mn,mx):
  return ((alfa - mn) / (mx - mn))  * (pi/2)

def phase_denormalize(norm,mn,mx):
  return ((norm * (mx - mn)) / (pi/2)) + mn