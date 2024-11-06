# https://github.com/yongshanding/FastSC/blob/c3d9d92b0d75e8b633ec9fd1e74a6bbb48dc4cab/experiments/frequency_simulate.py

import os, sys, getopt, math, re, random
import numpy as np

import time
from datetime import datetime
#import config


print("Importing qiskit...")
import qiskit
print("Importing fastsc...")
import fastsc
#from fastsc.coloring import success_rate_rand_coloring, success_rate_full_coloring, success_rate_layer_coloring, success_rate_google_like

from fastsc.coloring import static_coloring, color_dynamic, google_like, color_opt
from fastsc.coloring import compute_decoherence, compute_crosstalk_by_layer
from fastsc.models import Device, Sycamore_device
from fastsc.benchmarks import get_circuit

#data_path = config.DATA_PATH
#file_name = datetime.today().strftime("%h%d")

###########################################################
# Simulation Setup
###########################################################

### Device Parameters ###
#side_length = 4
omega_max = 7 #GHz
delta_int = 1.0
delta_ext= 0.5
delta_park = 0.5
alpha = -0.2
ejs = 8
ejl = 20
ec = 0.5
cqq = 0.019

###########################################################
# Simulation
###########################################################

#def reschedule(circ, scheduler):
#    # scheduler = qiskit, local, global
#    res = circ
#    if (scheduler == 'local'):
#        print("Local crosstalk-aware scheduler: Not yet implemented.")
#        # Local crosstalk-aware scheduler
#
#    elif (scheduler == 'global'):
#        print("Global crosstalk-aware scheduler: Not yet implemented.")
#        # Global crosstalk-aware scheduler
#
#    elif (scheduler != 'qiskit'):
#        print("Scheduler %s not recognized." % scheduler)
#    return res


def simulate(device, circuit, mapper, scheduler, freq, dist, decomp, depth=0, lim_colors=0,verbose=0,uniform_freq=0,sigma=0.0,res_coupling=0.0):
    circ = get_circuit(device.qubits, circuit, dep=depth)
    # Crosstalk-aware mapping yet to be implemented.
    #scheduled = reschedule(circ, scheduler)

    #if (freq == 'random'):
        # random coloring
    #    sr, avg, worst, d_before, d_after, t, c, t_act, t_2q = success_rate_rand_coloring(device, circ, scheduler, dist, decomp)

    if (freq == 'full'):
        # Full coloring
        ir = static_coloring(device, circ, scheduler, dist, decomp, verbose, uniform_freq)
        err, swap_err, leak_err = compute_crosstalk_by_layer(device, ir, verbose)
        success = 1. - err
        qb_err = compute_decoherence(device, ir)
        success = success * (1. - qb_err)
        d_before, d_after = ir.depth_before, ir.depth_after
        total_time, max_colors = ir.total_time, ir.max_colors
        #sr, avg, worst, d_before, d_after, t, c, t_act, t_2q = success_rate_full_coloring(device, circ, scheduler, dist, decomp, outputfile, verbose)
    elif (freq == 'layer'):
        # Layered coloring
        ir = color_dynamic(device, circ, scheduler, dist, decomp, lim_colors, verbose)
        err, swap_err, leak_err = compute_crosstalk_by_layer(device, ir, verbose)
        success = 1. - err
        qb_err = compute_decoherence(device, ir)
        success = success * (1. - qb_err)
        d_before, d_after = ir.depth_before, ir.depth_after
        total_time, max_colors = ir.total_time, ir.max_colors
        #sr, avg, worst, d_before, d_after, t, c, t_act, t_2q = success_rate_layer_coloring(device, circ, scheduler, dist, decomp, outputfile, lim_colors, verbose)
    elif (freq == 'google'):
        # with (Google-like) tunable coupling
        ir = google_like(device, circ, scheduler, dist, decomp, verbose, res_coupling)
        err, swap_err, leak_err = compute_crosstalk_by_layer(device, ir, verbose)
        success = 1. - err
        qb_err = compute_decoherence(device, ir)
        success = success * (1. - qb_err)
        d_before, d_after = ir.depth_before, ir.depth_after
        total_time, max_colors = ir.total_time, ir.max_colors
        #sr, avg, worst, d_before, d_after, t, c, t_act, t_2q = success_rate_google_like(device, circ, scheduler, dist, decomp, outputfile, verbose)
    elif (freq == 'opt'):
        # Layered coloring
        ir = color_opt(device, circ, scheduler, dist, decomp, lim_colors, verbose)
        err, swap_err, leak_err = compute_crosstalk_by_layer(device, ir, verbose)
        success = 1. - err
        qb_err = compute_decoherence(device, ir)
        success = success * (1. - qb_err)
        d_before, d_after = ir.depth_before, ir.depth_after
        total_time, max_colors = ir.total_time, ir.max_colors
        #sr, avg, worst, d_before, d_after, t, c, t_act, t_2q = success_rate_layer_coloring(device, circ, scheduler, dist, decomp, outputfile, lim_colors, verbose)
    else:
        success = 0.0
        swap_err = 0.0
        leak_err = 0.0
        qb_err = 0.0
        d_before = 0
        d_after = 0
        total_time = 0.0
        max_colors = 0
    return success, swap_err, leak_err, qb_err, d_before, d_after, total_time, max_colors





