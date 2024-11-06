# https://github.com/mhinkie/ShorDiscreteLog/blob/86e7b394de24fe45652a0b8a282656cd513a403b/shor/mosca_ekert/me_output.py
from shor.mosca_ekert.mosca_ekert import DiscreteLogMoscaEkertSharedRegister, DiscreteLogMoscaEkertSeperateRegister
from qiskit import Aer, transpile, execute
import json


def get_order(g, p):
    for x in range(1, p):
        if g**x % p == 1:
            return x

def get_qobj_output(circuit, simulator):
    circsim = transpile(circuit, simulator)

    job = execute(circsim, simulator, shots=1)
    job_dict = job.qobj().to_dict()

    json_object = json.dumps(job_dict, indent=4)
    return json_object

p = 29
g = 3
b = g**2 % p
r = get_order(g, p)
print("order: ", r)

simulator = Aer.get_backend('aer_simulator')

f = open("circuit_output.qobj", "w")
me_algo = DiscreteLogMoscaEkertSeperateRegister(b, g, p, r=r, full_run=True, quantum_instance=simulator)
f.write(get_qobj_output(me_algo.get_circuit(), simulator))
f.close()

