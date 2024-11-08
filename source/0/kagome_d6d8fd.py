# https://github.com/rrodenbusch/open-science-prize-2022/blob/706fd627f3c2f5f2a0037841d425cff241f7e13f/kagome.py
# This code is part of kagome-vqe.
#
# (C) Copyright LJSB Enterprises, LLC 2022.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
"""IBM Open Challenge 2022 KAGOME VQE LATTICE tools


@author: rrodenbusch
"""

import sys
import pandas
import subprocess
import numpy as np
from sympy import init_printing
from time import time

init_printing(use_latex = True )

from qiskit_nature.problems.second_quantization.lattice import Lattice
import rustworkx         as rx
version_info="myTools(major=1, minor=1, micro=0)"


def getVersion(output=True):
    myversion=f"Python: {str(sys.version_info)}\nmyTools: {version_info}\n"
    if output:
        print(myversion)

    return(myversion)


def around(point,nbits=5):
    """Truncate to nbits decimal places

        Args:
            point (float): input value
            nbits (int): number of decimal places
            backend (Backend): The backend properties dictionary
        Returns:
            float: Truncated value
    """
    import numpy as np
    return np.around(point,nbits)

def create_lattice(numNodes,edges):
    # Generate graph of kagome unit cell
    graph = rx.PyGraph(multigraph=False)
    graph.add_nodes_from(range(numNodes))

    # Generate graph from the list of edges
    graph.add_edges_from(edges)

    # Make a Lattice from the graph
    return Lattice(graph)

def draw_lattice(lattice,positions=None,
                 with_labels=True,font_color='white',
                 node_color='purple'):
    style={'with_labels':with_labels, 'font_color':font_color,
           'node_color':node_color, }
    if positions is not None:
        style['pos']=positions
    image = lattice.draw(style=style)
    return image

def get_hamiltonian(lattice,spin_interaction=1.0,global_potential=0.0):
    from heisenberg_model import HeisenbergModel
    from qiskit_nature.mappers.second_quantization import LogarithmicMapper
    heis = HeisenbergModel.uniform_parameters(lattice=lattice,
                                                 uniform_interaction=spin_interaction,
                                                 uniform_onsite_potential=global_potential,
                                                )
    H = 4 * LogarithmicMapper().map(heis.second_q_ops().simplify())
    return H

def get_provider(hub='ibm-q', group='open', project='main', channel='ibm_quantum',
                 compatible=False, output=True, force=False):
    """ Get provider handle from account
            Args:
            Returns:
                Provider: Provider for current account
            Raises:
    """
    from qiskit import IBMQ
    if force or IBMQ.active_account() is None:
        IBMQ.load_account()

    if compatible:
        provider = IBMQ.get_provider(hub='ibm-q', group='open', project='main')
        if output:
            print("Available backends")
            for curBackend in provider.backends():
                print(f"\t{curBackend.name()}")
        return provider
    else:
        from qiskit_ibm_provider import IBMProvider
        from qiskit_ibm_runtime import QiskitRuntimeService

        service = QiskitRuntimeService(channel=channel)
        provider = IBMProvider(instance=f"{hub}/{group}/{project}")
        if output:
            print("Available backends")
            for curBackend in provider.backends():
                print(f"\t{curBackend.name}")
        return provider, service


def init_notebook(output=True):
    """Setup a jupyter notebook with personalized defaults and return Environment

        Args:
            output (Boolean): [True] Print the environment string
        Returns:
            str : Formatted environment string
    """
    import qiskit
    kVersion = f"qTools: {version_info}\nQiskit: {iter2str(dict(qiskit.__qiskit_version__))}"


    if output:
        print(kVersion)

    return(kVersion)



def iter2str(obj,name: str = None,indent: int = 4) -> str:
    """ iter2str
            Format an iterable into a printable string

        Args:
            obj (iterable): Object to be parsed
            name (str): Name of object to insert into string
            indent (str): The string to preprend to all new lines in the lookup

        Returns:
            str: The formatted string
        Raises:
        Examples:
    """
    if obj is None or not isinstance(obj,(tuple,set,list,dict)):
        raise TypeError(f"Argument must be dictionary, received {type(obj)}")
    if isinstance(indent,str):
        indent = len(indent)
    if not isinstance(indent,int):
        raise TypeError(f"Indent must be integer or string received {type(indent)}")

    if not name is None:
        iter_str = f"{name}: {type(obj).__name__}\n"
    else:
        iter_str = f"<{type(obj).__name__}>\n"

    pad = ' ' * indent
    if isinstance(obj,dict):
        for key, nxt_obj in obj.items():
            if isinstance(nxt_obj,(dict,set,tuple,list)):
                iter_str += iter2str(nxt_obj,name=f"{pad}{key}",indent=indent+4)
            else:
                iter_str += f"{pad}{key} : {nxt_obj}\n"
    elif isinstance(obj,(set,tuple,list)):
        idx = 0;
        for nxt_obj in obj:
            if isinstance(nxt_obj,(dict,set,tuple,list)):
                iter_str += iter2str(nxt_obj,name=f"{pad}{idx}",indent=indent+4)
            else:
                iter_str += f"{pad}{idx} -> {nxt_obj}\n"
            idx += 1
    else:
        iter_str += f"{pad}{obj}\n"

    return iter_str


