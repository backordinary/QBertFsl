# https://github.com/alejogq/Quantum-Computing-Introduction/blob/c849ce38411d06e287b5184d67f9b3d965792402/Construccion%20de%20Circuitos/herramientas/learn_quantum.py
import math as math
from math import pi, sqrt
import fractions as frac
from cmath import phase

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
import numpy as np

from qiskit import Aer, IBMQ, execute

from qiskit.tools.monitor import job_monitor
from itertools import groupby
import qiskit.quantum_info.synthesis.two_qubit_decompose as twoq

imag = complex(0, 1)

ket_0 = np.array([[1], [0]])
ket_1 = np.array([[0], [1]])

ket_plus = np.array([[1 / sqrt(2)], [1 / sqrt(2)]])
ket_minus = np.array([[1 / sqrt(2)], [- 1 / sqrt(2)]])

ket_l = np.array([[1 / sqrt(2)], [imag / sqrt(2)]])
ket_r = np.array([[1 / sqrt(2)], [-imag / sqrt(2)]])

pauliX = np.array([[0, 1], [1, 0]], dtype=complex)
pauliY = np.array([[0, 0. - 1.j], [0. + 1.j, 0]], dtype=complex)
pauliZ = np.array([[1, 0], [0, -1]], dtype=complex)

hadamard = (1 / sqrt(2)) * np.array([[1 + 0.j, 1 + 0.j],
                                     [1 + 0.j, -1 + 0.j]], dtype=complex)

cnot01 = np.array([[1, 0, 0, 0],
                   [0, 1, 0, 0],
                   [0, 0, 0, 1],
                   [0, 0, 1, 0]], dtype=complex)

cnot10 = np.array([[1, 0, 0, 0],
                   [0, 0, 0, 1],
                   [0, 0, 1, 0],
                   [0, 1, 0, 0]], dtype=complex)

# line feed in latex
llf = r'\begin{equation} \\ \end{equation}'

default_bracket_type = 'p'


def ket(str_bits):
    ret = get_basis(str_bits[0])
    for n in range(1, len(str_bits)):
        ret = np.kron(ret, get_basis(str_bits[n]))
    return ret


def bra(str_bits):
    return ket(str_bits).T.conj()


def get_basis(char_bit):
    if char_bit == '0' or char_bit == 'H':
        return ket_0
    if char_bit == '1' or char_bit == 'V':
        return ket_1
    if char_bit == '+':
        return ket_plus
    if char_bit == '-':
        return ket_minus
    if char_bit == 'L':
        return ket_l
    if char_bit == 'R':
        return ket_r

    raise ValueError('Invalid character passed to get_basis')


def reverse_results(results):
    new_results = {}
    for k, v in results.items():
        k = reverse_string(k)
        new_results[k] = v
    return new_results.items()


def print_reverse_results(results, label=None):
    lbl = 'Reversed:'
    if not label is None:
        lbl = lbl + label + ':'
    print(lbl, sorted(reverse_results(results)))


def swap_entries(qiskit_array):
    half_size = int(qiskit_array.shape[0] / 2)  # always square and powers of 2.

    for n in range(1, half_size, 2):
        qiskit_array[:, [n, half_size + n - 1]] = qiskit_array[:, [half_size + n - 1, n]]

    for n in range(1, half_size, 2):
        qiskit_array[[n, half_size + n - 1], :] = qiskit_array[[half_size + n - 1, n], :]
    return qiskit_array


def print_matrix(QC):
    print('Adjusted Matrix:')
    with np.printoptions(linewidth=1024):
        print(what_is_the_matrix(QC))


def show_eigens(QC, bracket_type=None):
    unitary = what_is_the_matrix(QC)
    w, v = np.linalg.eig(unitary)

    bracket_type = get_bracket_type(bracket_type)
    output = r'\begin{equation*}'
    for n in range(w.shape[0]):
        output += r'\lambda_' + str(n) + '=' + format_complex_as_latex(w[n])
        output += r',\; '
        output += np_array_to_latex(v[n].reshape(v[n].shape[0], 1),
                                    bracket_type=bracket_type, factor_out=False, begin_equation=False,
                                    label='v_' + str(n))
        output += r'\quad'
    output += r'\end{equation*}'
    return output


def what_is_the_matrix(QC):
    qiskit_array = execute_unitary(QC)
    return swap_entries(qiskit_array)


