# https://github.com/awlaplace/Quantum/blob/f5938ed04e33cf3e35b7976c8068d9797fdf9882/QKD/BB84/BB84_intercept.py
# implement BB84 protocol with interception

# preprocessing
from qiskit import QuantumCircuit, Aer, transpile, assemble
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from numpy.random import randint
import numpy as np

np.random.seed(seed=0)
# fix 100 quantum bits
n = 100

def encode_message(bits, bases):
    message = []
    for i in range(n):
        qc = QuantumCircuit(1,1)
        if bases[i] == 0: # Prepare qubit in Z-basis
            if bits[i] == 0:
                pass 
            else:
                qc.x(0)
        else: # Prepare qubit in X-basis
            if bits[i] == 0:
                qc.h(0)
            else:
                qc.x(0)
                qc.h(0)
        qc.barrier()
        message.append(qc)
    return message


def measure_message(message, bases):
    backend = Aer.get_backend('aer_simulator')
    measurements = []
    for q in range(n):
        if bases[q] == 0: # measuring in Z-basis
            message[q].measure(0,0)
        if bases[q] == 1: # measuring in X-basis
            message[q].h(0)
            message[q].measure(0,0)
        aer_sim = Aer.get_backend('aer_simulator')
        qobj = assemble(message[q], shots=1, memory=True)
        result = aer_sim.run(qobj).result()
        measured_bit = int(result.get_memory()[0])
        measurements.append(measured_bit)
    return measurements


def remove_garbage(a_bases, b_bases, bits):
    good_bits = []
    for q in range(n):
        if a_bases[q] == b_bases[q]:
            # If both used the same basis, add this to the list of 'good' bits
            good_bits.append(bits[q])
    return good_bits


def sample_bits(bits, selection):
    sample = []
    for i in selection:
        # use np.mod to make sure the bit we sample is always in the list range
        i = np.mod(i, len(bits))
        # pop(i) removes the element of the list at index 'i'
        sample.append(bits.pop(i))
    return sample

def main(): 
    # Step 1
    ## Alice choose random bit sequence and bases
    alice_bits = randint(2, size=n)
    alice_bases = randint(2, size=n)

    # Step 2
    ## Alice encodes quantum bit sequence by using classical bits and bases, send Bob that
    message = encode_message(alice_bits, alice_bases)

    # interception
    ## Eve intercepts Alice's message by using random bases
    eve_bases = randint(2, size=n)
    intercepted_message = measure_message(message, eve_bases)

    # Step 3
    ## Bob measures Alice's message by using random bases
    bob_bases = randint(2, size=n)
    bob_results = measure_message(message, bob_bases)

    # Step 4
    ## Alice and Bob publish each bases and share the secret key
    bob_key = remove_garbage(alice_bases, bob_bases, bob_results)
    alice_key = remove_garbage(alice_bases, bob_bases, alice_bits)

    # Step 5
    sample_size = 15
    bit_selection = randint(n, size=sample_size)

    bob_sample = sample_bits(bob_key, bit_selection)
    print("  bob_sample = " + str(bob_sample))
    alice_sample = sample_bits(alice_key, bit_selection)
    print("alice_sample = "+ str(alice_sample))


if __name__ == '__main__':
    main()

'''
  bob_sample = [0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1]
alice_sample = [0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1]
'''