def SparsePauliPrint(pauli,label='Sparse Pauli'):
    cnt=0
    print(f"{label}{pauli.to_matrix().shape} as list:")
    for curItem in pauli.to_list():
        cnt+=1
        print(f"{cnt}:\t{curItem[0]} * {curItem[1]}")
    print("\n")


def save_object(obj,fname):
    import pickle
    with open(fname, 'wb') as obj_file:
        pickle.dump(obj, obj_file)

def load_object(fname):
    import pickle
    with open(fname, 'rb') as obj_file:
        obj = pickle.load(obj_file)
    return obj

def formatDuration(duration):
    days    = divmod(duration, 86400)        # Get days (without [0]!)
    hours   = divmod(days[1], 3600)          # Use remainder of days to calc hours
    minutes = divmod(hours[1], 60)           # Use remainder of hours to calc minutes
    msg = ''
    if int(days[0]) > 0:
        msg += f"{int(days[0])} days, {int(hours[0])} hours, {int(minutes[0])} min"
    elif int(hours[0]) > 0:
        msg += f"{int(hours[0])} hours, {int(minutes[0])} min"
    elif int(minutes[0]) > 0:
        msg += f"{int(minutes[0])} min, {int(minutes[1])} sec"
    else:
        msg += f"{np.around(minutes[1],5)} sec"
    return msg

from qiskit.algorithms import MinimumEigensolver, VQEResult
from qiskit.providers import JobError
import numpy as np
import matplotlib.pyplot as plt
from qiskit.providers.jobstatus import JobStatus
_runningJobs = [JobStatus.INITIALIZING,
                JobStatus.QUEUED,
                JobStatus.VALIDATING,
                JobStatus.RUNNING, ]
_doneJobs    = [JobStatus.CANCELLED, JobStatus.DONE, JobStatus.ERROR, ]

