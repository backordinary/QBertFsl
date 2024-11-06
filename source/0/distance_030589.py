# https://github.com/ThankQ2022/FeaturesForQAOA/blob/15be048ff385f2224fe06d409732e2fa51f5d134/src/distance.py
"""
Author: Minyoung Kim ( June. 30, 2022)
2022 Hackaton 
Team: ThankQ
description: 
distance functions and calculating kernel from quantum feature map is implemented 
"""
import numpy as np

from qiskit_machine_learning.kernels import QuantumKernel
from qiskit import BasicAer
from qiskit.circuit.library import ZZFeatureMap
from qiskit.utils import QuantumInstance, algorithm_globals

def norm(x:np.array):
    """get L2 norm 

    Args:
        x (np.array): vector

    Returns:
        magnitude of x (sum(x^2))^(1/2)
    """
    return np.sqrt(np.dot(x, x))

def sin_dist(x:np.array, y:np.array):
    """get sin distance of two vectors

    Args:
        x (np.array): vector
        y (np.array): another vector same size with x

    Returns:
        float: sqrt(1- cos^2) 
    """
    return np.sqrt(1-(np.dot(x, y)/ norm(x)/norm(y))**2)

def L2(x:np.array, y:np.array):
    """get L2 distance(Euclidean distance) of two vectors

    Args:
        x (np.array): vector
        y (np.array): another vector same size with x

    Returns:
        float : sqrt[sum{(x-y)**2}]
    """
    return norm(x-y)

def L1(x:np.array, y:np.array):
    """get L1 distance(Manhattan distance) of two vectors

    Args:
        x (np.array): vector
        y (np.array): another vector same size with x

    Returns:
        float: mean(abs(x-y))
    """
    return np.mean(np.abs(x-y))
    
#Commonly used functions to calculate distance in feature space 
distance_func_list = [sin_dist, L2, L1 ]

class QuantumKernelMap():
    """Quantum Kernel map construction
    """
    def __init__(self, backend):
        """construct function of quantum kernel map class

        Args:
            backend (_type_): set backend for quantum circuit
        """
        self.backend = backend

    def get_kernel(self, data:np.array):
        """from given data, get kernel with ZZFeatureMap
        
        Args:
            data (np.array): N by M matrix, N: number of data points, M: number of features

        Returns:
            kernel matrix(np.array)
        """
        num_datapt, _  = data.shape
        feature_map =ZZFeatureMap(feature_dimension=num_features, reps=2, entanglement="linear")
        kernel = QuantumKernel(feature_map=feature_map, quantum_instance=self.backend)
        ret = kernel.evaluate(data)
        return ret 

    def get_distance(self, data:np.array, save=False):
        """Get adjacency matrix from kernel 
        Args: 
            data (np.array): N by M matrix, N: number of data points, M: number of features

        Returns:
            adjacency matrix(np.array)
        """
        ret = self.get_kernel(data)
        ret = np.ones_like(ret)-ret
        #Redundant values in diagonal part 
        np.fill_diagonal(ret, 0)

        if save: 
            np.save("../results/kernel.npy", ret)
            print("adjacency matrix is saved in /results/kernel.npy")
        
        return ret
    
    
