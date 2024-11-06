# https://github.com/qiskit-community/qiskit-presentations/blob/d5690616ada7b14ab4d091e5ecc87755f6d6a18a/2018-09-07_TechCrunch/techcrunch_keynote.py
# -*- coding: utf-8 -*-

# Copyright 2018, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

from IPython.display import HTML
from presentation_helpers import *

from AI import *

mode = "offline"

print('Hello TechCrunch .... ')

def superposition():
    return HTML(html_img("superposition.gif"))

def entanglement():
    return HTML(html_img("entenglemant.gif"))

def interference():
    return HTML(html_img("interference.gif"))

def algorithm():
    return HTML(html_img("algorithm.jpg"))

def quantum_computer():
    return HTML(html_img("quantum_lab.jpg"))

def quantum_computer_inside():
    return HTML(html_img("quantum-computer.jpg"))

def quantum_chip():
    return HTML(html_img("quantum_chip.jpg"))

def quantum_chip_detail():
    return HTML(html_img("quantum_chip_detail.jpg"))

def quantum_qubit():
    return HTML(html_img("quantum_qubit.jpg"))

def lab():
    URL = "https://www.youtube.com/embed/y58QyievkxU"

    content = html_video("IBMQlab.mp4")

    return HTML(content)


def qx():
    return HTML(html_link(html_video("QX.mp4"),
                         'https://quantumexperience.ng.bluemix.net'))

def qiskit():
    URL = "https://qiskit.org"

    content = show_content( html_iframe(URL),
                            html_img("qiskit-web.png"),
                            url_check= URL)

    return HTML(content)

def bell():
    return HTML('''
        <pre>
from qiskit import ClassicalRegister, QuantumRegister
from qiskit import QuantumCircuit, execute

q = QuantumRegister(2)
c = ClassicalRegister(2)
qc = QuantumCircuit(q, c)

qc.h(q[0])
qc.cx(q[0], q[1])
qc.measure(q, c)

job_sim = execute(qc, "local_qasm_simulator")
sim_result = job_sim.result()

print(sim_result.get_counts(qc))
        </pre>

        ''')


def AI_execution(face):
    execute_AI(face)
    return HTML(f'''
        <pre>

        ------ >>> {face} <<< ------
        ------------------------
        Sending to execute  🚀🚀
        ------------------------
        Waiting for results ⏱⏱
        ------------------------
        Using local simulator ⚗️️️️️
        </pre>''')

def quantum_execution():
    return HTML(html_img("quantum_execution.gif"))

def how_works():
    return HTML(html_img("SVM.gif")+html_img("QML1.jpg"))

def implementation():
    return HTML(html_img("implementation.jpg"))

def qiskit_code():
    return HTML('''
    <pre>
# setup the circuit
q = QuantumRegister("q", n)
c = ClassicalRegister("c", n)
trial_circuit = QuantumCircuit(q, c)

# 0: Set the qubits in superposition
for r in range(len(x_vec1)):
    trial_circuit.h(q[r])
    trial_circuit.u1(2*x_vec1[r], q[r])

# 1: Using entanglement,map the training data to a quantum feature map
for node in entangler_map:
    for j in entangler_map[node]:
        trial_circuit.cx(q[node], q[j])
        trial_circuit.u1(2*(np.pi-x_vec1[node])*(np.pi-x_vec1[j]), q[j])
        trial_circuit.cx(q[node], q[j])

# 2: Train the quantum classifier by updating the quantum network.
trial_circuit.barrier(q)

for r in range(len(x_vec1)):
    trial_circuit.ry(theta[2*r],q[r])
    trial_circuit.rz(theta[2*r+1],q[r])

for i in range(m):
    for node in entangler_map:
        for j in entangler_map[node]:
            trial_circuit.cz(q[node], q[j])
    for j in entangler_map[node]:
        trial_circuit.ry(theta[n * ( i + 1 ) * 2 + 2 * j],q[j])
        trial_circuit.rz(theta[n * ( i + 1 ) * 2 + 2 * j + 1],q[j])

trial_circuit.barrier(q)

if measurement:
    for j in range(n):
        trial_circuit.measurement(q[j],c[j])

    </pre>
    ''')

def quantum_improve():
    return HTML(html_img("QML3.jpg"))

def AI_result():
    result=result_AI_inference()

    image = html_img("q"+result["inference"]+".jpg",500)

    return HTML(f'''
        <pre>
        -----------------------------------
        Predicted label is {result["label"]} = "{result["inference"]}"
        Classification success is {result["quality"]} %
        -----------------------------------
        -----------------------------------
        testing success ratio:  1.0
        predicted labels: {result["labels"]}
        -----------------------------------
        ⏰ {result["time"]}
        -----------------------------------
        </pre>
        </br>
        </br>
        '''+image)

def community():
    return HTML(html_video("community.mp4"))

def diagram_ML():
    return HTML(html_img("Slide02.jpeg"))

def papers():
    return HTML(html_img("papers.jpg"))

def executions():
    return HTML(html_img("executions-QX-complete.gif"))

def thinking():
    return HTML(html_img('thinking.jpg'))

def share():
    return HTML('TODO: improve image, and update with the Public Github url ' +
                html_img('url-presentation.png',400))