# Define a custome VQE class to orchestra the ansatz, classical optimizers,
# initial point, callback, and final result
class CustomVQE(MinimumEigensolver):

    def __init__(self, estimator, circuit, optimizer, timeout=120, target=None,
                label=None):
        self._estimator     = estimator
        self._circuit       = circuit
        self._optimizer     = optimizer
        self._timeout       = timeout
        self._target        = target
        self._callback_data = []
        self._result        = None
        self._initial_point = None
        self._label         = label

    def _callback(self, value):
        self._callback_data.append(value)

    @property
    def callback_data(self):
        return self._callback_data

    @property
    def initial_point(self):
        return self._initial_point

    @property
    def label(self):
        return self._label

    @property
    def result(self):
        return self._result

    @property
    def target(self) -> int | None:
        return self._target

    def __repr__(self):
        return(f"{self._label}"
               f"{self._target}\n"
               f"{self._initial_point}"
               f"{self._callback_data}"
               f"{self._result}")

    def __str__(self):
        return(f"{self._label}\n"
               f"Target: {self._target}\n"
               f"Result:\n{self._result}\n"
               f"InitialPoint:\n{self._initial_point}\n"
               f"Callback Data:\n{self._callback_data}\n")

    def list_result(self):
        msg =  f"'{self.label}' "
        msg += f"\tComputed: {np.around(self._result.eigenvalue,3)}"
        if self._target is not None:
            rel_error = abs((self._target - self._result.eigenvalue) / self._target)
            msg += f"\tTarget:   {np.around(self.target,3)}"
            msg += f"\tError {np.around(100*rel_error,3)}%"
        return msg

    def show_result(self):
        eigenvalue = self._result.eigenvalue
        print(f'Computed ground state energy: {eigenvalue:.10f}')
        plt.title(self._label)
        plt.plot(self._callback_data, color='purple', lw=2)
        plt.ylabel('Energy')
        plt.xlabel('Iterations')
        if self._target is not None:
            rel_error = abs((self._target - eigenvalue) / self._target)
            print(f'Expected ground state energy: {self._target:.10f}')
            print(f'Relative error: {np.around(100*rel_error,8)}%')
            plt.axhline(y=self._target, color="tab:red", ls="--", lw=2, label="Target: " + str(self._target))
        else:
            plt.axhline(y=eigenvalue, color="tab:red", ls="--", lw=2, label="Target: None" )
        plt.legend()
        plt.grid()
        plt.show()

    def compute_minimum_eigenvalue(self, operators, aux_operators=None, x0=None):

        # Define objective function to classically minimize over
        def objective(x):
            # Execute job with estimator primitive
            try_count = 0
            job_result = None
            start = time()
            while (job_result is None) and (try_count < 2):
                try_count += 1
                jobId = 'UNK'
                try:
                    job = self._estimator.run([self._circuit], [operators], [x])
                    jobId = job.job_id()
                    job_status = job.status()
                    if (job_status is not JobStatus.DONE) and (job_status not in _runningJobs):
                        print(f"Job:{jobId} Try:{try_count} Status:{job_status} T:{time()-start}sec")
                    elif self._timeout is not None:
                        job_result = job.result(timeout=self._timeout)
                    else:
                        job_result = job.result()

                except JobError as ex:
                    print(f"Job:{jobId} Try:{try_count} Status:{job_status} T:{time()-start}sec")
                    print(f"Job {jobId} Try {try_count} Error {ex}")
                    if try_count < 2:
                        pass
                    else:
                        raise ex

            # Get the measured energy value
            value = job_result.values[0]
            # Save result information
            self._callback_data.append(value)
            return value

        # Select an initial point for the ansatzs' parameters
        if x0 is None:
            x0 = np.pi/4 * np.random.rand(self._circuit.num_parameters)
        self._initial_point = x0

        result = VQEResult()

        # Run optimization
        start = time()
        res = self._optimizer.minimize(objective, x0=x0)
        result.optimizer_time = time()-start

        # Populate VQE result
        result.cost_function_evals = res.nfev
        result.eigenvalue = res.fun
        result.optimal_parameters = res.x
        result.optimizer_result = res
        result.optimal_point = np.array(self._callback_data)

        # Update Custom VQE Data
        self._result = result
        return result

def list_results(result):
    results = result
    if not isinstance(results,list):
        results = [result]
    for idx in range(len(results)):
        custom_vqe = results[idx]
        print(f"{idx}: {custom_vqe.list_result()}")
    print("\n")

def load_customVQE(fname):
    import os.path
    if os.path.isfile(fname):
        results = load_object(fname)
    else:
        print(f"File not found.")

        results = []
    print(f"Loaded {len(results)} results")
    return results

def save_customVQE(obj,fname):
    estimators = []
    objList = obj
    if not isinstance(obj,list):
        objList = [obj]
    # runtime estimator causes recursion error on load
    for curObj in objList:
        estimators.append(curObj._estimator)
        curObj._estimator = None

    # save the list
    save_object(objList,fname)

    # restore the estimator
    if isinstance(obj,list):
        for idx in range(len(estimators)):
            obj[idx]._estimator = estimators[idx]
    else:
        obj._estimator = estimators[0]

def runCustomVQE(H, ansatz, optimizer, timeout=120, x0=None, target = None,
                 resultsList=None, service=None, backend=None, label=None):
    if label is None:
        label = "CustomVQE"
    if resultsList is not None:
        label += f" {len(resultsList)}"

    if backend is None:
        from qiskit.primitives import Estimator

        estimator = Estimator([ansatz], [H])
        label += f" Local {optimizer.__class__.__name__}"
        print(label)
        custom_vqe = CustomVQE(estimator, ansatz, optimizer,
                               timeout=None, target=target, label=label)
        result = custom_vqe.compute_minimum_eigenvalue(H,x0=x0)
    else:
        from qiskit_ibm_runtime import Session, Estimator as RuntimeEstimator

        with Session(service=service, backend=backend) as session:
            label += f" {backend} {optimizer.__class__.__name__}"
            print(label)
            estimator = RuntimeEstimator(session=session)
            custom_vqe = CustomVQE(estimator, ansatz, optimizer,
                                   timeout=timeout, target=target, label=label)
            result = custom_vqe.compute_minimum_eigenvalue(H,x0=x0)

    if resultsList is not None:
        resultsList.append(custom_vqe)

    print(f"Runtime {formatDuration(result.optimizer_time)}")
    return custom_vqe





""" Unknown if those below need to be included or not """


def print_dists(points,nPoints):
    def dist(a,b,digits=5):
        a=np.array(a)
        b=np.array(b)
        return np.around(np.linalg.norm(a-b),digits)
    for i in range(nPoints):
        for j in range(i+1,nPoints):
            print(f"dist({i},{j}) = {dist(points[i],points[j])}")




