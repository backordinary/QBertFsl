# https://github.com/nelimee/quantum-tools/blob/b9d19c6a1bdcb4e30316f152d9c441fb63ace6ec/gates/rx.py
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

"""This module contains functions to apply a single-qubit RX gate.
"""
from typing import Tuple, Union
from sympy import pi
from qiskit import QuantumCircuit, QuantumRegister, CompositeGate
import utils.gates.comment

QubitType = Tuple[QuantumRegister, int] #pylint: disable=invalid-name

class RxGate(CompositeGate):

    def __init__(self,
                 theta: float,
                 qubit: QubitType,
                 qcirc: QuantumCircuit = None):
        """Initialize the RxGate class.

        Parameters:
            theta: Parameter of the RX gate.
            qubit: The qubit on which the RX gate is applied.
            qcirc: The associated quantum circuit.
        """

        used_qubits = [qubit]

        super().__init__(self.__class__.__name__, # name
                         [theta],                 # parameters
                         used_qubits,             # qubits
                         qcirc)                   # circuit

        circuit.comment("RX")
        circuit.u3(theta, pi/2, 3*pi/2, qubit)

def rx(self,
       qubit: QubitType,
       theta: float) -> RxGate:
    self._check_qubit(qubit)
    return self._attach(RxGate(self, qubit, theta, self))

QuantumCircuit.rx = rx
CompositeGate.rx = rx
