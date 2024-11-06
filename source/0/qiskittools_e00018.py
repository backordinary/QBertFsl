# https://github.com/qiskit-community/qiskit-vscode/blob/7610e35db7c72851e9bca692768b130b0e1ad1ef/client/resources/qiskitScripts/qiskitTools.py
# Copyright (c) 2018, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

import json
from qiskit import __version__
from IBMQuantumExperience import IBMQuantumExperience
from packaging import version
import argparse
import warnings
from qiskit import QuantumCircuit
from qiskit.wrapper import load_qasm_file
from qiskit import execute

if (version.parse(__version__) >= version.parse("0.6")):
    from qiskit import IBMQ
    from qiskit import Aer


class QiskitUnsupportedVersion(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class QiskitTools(object):
    """
    Utilities for the Qiskit-terra-related scripts
    """

    def __init__(self):
        self.PUBLIC_NAMES = {
            'ibmq_20_tokyo': 'IBM Q 20 Tokyo',
            'QS1_1': 'IBM Q 20 Austin',
            'ibmq_16_melbourne': 'IBM Q 16 Melbourne',
            'ibmqx5': 'IBM Q 16 Rueschlikon',
            'ibmq_16_rueschlikon': 'IBM Q 16 Rueschlikon',
            'ibmqx4': 'IBM Q 5 Tenerife',
            'ibmq_5_tenerife': 'IBM Q 5 Tenerife',
            'ibmqx2': 'IBM Q 5 Yorktown',
            'ibmq_5_yorktown': 'IBM Q 5 Yorktown',
            'ibmq_qasm_simulator': 'IBM Q QASM Simulator'
        }

    def executeQASM(self, filename):
        if (version.parse(__version__) >= version.parse("0.6") and
                (version.parse(__version__) < version.parse("0.7"))):

            qc = load_qasm_file(filename)
            job_sim = execute(qc, Aer.get_backend("qasm_simulator"))
            result = job_sim.result()
            return result.get_counts()

        elif (version.parse(__version__) >= version.parse("0.7")):
            qc = QuantumCircuit.from_qasm_file(filename)
            job_sim = execute(qc, Aer.get_backend("qasm_simulator"))
            result = job_sim.result()
            return result.get_counts()

        else:
            raise QiskitUnsupportedVersion(
                'Qiskit-terra version must be v0.6 or v0.7')

    def listRemoteBackends(self, apiToken, url,
                           hub=None, group=None, project=None):

        if version.parse(__version__) >= version.parse("0.6"):

            if (hub is None or group is None or project is None):
                IBMQ.enable_account(apiToken, url)
            else:
                IBMQ.enable_account(apiToken, url=url,
                                    hub=hub, group=group,
                                    project=project)

            backs = [backend.name() for backend in IBMQ.backends()]

        else:
            raise QiskitUnsupportedVersion(
                'Qiskit-terra version must be > v0.6')

        return backs

    def listLocalBackends(self):

        if version.parse(__version__) >= version.parse("0.6"):
            backs = [backend.name() for backend in Aer.backends()]

        else:
            raise QiskitUnsupportedVersion(
                'Qiskit-terra version must be > v0.6')

        return backs

    def getBackendStatus(self, back, apiToken, url,
                         hub=None, group=None, project=None):
        if version.parse(__version__) >= version.parse("0.6"):

            if (hub is None or group is None or project is None):
                IBMQ.enable_account(apiToken, url)
            else:
                IBMQ.enable_account(apiToken, url,
                                    hub=hub, group=group,
                                    project=project)

            return self.parseBackendStatus(IBMQ.get_backend(back).status())

        else:
            raise QiskitUnsupportedVersion(
                'Qiskit-terra version must be > v0.6')

    def createDeviceStatus(self, back):
        return {
            'name': self.PUBLIC_NAMES[back],
            'status': self.parseBackendStatus(
                IBMQ.get_backend(back).status()
            )
        }

    def parseBackendStatus(self, backendStatus):
        if (version.parse(__version__) >= version.parse("0.6") and
                (version.parse(__version__) < version.parse("0.7"))):
            return {
                'name': backendStatus['name'],
                'pending_jobs': backendStatus['pending_jobs'],
                'available': self.parseAvailability(backendStatus)
            }
        elif (version.parse(__version__) >= version.parse("0.7")):
            # The type(backendStatus) is now <class 'qiskit.providers.models.backendstatus.BackendStatus'>
            # previously was <class 'qiskit._util.AvailableToOperationalDict'>
            return {
                'name': backendStatus.backend_name,
                'pending_jobs': backendStatus.pending_jobs,
                'available': backendStatus.operational
            }

        else:
            raise QiskitUnsupportedVersion(
                'Qiskit-terra version must be > v0.6')

    def parseAvailability(self, backendStatus):
        try:
            return backendStatus['available']
        except KeyError:
            return backendStatus['operational']
