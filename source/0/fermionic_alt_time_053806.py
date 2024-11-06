# https://github.com/Qiskit-Extensions/qiskit-alt/blob/874d6e976802d46c7cd0a0f3d5a167ae3ce2931d/bench/fermionic_alt_time.py
# Benchmark qiskit_alt constructing Fermionic operators from pyscf integrals.
import qiskit_alt
qiskit_alt.project.ensure_init()

import timeit

def make_setup_code(basis, geometry):
    return f"""
import qiskit_alt

h2_geometry = [['H', [0., 0., 0.]], ['H', [0., 0., 0.7414]]]

h2o_geometry = [['O', [0., 0., 0.]],
            ['H', [0.757, 0.586, 0.]],
            ['H', [-0.757, 0.586, 0.]]]

from qiskit_alt.electronic_structure import fermionic_hamiltonian
fermionic_hamiltonian({geometry}, {basis})
#qiskit_alt.fermionic_hamiltonian({geometry}, {basis})
"""

def run_one_basis(basis, geometry, num_repetitions):
    setup_code = make_setup_code(basis, geometry)
    bench_code = f"fermionic_hamiltonian({geometry}, {basis})"
    time = timeit.timeit(stmt=bench_code, setup=setup_code, number=num_repetitions)
    t = 1000 * time / num_repetitions
    print(f"geometry={geometry}, basis={basis} {t:0.2f}", "ms")
    return t


def run_benchmarks():
    alt_times = []

    for basis, geometry, num_repetitions in (("'sto3g'", "h2_geometry", 10), ("'631g'", "h2_geometry", 10),
                                             ("'631++g'", "h2_geometry", 10),
                                             ("'sto3g'", "h2o_geometry", 10), ("'631g'", "h2o_geometry", 5)):
        t = run_one_basis(basis, geometry, num_repetitions)
        alt_times.append(t)

    return alt_times


if __name__ == '__main__':
    alt_times = run_benchmarks()
