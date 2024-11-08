# https://github.com/epiqc/PartialCompilation/blob/50d80f56efdf754e40a0b1dd00404788a03fdf3d/qiskit-terra/test/python/tools/monitor/test_backend_monitor.py
# -*- coding: utf-8 -*-

# Copyright 2018, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

"""Tests for the wrapper functionality."""

import unittest
from qiskit.tools.monitor import backend_overview, backend_monitor
from qiskit.test import QiskitTestCase, requires_qe_access


class TestBackendOverview(QiskitTestCase):
    """Tools test case."""

    @requires_qe_access
    def test_backend_overview(self, qe_token, qe_url):
        """Test backend_overview"""
        from qiskit import IBMQ  # pylint: disable: import-error
        IBMQ.enable_account(qe_token, qe_url)
        backend_overview()

    @requires_qe_access
    def test_backend_monitor(self, qe_token, qe_url):
        """Test backend_monitor"""
        from qiskit import IBMQ  # pylint: disable: import-error
        IBMQ.enable_account(qe_token, qe_url)
        for back in IBMQ.backends():
            if not back.configuration().simulator:
                backend = back
                break
        backend_monitor(backend)


if __name__ == '__main__':
    unittest.main(verbosity=2)
