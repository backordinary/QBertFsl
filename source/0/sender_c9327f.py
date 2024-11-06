# https://github.com/jdanielescanez/quantum-solver/blob/122be33c6a095a17bc777bf112925af854e50beb/src/rsa_substitute/sender.py
#!/usr/bin/env python3

# Author: Daniel Escanez-Exposito

from qiskit import QuantumCircuit
from rsa_substitute.participant import Participant
import numpy as np

## The Sender entity in the E91 implementation
## @see https://journals.aijr.org/index.php/ajgr/article/view/699/168
class Sender(Participant):
  ## Constructor
  def __init__(self, name='', r=0, p=[]):
    super().__init__(name)
    self.r = r
    self.p = p

    self.n = len(self.p)
    self.r_numbers = np.random.choice(list(range(self.n)), size=self.r, replace=True)

  def encode(self, message):
    qc = message.copy()
    for r_number in self.r_numbers:
      qc += self.p[r_number]
    qc.barrier()
    return qc

  def decode(self, message):
    qc = message.copy()
    for r_number in self.r_numbers:
      qc += self.p[r_number].inverse()
    qc.barrier()
    return qc
    