###########################################################
# Main procedure
###########################################################

def main():
    #random.seed(60615)
    #np.random.seed(60615)
    circuit = None
    qubits = 0
    mapper = None
    scheduler = None
    freq = None
    dist = None
    decomp = None
    depth = 0
    lim_colors = 0 # when lim_colors=0 we don't limit the number of colors
    verbose = 0 # 0 - verbose, 1 - less verbose
    uniform_freq = 0
    sigma = 0.0
    res_coupling = 0.0
    topology = None
    device_param = None
    try:
        opt, args = getopt.getopt(sys.argv[1:], "hi:p:m:s:f:x:d:q:c:v:u:n:r:t:", ["help", "input=", "depth=", "mapper=", "scheduler=", "frequency=", "crosstalk=", "decomposition=", "qubits=","colors=","verbose=","uniform_freq=","noise=","res_coupling=", "topology="])
    except getopt.GetOptError as err:
        print(err)
        print("Usage: frequency_simulate.py -i <input circuit=bv> -q <num qubits (square)> -p <depth of supremacy circuit> -m <mapper=qiskit> -s <scheduler=qiskit> -f <frequency assignment=full> -x <crosstalk distance=1> -d <circuit decomposition=iswap> -c <max colors> -v <verbosity=1: less verbose> -u <uniform_freq=0> -n <flux noise=0.0> -r <res_coupling> -t <topology>")
        sys.exit(2)
    usage = True
    for o,a in opt:
        usage = False
        if o in ("-h", "--help"):
            print("Usage: frequency_simulate.py -i <input circuit=bv> -q <num qubits (square)> -p <depth of supremacy circuit> -m <mapper=qiskit> -s <scheduler=qiskit> -f <frequency assignment=full> -x <crosstalk distance=1> -d <circuit decomposition=iswap> -c <max colors> -v <verbosity=1: less verbose> -u <uniform_freq=0> -n <flux noise=0.0> -r <res_coupling> -t <topology>")
            sys.exit()
        elif o in ("-i", "--input"): # bv, qgan, qaoa, ising, xeb_iswap_barrier
            circuit = a
        elif o in ("-q", "--qubits"): # 4, 9, 16, 25, ...
            qubits = int(a)
        elif o in ("-p", "--depth"): # parameter for xeb experiments
            depth = int(a)
        elif o in ("-m", "--mapper"): # qiskit
            mapper = a
        elif o in ("-s", "--scheduler"): # qiskit, greedy, tiling
            scheduler = a
        elif o in ("-f", "--frequency"): # full, layer, google, opt
            freq = a
        elif o in ("-x", "--crosstalk"): # 1, 2, 3
            dist = int(a)
        elif o in ("-d", "--decomposition"): # iswap, cphase, flexible
            decomp = a
        elif o in ("-c", "--colors"): # 0, 1, 2, ...
            lim_colors = int(a)
        elif o in ("-v", "--verbose"): # 0 (print trace), 1 (only circuit output)
            verbose = int(a)
        elif o in ("-u", "--uniform_freq"): # 0, 1 (uniform freq assignment)
            uniform_freq = int(a)
        elif o in ("-n", "--noise"): # 0.01 (std dev in flux noise) 
            sigma = float(a)
        elif o in ("-r", "--res_coupling"): # 0.0, 0.1, ... (residual coupling factor)
            res_coupling = float(a)
        elif o in ("-t", "--topology"): 
            # grid, erdosrenyi0.5, cycle, wheel, turan, regular3, hexagonal
            # Note that regular(d,n) must have n*d is even and d < n.
            topology = a
        else:
            print("Usage: frequency_simulate.py -i <input circuit=bv> -q <num qubits (square)> -p <depth of supremacy circuit> -m <mapper=qiskit> -s <scheduler=qiskit> -f <frequency assignment=full> -x <crosstalk distance=1> -d <circuit decomposition=iswap> -c <max colors> -v <verbosity=1: less verbose> -u <uniform_freq=0> -n <flux noise=0.0> -r <res_coupling> -t <topology=grid>")
            sys.exit(2)

    if (usage):
        print("------")
        print("Usage: frequency_simulate.py -i <input circuit=bv> -q <num qubits (square)> -dep <depth of circuit> -m <mapper=qiskit> -s <scheduler=qiskit> -f <frequency assignment=full> -x <crosstalk distance=1> -d <circuit decomposition=iswap> -c <max colors> -v <verbosity=1: less verbose> -u <uniform_freq=0> -n <flux noise=0.0> -r <res_coupling> -t <topology>")
        print("------")

    if (mapper == None): mapper = 'qiskit'
    if (scheduler == None): scheduler = 'qiskit'
    if (freq == None): freq = 'full'
    if (dist == None): dist = 1
    if (decomp == None): decomp = 'iswap'
    supported = ['grid', 'erdosrenyi', 'cycle', 'wheel', 'complete', 'turan', 'regular', 'hexagonal', 'path', 'ibm_falcon', 'ibm_penguin', '1express','2express']
    if (topology == None): 
        topology = 'grid'
    elif ('erdosrenyi' in topology):
        device_param = float(topology[10:]) # edge prob p
        topology = 'erdosrenyi'
    elif ('turan' in topology):
        device_param = int(topology[5:]) # multipartite r disjoint subsets
        topology = 'turan'
    elif ('regular' in topology):
        device_param = int(topology[7:]) # degree d of d-regular graph
        topology = 'regular'
    #elif (topology == 'ibm_falcon'):
    #    qubits = 27
    #elif (topology == 'ibm_penguin'):
    #    qubits = 20
    elif ('express' in topology): # 1express3: 1-d cube (path) express every 3 nodes
        device_param = int(topology[8:])
        topology = topology[:8]
    elif not(topology in supported):
        print("Topology %s not yet supported." % topology)
    #if (outputfile == None): outputfile = file_name

    device = Device(topology, qubits, omega_max, delta_int, delta_ext, delta_park, cqq, alpha, ejs, ejl, ec, d=dist)
    device.build_graph(device_param) # build connectivity and crosstalk graphs

    start = time.time()
    # success, avg, worst, d_before, d_after, t, c, t_act, t_2q = simulate(device, circuit, mapper, scheduler, freq, dist, decomp, outputfile, depth=depth, lim_colors=lim_colors, verbose=verbose)
    success, swap_err, leak_err, qb_err, d_before, d_after, t, c = simulate(device, circuit, mapper, scheduler, freq, dist, decomp, depth=depth, lim_colors=lim_colors, verbose=verbose, uniform_freq=uniform_freq, sigma=sigma, res_coupling=res_coupling)
    # calculate decoherence
    #decoh = compute_decoherence(device, t_act, t_2q)
    #success *= decoh
    end = time.time()
    print("======================")
    # print("Avg(worst) success rate per timestep: %12.10f(%12.10f)" % (avg, worst))
    print("Final success rate: %12.10f" % success)
    print("Swap error: %12.10f" % swap_err)
    print("Leakage error: %12.10f" % leak_err)
    print("Circuit depth: %d, %d" % (d_before, d_after)) # before and after decomp 2-q gates
    print("Circuit execution time: %12.10f ns" % t)
    print("Decoherence error: ", qb_err)
    print("Compilation time: %12.10f s" % (end-start))
    print("Colors: %d" % c)


if __name__ == "__main__":
    main()
