# https://github.com/Qiskit-Extensions/qiskit-alt/blob/97f6e8c35aca25db2ce8231a1bbae885c34c9173/bench/run_all_bench.py
import subprocess
import shutil
import os

# Include these lines if we run all files in one process
import qiskit_alt
qiskit_alt.project.ensure_init()


bench_scripts = [
    "fermionic_alt_time.py",
    "fermionic_nature_time.py",
    "from_matrix_alt.py",
    "from_matrix_quantum_info.py",
    "jordan_wigner_alt_time.py",
    "jordan_wigner_nature_time.py",
    "pauli_from_list_alt.py",
    "pauli_from_list_qinfo.py",
    ]


_python = shutil.which("python")

## Run each benchmark script in a separate process
def run_bench(fname):
    dirname = os.path.dirname(os.path.abspath(__file__))
    full = os.path.join(dirname, fname)
    res = subprocess.run(
        [_python, full], check=True, capture_output=True, encoding='utf8'
    ).stdout
    print(res)


def exec_full_dir(fname):
    dirname = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(dirname, fname)
    exec_full(filepath)


def exec_full(filepath):
    global_namespace = {
        "__file__": filepath,
        "__name__": "__main__",
    }
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'), global_namespace)


for fname in bench_scripts:
    print(fname)
    exec_full_dir(fname)
    print()