def mytime():
    """ epoch
            Return integer seconds of Unix epoch time
        Args:
        Returns:
            int: Seconds since midnight 1/1/1970
        Raises:
    """
    from time import time
    return(int(time()))

def strtime(epoch=None):
    """ epochString
            Return formatted time string in UTC
        Args:
            epoch: int time, if None current time is used
        Returns:
            str: Formatted time string
        Raises:
    """
    from time import gmtime,asctime
    if epoch is None:
        epoch = mytime()
    return(f"{asctime(gmtime(epoch))} UTC")

def listDir(docDir):
    availfiles = subprocess.run( ["ls","",docDir], capture_output = True)
    filelist = availfiles.stdout.decode()
    lines      = filelist.splitlines()
    dirName    = lines.pop(0)
    print(dirName)
    for x in lines:
        print("   ",x)

def printnl(S):
    """ printnl
            Print a string wihtout a newline character
        Args:
            S (str): The string to print
        Returns:
            String: The formatted string
        Raises:
    """
    print(S,end="")


def sort_lists(xarr,yarr):
    """ sort_lists
            Sort two lists based on first list
        Args:
            xarr (list): X array, list which determines sort oder
            yarr (list): Y array, list to be sorted with xarr
        Returns:
            tuple: sortedX, sortedY arrays
        Raises:
    """
    xarr = np.array(xarr)
    yarr = np.array(yarr)
    indices = xarr.argsort()
    sortX = xarr[indices]
    sortY = yarr[indices]
    return sortX, sortY

def combine_datasets(xvals, yvals):
    """ combine_datasets
            Combine multiple x,y data sets into a single sorted list
        Args:
            xvals (list): List of x arrays
            yvals (list): List of y arrays
        Returns:
            tuple: sortedX, sortedY arrays
        Raises:
    """
    if len(xvals) != len(yvals):
        return None
    xarr = []
    yarr = []
    for idx in range(len(xvals)):
        xarr.extend(xvals[idx])
        yarr.extend(yvals[idx])
    xarr = np.array(xarr)
    yarr = np.array(yarr)
    indices = xarr.argsort()
    sortX = xarr[indices]
    sortY = yarr[indices]
    return sortX, sortY

def classlookup(cls,indent=''):
    """ classlookup
            Return the class hierarchy for all base classses of class

        Args:
            cls (class): The class to lookup
            indent (str): The string to preprend to all new lines in the lookup

        Returns:
            str: The formatted string
        Raises:
        Examples:
    """
    c = list(cls.__bases__)
    cstr = []
    if indent == '':
        cstr = [cls.__name__]
    indent = indent + '    '
    for base in c:
        astr = classlookup(base,indent=indent)
        if astr is not None:
            cstr.append(f"{indent}{base.__name__}")
            cstr.append(astr)
    return cstr


def list2str(obj):
    """ list2str
            Format a list into a printable string

        Args:
            obj (list): Object to be parsed
            name (str): Name of object to insert into string
            indent (str): The string to preprend to all new lines in the lookup

        Returns:
            str: The formatted string
        Raises:
        Examples:
    """
    if isinstance(obj,list):
        if len(obj) > 0:
            for cstr in obj:
                if isinstance(cstr,list):
                    if len(cstr) > 0:
                        list2str(cstr)
                elif cstr is not None:
                    print(cstr)
    elif obj is not None:
        print(obj)


def helloWorld():
    print( "Hello World")


def read_from_file(fname):
    lines = []
    with open(fname,'r') as f:
        lines.append(f.read())
    return lines

def save_object(obj,fname):
    import pickle
    with open(fname, 'wb') as obj_file:
        pickle.dump(obj, obj_file)

def load_object(fname):
    import pickle
    with open(fname, 'rb') as obj_file:
        obj = pickle.load(obj_file)
    return obj

def append_to_file(fname,line,timestamp=False):
    from os import getcwd
    if not isinstance(line,str):
        line=str(line)
    if timestamp:
        from time import time
        epoch = str(int(time()))
        line = f"{epoch},{line}"
    with open(fname,'a+') as f:
        f.write(line)
    return getcwd()

def write_to_file(fname,line,timestamp=False):
    from os import getcwd
    if not isinstance(line,str):
        line=str(line)
    if timestamp:
        from time import time
        epoch = str(int(time()))
        line = f"{epoch},{line}"

    with open(fname,'w') as f:
        f.write(line)
    return getcwd()

if __name__ == "__main__":
    verstr = getVersion(output=True)