def show_me_the_matrix(qc, bracket_type=None, factor_out=True, label=None):
    unitary = what_is_the_matrix(qc)
    return np_array_to_latex(unitary,
                             bracket_type=get_bracket_type(bracket_type),
                             factor_out=factor_out,
                             label=label)


def show_density_matrix(qc, bracket_type=None, factor_out=False, label=None):
    state_vector = execute_state_vector(qc)
    sv = state_vector.reshape(1, state_vector.shape[0])
    density_matrix = sv.T.conj()@sv
    if not np.isclose(np.trace(density_matrix@density_matrix), 1):
        return 'Not a pure state -- not implemented for mixed'
    return np_array_to_latex(density_matrix,
                             bracket_type=get_bracket_type(bracket_type),
                             factor_out=factor_out,
                             label=label)


def get_bracket_type(bracket_type=None):
    if bracket_type is None:
        return default_bracket_type
    return bracket_type


def np_array_to_latex(np_array, bracket_type=None, factor_out=True, label=None, begin_equation=True):
    rows, cols = np_array.shape
    bracket_type = get_bracket_type(bracket_type)
    if factor_out:
        factor = factor_array(np_array)
        if factor == 0:
            factor_out = False
    output = ''
    if begin_equation:
        output = r'\begin{equation*}'
    if label is not None:
        output += label + ' = '
    if factor_out:
        output += format_float_as_latex(factor)
    output += r'\begin{' + bracket_type + r'matrix}'
    for i in range(rows):
        for j in range(cols):
            current = np_array[i, j]
            if factor_out:
                current = current / factor
            output += format_complex_as_latex(current)
            if j < cols - 1:
                output += ' & '
        output += r' \\ ' + '\n'
    output += r'\end{' + bracket_type + r'matrix}'
    if begin_equation:
        output += r'\end{equation*}'
    return output


def factor_array(np_array):
    factor = 0

    rows, cols = np_array.shape
    for i in range(rows):
        for j in range(cols):
            potential = abs(round(np_array[i, j].real, 6))
            if potential != 0 and factor != 0 and potential != factor:
                return 0
            else:
                if factor == 0 and potential != 0:
                    factor = potential

            potential = abs(round(np_array[i, j].imag, 6))
            if potential != 0 and factor != 0 and potential != factor:
                return 0
            else:
                if factor == 0 and potential != 0:
                    factor = potential
    if factor == 1:
        return 0
    return factor


def format_complex_as_latex(complex):
    latex = ''
    if np.isclose(complex.real, 0):
        if np.isclose(complex.imag, 0):
            return ' 0 '
        else:
            if complex.imag < 0:
                latex += '-'
            if np.isclose(np.abs(complex.imag), 1):
                latex += 'i'
            else:
                latex += format_float_as_latex(np.abs(complex.imag)) + 'i'
    else:
        latex += format_float_as_latex(complex.real)
        if np.isclose(complex.imag, 0):
            return latex
        if complex.imag > 0:
            latex += '+'
        else:
            latex += '-'
        if np.isclose(np.abs(complex.imag), 1):
            latex += 'i'
        else:
            latex += format_float_as_latex(np.abs(complex.imag)) + 'i'
    return latex


def format_float_as_latex(raw):
    if raw < 0:
        sign = '-'
    else:
        sign = ''

    positive = np.abs(raw)

    f = frac.Fraction(positive).limit_denominator(8)
    if f.denominator == 1:
        return format_raw(raw)

    if np.isclose(f.numerator / f.denominator, positive):
        return sign + r'\frac{' + str(f.numerator) + '}{' + str(f.denominator) + '}'

    square = positive ** 2
    f = frac.Fraction(square).limit_denominator(16)
    if np.isclose(f.numerator / f.denominator, square):
        return sign + r'\frac{' + latex_sqrt(reduce_int_sqrt(f.numerator)) + '}{' + latex_sqrt(
            reduce_int_sqrt(f.denominator)) + '}'

    return format_raw(raw)


def latex_sqrt(reduce):
    factor = reduce[0]
    radical = reduce[1]
    if radical == 1:
        return str(factor)
    if factor == 1:
        return r'\sqrt{' + str(radical) + '}'
    return str(factor) + r'\sqrt{' + str(radical) + '}'


def format_raw(raw):
    output = np.format_float_positional(raw, precision=4, trim='-')
    ## doesn't seem to trim properly
    if output[-1] == '.':
        output = output[:-1]
    return output


