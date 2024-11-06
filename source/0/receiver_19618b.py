# https://github.com/jdanielescanez/quantum-solver/blob/122be33c6a095a17bc777bf112925af854e50beb/src/bb84/receiver.py
#!/usr/bin/env python3

# Author: Daniel Escanez-Exposito

from bb84.participant import Participant
from qiskit import QuantumCircuit
from numpy.random import rand

## The Receiver entity in the BB84 implementation
## @see https://qiskit.org/textbook/ch-algorithms/quantum-key-distribution.html
class Receiver(Participant):
  ## Constructor
  def __init__(self, name='', original_bits_size=0):
    super().__init__(name, original_bits_size)

  ## Decode the message measuring the circuit (density-dependent)
  def decode_quantum_message(self, message, density, backend):
    ## The values of the participant
    self.values = []
    for i, qc in enumerate(message):
      qc.barrier()
      if rand() < density:
        if self.axes[i] == 1:
          qc.h(0)
        qc.measure(0, 0)
        result = backend.run(qc, shots=1, memory=True).result()
        measured_bit = int(result.get_memory()[0])
        self.values.append(measured_bit)
      else:
        self.values.append(-1)
    return message
