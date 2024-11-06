# https://github.com/nelimee/quantum-tools/blob/b9d19c6a1bdcb4e30316f152d9c441fb63ace6ec/gates/state_preparation.py
# ======================================================================
# Copyright CERFACS (May 2018)
# Contributor: Adrien Suau (suau@cerfacs.fr)
#
# This software is governed by the CeCILL-B license under French law and
# abiding  by the  rules of  distribution of free software. You can use,
# modify  and/or  redistribute  the  software  under  the  terms  of the
# CeCILL-B license as circulated by CEA, CNRS and INRIA at the following
# URL "http://www.cecill.info".
#
# As a counterpart to the access to  the source code and rights to copy,
# modify and  redistribute granted  by the  license, users  are provided
# only with a limited warranty and  the software's author, the holder of
# the economic rights,  and the  successive licensors  have only limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using, modifying and/or  developing or reproducing  the
# software by the user in light of its specific status of free software,
# that  may mean  that it  is complicated  to manipulate,  and that also
# therefore  means that  it is reserved for  developers and  experienced
# professionals having in-depth  computer knowledge. Users are therefore
# encouraged  to load and  test  the software's  suitability as  regards
# their  requirements  in  conditions  enabling  the  security  of their
# systems  and/or  data to be  ensured and,  more generally,  to use and
# operate it in the same conditions as regards security.
#
# The fact that you  are presently reading this  means that you have had
# knowledge of the CeCILL-B license and that you accept its terms.
# ======================================================================

"""This module contains functions and gates to prepare quantum states.
"""

from typing import Tuple, List, Union
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.extensions.quantum_initializer import _initializer

QuantumBit = Tuple[QuantumRegister, int] #pylint: disable=invalid-name

def initialize(circuit: QuantumCircuit,
               desired_vector: List[complex],
               qubits: Union[List[QuantumBit], QuantumRegister]):
    """Initialise the given qubits to the state represented by desired_vector."""
    if isinstance(qubits, QuantumRegister):
        return _initializer.initialize(circuit,
                                       desired_vector,
                                       [qubits[i] for i in range(len(qubits))])

    return _initializer.initialize(circuit,
                                   desired_vector,
                                   qubits)
