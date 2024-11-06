# https://github.com/niefermar/CuanticaProgramacion/blob/cf066149b4bd769673e83fd774792e9965e5dbc0/qiskit/backends/local/_simulatorerror.py
# -*- coding: utf-8 -*-

# Copyright 2017, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

"""
Exception for errors raised by simulators.

Author: Juan Gomez
"""

from qiskit import QISKitError


class SimulatorError(QISKitError):
    """Base class for errors raised by simulators."""

    def __init__(self, *message):
        """Set the error message."""
        super().__init__(*message)
        self.message = ' '.join(message)

    def __str__(self):
        """Return the message."""
        return repr(self.message)