def prime_factors(n):
    i = 2
    factors = []
    while i ** 2 <= n:
        if n % i:
            i += 1
        else:
            n = n / i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors


def reduce_int_sqrt(n):
    factor = 1
    radical = 1
    for prime, prime_group in groupby(prime_factors(n)):
        prime_exponent = len(list(prime_group))
        factor = factor * prime ** (prime_exponent // 2)
        radical = radical * prime ** (prime_exponent % 2)
    return factor, radical


def reverse_string(str):
    return str[::-1]


def print_state_vector(QC):
    state_vector = execute_state_vector(QC)
    print(format_state_vector(state_vector))


def show_state_vector(QC, show_zeros=False, label='\psi'):
    str_state_vector = r'\begin{equation*} \vert ' + label + r'\rangle='
    ket_format = format_state_vector(execute_state_vector(QC), show_zeros)
    is_first = True
    for k, v in sorted(ket_format.items()):
        if not is_first:
            if v.real >= 0:
                str_state_vector += '+'
            else:
                if v.real == 0 and v.imag >= 0:
                    str_state_vector += '+'
        is_first = False
        str_state_vector += format_complex_as_latex(v) + r' \vert' + k + r'\rangle'
    str_state_vector += r'\end{equation*}'
    return str_state_vector


def format_state_vector(state_vector, show_zeros=False):
    binary_vector = {}

    bits = int(math.log(len(state_vector), 2))
    for n in range(len(state_vector)):
        if show_zeros or state_vector[n] != 0:
            ket = f"{n:b}"  ## get the binary for the cell
            ket = ket.rjust(bits, '0')
            ket = reverse_string(ket)
            binary_vector[ket] = state_vector[n]
    return binary_vector


def print_short_state_vector(QC):
    ket_format = format_state_vector(execute_state_vector(QC))
    for k, v in ket_format.items():
        if v.imag != 0:
            print('{0}+{1}I |{2}> '.format(v.real, v.imag, k))
        else:
            print('{0}|{1}> '.format(v.real, k))


def decompose_single(unitary_matrix):
    (theta, phi, lamb) = twoq.euler_angles_1q(unitary_matrix)
    qr = QuantumRegister(1)
    qc = QuantumCircuit(qr)
    qc.append(rrz_gate(lamb), [qr[0]])
    qc.ry(theta, qr[0])
    qc.append(rrz_gate(phi), [qr[0]])
    new = what_is_the_matrix(qc)
    alpha = get_global_phase(unitary_matrix, new)
    print('alpha= {}, beta= {}, gamma= {}, delta={}'
          .format(format_rotation(alpha),
                  format_rotation(phi),
                  format_rotation(theta),
                  format_rotation(lamb)))


def decompose_single_qiskit(unitary_matrix):
    (theta, phi, lamb) = twoq.euler_angles_1q(unitary_matrix)
    qc = QuantumCircuit(1)
    qc.u3(theta, phi, lamb, 0)
    new = what_is_the_matrix(qc)
    alpha = get_global_phase(unitary_matrix, new)
    print('theta= {}, phi= {}, lambda= {}, phase={}'
          .format(format_rotation(theta),
                  format_rotation(phi),
                  format_rotation(lamb),
                  format_rotation(alpha)))


def get_global_phase(original, new):
    if np.allclose(original, new):
        alpha = 0
    else:
        m_factor = original @ np.linalg.inv(new)
        if not np.isclose(m_factor[0, 0], 0):
            factor = phase(m_factor[0, 0])
        else:
            factor = phase(m_factor[0, 1])

        if np.allclose(original,
                       (np.exp(imag * factor)) * new):
            alpha = factor
        else:
            raise ValueError('New Matrix not equal to old ')
    return alpha


def decompose_single_all(decompose, fraction=8):
    found = False
    i = complex(0, 1)
    for a in range(1, 2 * fraction):
        for b in range(0, 2 * fraction):
            for c in range(0, 2 * fraction):
                for d in range(0, 2 * fraction):

                    alpha = pi - (pi / fraction) * a
                    beta = pi - (pi / fraction) * b
                    gamma = pi - (pi / fraction) * c
                    delta = pi - (pi / fraction) * d

                    ar = np.array([[np.cos(alpha) + i * np.sin(alpha), 0],
                                   [0, np.cos(alpha) + i * np.sin(alpha)]])
                    br = np.array([[np.cos(beta / 2) - i * np.sin(beta / 2), 0],
                                   [0, np.cos(beta / 2) + i * np.sin(beta / 2)]])
                    cr = np.array([[np.cos(gamma / 2), -np.sin(gamma / 2)],
                                   [np.sin(gamma / 2), np.cos(gamma / 2)]])
                    dr = np.array([[np.cos(delta / 2) - i * np.sin(delta / 2), 0],
                                   [0, np.cos(delta / 2) + i * np.sin(delta / 2)]])

                    if np.allclose(dr @ cr @ br @ ar, decompose):
                        print('alpha= {}, beta= {} gamma= {} delta= {}'
                              .format(format_rotation(alpha),
                                      format_rotation(beta),
                                      format_rotation(gamma),
                                      format_rotation(delta)))
                        found = True
    if not found:
        print('Didnt find it')


def decompose_single_u3_all(decompose, fraction=8):
    found = False
    i = complex(0, 1)
    for t in range(1, 2 * fraction):
        for l in range(0, 2 * fraction):
            for p in range(0, 2 * fraction):

                theta = pi - (pi / fraction) * t
                lam = pi - (pi / fraction) * l
                phi = pi - (pi / fraction) * p

                u = np.array([[np.cos(theta / 2), -np.exp(i * lam) * np.sin(theta / 2)],
                              [np.exp(i * phi) * np.sin(theta / 2), np.exp(i * lam + i * phi) * np.cos(theta / 2)]])

                if np.allclose(u, decompose):
                    print('theta= {}, phi= {}, lambda= {}'
                          .format(format_rotation(theta),
                                  format_rotation(phi),
                                  format_rotation(lam)))
                    found = True
    if not found:
        print('Didnt find it')


def decompose_single_qiskit_raw(unitary_matrix):
    alpha = phase(np.linalg.det(unitary_matrix) ** (-1.0 / 2.0))

    (theta, lamb, phi) = twoq.euler_angles_1q(unitary_matrix)
    return alpha, theta, lamb, phi


def execute_state_vector(QC):
    backend = Aer.get_backend('statevector_simulator')
    results = execute(QC, backend=backend).result()
    state_vector = results.get_statevector(QC)
    return state_vector


def execute_unitary(QC):
    backend = Aer.get_backend('unitary_simulator')
    results = execute(QC, backend=backend).result()
    unitary = results.get_unitary(QC)
    return unitary


def execute_real(QC, strBackend, shots):
    backend = IBMQ.get_backend(strBackend)
    job = execute(QC, backend=backend, shots=shots)
    job_monitor(job)

    results = job.result()
    answer = results.get_counts()
    return answer


def execute_seeded(QC, shots):
    return execute_simulated(QC, shots, 12345)  ## just a number that will always be the same


def execute_simulated(QC, shots, seed_simulator=None):
    backend = Aer.get_backend("qasm_simulator")
    results = execute(QC, backend=backend, shots=shots, seed_simulator=seed_simulator).result()
    answer = results.get_counts()
    return answer


def simulate(QC, shots, seed_simulator=None):
    results = execute_simulated(QC, shots, seed_simulator)
    print_reverse_results(results)


# Custom Gates

def global_gate(alpha):
    name = 'G \n(' + format_rotation(alpha) + ')'
    sub_global = QuantumCircuit(1, name=name)
    sub_global.rz(alpha, 0)
    sub_global.y(0)
    sub_global.rz(alpha, 0)
    sub_global.y(0)
    return sub_global.to_instruction()


def rrz_gate(beta):
    name = 'RRz \n(' + format_rotation(beta)+ ')'
    sub_rrz = QuantumCircuit(1, name=name)
    sub_rrz.rz(beta / 2, 0)
    sub_rrz.x(0)
    sub_rrz.rz(-beta / 2, 0)
    sub_rrz.x(0)
    return sub_rrz.to_instruction()


def format_rotation(rot):
    fraction = frac.Fraction(round(math.degrees(rot)), 180).limit_denominator(8)
    if np.isclose(fraction * pi, rot):
        if fraction < 0:
            sign = '-'
        else:
            sign = ''
        ret = str(abs(fraction))
        ret = ret.replace('1/', 'pi/')
        if ret == '1':
            return sign + 'pi'
        if ret == '2':
            return sign + '2pi'
        return sign + ret
    else:
        return str(rot)
