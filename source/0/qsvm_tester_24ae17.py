# https://github.com/qismib/QuaKe/blob/135c44e7b5d1de374157042d8c49b456f576d863/src/quake/models/qsvm/qsvm_tester.py
"""
    This module implements a class for comparing classical and quantum Support Vector Machines (SVMs) by realizing training runs, returning the classification scores and several visualizations.
"""
import logging
from pathlib import Path
import pickle
import numpy as np
from qiskit import QuantumCircuit
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from quake.models.svm.utils import extract_feats, rearrange_scale
from quake.models.attention.train import (
    load_and_compile_network as load_attention_network,
)
from typing import Union
from quake.models.attention.attention_dataloading import (
    read_data as read_data_attention,
)
from quake.models.cnn.cnn_dataloading import read_data as read_data_cnn
from quake.models.cnn.train import load_and_compile_network as load_cnn_network
from quake.dataset.generate_utils import Geometry
import matplotlib.pyplot as plt
from qiskit.quantum_info import Statevector
import qutip
from qiskit_machine_learning.kernels import QuantumKernel
import time
from qiskit.circuit.parametervector import ParameterVector

from qiskit.algorithms.optimizers import SPSA
from qiskit_machine_learning.kernels.algorithms import QuantumKernelTrainer
from qiskit.utils import QuantumInstance
from qiskit import Aer
from qiskit_machine_learning.utils.loss_functions import SVCLoss
from typing import Tuple
from quake import PACKAGE

logger = logging.getLogger(PACKAGE + ".qsvm")

class QKTCallback:
    """Callback wrapper class."""

    def __init__(self) -> None:
        self._data = [[] for i in range(5)]

    def callback(self, x0, x1=None, x2=None, x3=None, x4=None):
        """
        Args:
            x0: number of function evaluations
            x1: the parameters
            x2: the function value
            x3: the stepsize
            x4: whether the step was accepted
        """
        self._data[0].append(x0)
        self._data[1].append(x1)
        self._data[2].append(x2)
        self._data[3].append(x3)
        self._data[4].append(x4)

    def get_callback_data(self):
        return self._data

    def clear_callback_data(self):
        self._data = [[] for i in range(5)]


def get_features(
    input_folder: Path,
    extractor_type: str,
    setup: dict,
    seed: int = 42,
    run_tf_eagerly: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    """Getting track features extracted.

    Parameters
    ----------
    input_folder: Path
        The input data folder path.
    extractor_type: str
        Wether to extract with cnn or with attention.
    setup: dict
        Settings dictionary.
    seed: int
        Rng seed for reproducibility
    run_tf_eagerly: bool
        Wether to enable eager execution.

    Raises
    ------
    NotImplementedError
        If extractor type not one of `cnn` or `attention`.

    Returns
    -------
    dataset: list[np.ndarray]
        The featurespace for svm.
    labels: list[np.ndarray]
        The truth labels.
    """
    data_folder = input_folder / Path("data")
    load_map_folder = input_folder / Path("models") / extractor_type
    setup.update({"seed": seed, "run_tf_eagerly": run_tf_eagerly})

    if extractor_type == "cnn":
        read_data_fn = read_data_cnn
        load_net_fn = load_cnn_network
    elif extractor_type == "attention":
        read_data_fn = read_data_attention
        load_net_fn = load_attention_network
    else:
        raise NotImplementedError(
            f"exctractor model not implemented, found: {extractor_type}"
        )

    train_generator, val_generator, test_generator = read_data_fn(
        data_folder, load_map_folder, setup, split_from_maps=True
    )

    geo = Geometry(setup["detector"])

    # extractor setup
    esetup = setup["model"][extractor_type]
    esetup.update({"ckpt": load_map_folder / f"{extractor_type}.h5"})
    network = load_net_fn(esetup, setup["run_tf_eagerly"], geo=geo)
    should_add_extra_feats = setup["model"]["svm"]["should_add_extra_feats"]
    train_features, train_labels = extract_feats(
        train_generator, network, should_add_extra_feats, should_remove_outliers=True
    )
    val_features, val_labels = extract_feats(
        val_generator, network, should_add_extra_feats, should_remove_outliers=False
    )
    test_features, test_labels = extract_feats(
        test_generator, network, should_add_extra_feats, should_remove_outliers=False
    )

    # training and saving the SVMs
    dataset = rearrange_scale(
        train_features,
        val_features,
        test_features,
        setup["model"]["svm"]["should_do_scaling"],
    )
    labels = [train_labels, val_labels, test_labels]

    return dataset, labels


def get_spherical_coordinates(statevector: Statevector, qubit: int) -> list[np.float64]:
    """Getting qubit's spherical coordinates from the quantum vector state.

    Parameters
    ----------
    statevector: Statevector
        The multi-qubit final state.
    qbit: int
        The number of qubits of the circuit.

    Returns
    -------
    [theta, phi]: list[np.float64]
        Qubit's state in the Bloch sphere representation (azimuthal and polar angle).
    """
    state_qubit_base = list(statevector.to_dict().keys())
    state_qubit_amplitudes = list(statevector.to_dict().values())
    s0 = 0
    s1 = 0
    for i, state_qb in enumerate(state_qubit_base):
        if state_qb[qubit] == "0":
            s0 += state_qubit_amplitudes[i]
        else:
            s1 += state_qubit_amplitudes[i]
    r0 = np.abs(s0)
    phi0 = np.angle(s0)
    r1 = np.abs(s1)
    phi1 = np.angle(s1)

    r = np.sqrt(r0**2 + r1**2)
    theta = 2 * np.arccos(r0 / r)
    phi = phi1 - phi0
    return [theta, phi]


def get_subsample(
    dataset: np.ndarray, labels: np.ndarray, size: int, seed: int
) -> Tuple[np.ndarray, np.ndarray]:
    """Returning a smaller subsample of an input dataset.

    Parameters
    ----------
    dataset: np.ndarray
        The features distribution.
    labels: np.ndarray
        The truth labels.
    size: int
        Size of the subsample.
    seed: int
        Seed initialization for reproducibility.

    Returns
    -------
    subs_dataset: np.ndarray
        Subsampling of the feature distribution.
    subs_labels: np.ndarray
        Subsample truth labels.
    """
    subs_dataset, subs_labels = train_test_split(
        dataset, labels, train_size=size, random_state=seed
    )[::2]
    return subs_dataset, subs_labels


def align_kernel(
    kernel: QuantumKernel, dataset: np.ndarray, labels: np.ndarray, c: float
):
    """Performing kernel alignment with Statevector backend. It maximizes the accuracy on a validation set.

    Parameters
    ----------
    kernel: QuantumKernel
        The parametric circuit for encoding.
    dataset: np.ndarray
        The features distribution.
    labels: np.ndarray
        The truth labels.
    c: float
        The cost SVM hyperparameter.

    Returns
    -------
    aligned_kernel: QuantumKernel
        The aligned parametric circuit for encoding
    """

    if labels.shape[0] > 500:
        dataset, labels = get_subsample(dataset, labels, 500, 42)

    loss_func = SVCLoss(C=c)
    initial_point = np.zeros(len(kernel.get_unbound_user_parameters()))
    cb_qkt = QKTCallback()  # get_callback_data()
    spsa_opt = SPSA(
        maxiter=20, callback=cb_qkt.callback
    )  # , learning_rate=0.01, perturbation=0.01)
    qkt = QuantumKernelTrainer(
        quantum_kernel=kernel,
        loss=loss_func,
        optimizer=spsa_opt,
        initial_point=initial_point,
    )
    qka_results = qkt.fit(dataset, labels)
    logger.info(qka_results)
    aligned_kernel = qka_results.quantum_kernel
    logger.info(cb_qkt.get_callback_data()[2])
    opt_data = [qka_results, cb_qkt]
    return aligned_kernel, opt_data


def plot_bloch(
    x: ParameterVector,
    quantum_kernel: QuantumKernel,
    train_set: np.ndarray,
    color_labels: np.ndarray,
    path: Path,
    kernel_title: str,
) -> plt.figure:
    """Plotting and saving the quantum-encoded dataset on Bloch spheres.

    Parameters
    ----------
    x: ParameterVector
        The free parameters of the circuit.
    quantum_kernel: QuantumKernel
        The encoding parametric circuit.
    train_set: np.ndarray
        Points to encode in the quantum state.
    color_labels: np.ndarray
        Truth labels or prediction outcome.
    path: Path
        Saving directory.
    kernel_title: str
        Kernel name.

    Returns
    -------
    fig: plt.figure
        Plot of the encoded distribution.
    """
    featuremap = quantum_kernel.feature_map
    nqubits = featuremap.num_qubits
    if nqubits > 2:
        cols = 3
        rows = nqubits // cols + 1
    else:
        cols = nqubits
        rows = 1

    fig = plt.figure(constrained_layout=True, figsize=(6 * rows, 6 * rows))

    if quantum_kernel.user_parameters:
        featuremap = quantum_kernel.feature_map
    for qb in range(nqubits):
        ax = fig.add_subplot(rows, cols, qb + 1, projection="3d")
        b = qutip.Bloch(fig=fig, axes=ax)
        b.point_size = [5]
        b.point_marker = ["o"]
        pnts = np.zeros((len(color_labels), 3))

        for i, val in enumerate(train_set):
            bound_circuits = featuremap.assign_parameters({x: val})
            state = Statevector.from_instruction(bound_circuits)
            spherical = get_spherical_coordinates(state, qb)
            xs = np.sin(spherical[0]) * np.cos(spherical[1])
            ys = np.sin(spherical[0]) * np.sin(spherical[1])
            zs = np.cos(spherical[0])
            pnts[i] = [xs, ys, zs]
        b.add_points(pnts[color_labels == 1].T)
        b.add_points(pnts[color_labels == 0].T)
        b.render()
        ax.set_title(f"Feature {qb}", y=1.1, fontsize=10)

    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D

    legend_elements = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label=r"$0\nu\beta\beta$",
            markerfacecolor="r",
            markersize=10,
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label=r"$\beta$",
            markerfacecolor="b",
            markersize=10,
        ),
    ]
    fig.legend(handles=legend_elements, loc=(0.85, 0.75))

    if nqubits > 5:
        resolution = 500 * 5 / nqubits
    else:
        resolution = 500

    save_object(path, fig, "Bloch Sphere" + kernel_title + ".png", dpi=resolution)


accuracy = lambda label, y: np.sum(label == y) / label.shape[0]


def make_kernels(
    maps: list[QuantumCircuit], backend: Union[Aer.get_backend, QuantumInstance]
) -> list[QuantumKernel]:
    """Returning quantum kernels from quantum featuremaps.

    Parameters
    ----------
    maps: list[QuantumCircuit],
        Quantum featuremaps.
    backend: Union[Aer.get_backend, QuantumInstance]
        Backend for circuit execution

    Returns
    -------
    kernels: list[QuantumKernel]
        Quantum kernels associated to the featuremaps.
    """

    kernels = []
    for fmap in maps:
        if len(fmap.parameters) > len(fmap.qubits):
            theta = fmap.parameters[len(fmap.qubits) :]
            kernels.append(
                QuantumKernel(
                    feature_map=fmap,
                    user_parameters=theta,
                    quantum_instance=backend,
                )
            )
        else:
            kernels.append(QuantumKernel(feature_map=fmap, quantum_instance=backend))
    return kernels


def save_object(directory: Path, var: dict, name: str, dpi: int = 500):
    """Saving pickle or png images in a folder.

    Parameters
    ----------
    directory: Path
        Folder path.
    var: dict
        Object to save.
    name: str
        Filename.
    dpi: int
        Dot per inch picture resolution option.
    """
    if name.endswith(".pkl"):
        with open(directory / Path(name), "wb") as f:
            pickle.dump(var, f)
    elif name.endswith(".png"):
        var.savefig(directory / Path(name), bbox_inches="tight", dpi=dpi)
    else:
        logger.info(f'{"Could not save "} {name} {", can only save .pkl and .png"}')


def plot_data_2d(dataset: list[np.ndarray], labels: list[np.ndarray]) -> plt.figure:
    """Creating a picture that displays feature distribution of a 2D dataset.

    Parameters
    -----------
    dataset: list[np.ndarray]
        The featurespace for SVM.
    labels: list[np.ndarray]
        The truth labels.

    Returns
    -------
    fig: plt.figure
        Figure showing 1D and 2D feature distributions.
    """

    fig = plt.figure(figsize=(50, 100))
    fig, axs = plt.subplots(2, 2)
    fig.set_figheight(10)
    fig.set_figwidth(15)
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    x1_min, x1_max = np.min(dataset[0][:, 0]), np.max(dataset[0][:, 0])
    x2_min, x2_max = np.min(dataset[0][:, 1]), np.max(dataset[0][:, 1])
    x_min, x_max = np.min([x1_min, x2_min]), np.max([x1_max, x2_max])
    correlation_coefficients = np.zeros(2)
    axs[0, 0].hist(
        dataset[0][labels[0] == 0, 0], range=[x_min, x_max], bins=50, alpha=0.6
    )
    axs[0, 0].hist(
        dataset[0][labels[0] == 1, 0], range=[x_min, x_max], bins=50, alpha=0.6
    )
    axs[0, 0].legend(["Single beta", "Double beta"])
    axs[0, 0].set_title("Feature " + str(0))

    axs[1, 0].scatter(
        dataset[0][labels[0] == 0, 0],
        dataset[0][labels[0] == 0, 1],
        s=1,
        alpha=0.3,
    )
    axs[1, 0].scatter(
        dataset[0][labels[0] == 1, 0],
        dataset[0][labels[0] == 1, 1],
        s=1,
        alpha=0.3,
    )
    axs[1, 0].set_xlim([x1_min, x1_max])
    axs[1, 0].set_ylim([x2_min, x2_max])
    axs[1, 0].set_xlabel("Feature 0")
    axs[1, 0].set_ylabel("Feature 1")
    if 0 == 0:
        axs[1, 0].set_title("Training sample distribution")
    elif 0 == 1:
        axs[1, 0].set_title("Validation sample distribution")

    correlation_coefficients[0] = np.corrcoef(dataset[0][:, 0], dataset[0][:, 1])[
        0, 1
    ]

    # axs[1, i].text(
    #     0.6,
    #     -1.2,
    #     f"L. correlation = {correlation_coefficients[i]:.2}",
    #     bbox=props,
    # )

    axs[1, 0].text(
        (x1_max - x1_min) * 0.7 + x1_min,
        (x2_max - x2_min) * 0.75 + x2_min,
        f"L. correlation = {correlation_coefficients[0]:.2}",
        bbox=props,
    )

    axs[1, 0].legend(["Single beta", "Double beta"])
    axs[0, 1].hist(
        dataset[0][labels[0] == 0, 1], range=[x_min, x_max], bins=50, alpha=0.6
    )
    axs[0, 1].hist(
        dataset[0][labels[0] == 1, 1], range=[x_min, x_max], bins=50, alpha=0.6
    )
    axs[0, 1].legend(["Single beta", "Double beta"])
    axs[0, 1].set_title("Feature " + str(1))

    axs[1, 1].scatter(
        dataset[1][labels[1] == 0, 0],
        dataset[1][labels[1] == 0, 1],
        s=1,
        alpha=0.3,
    )
    axs[1, 1].scatter(
        dataset[1][labels[1] == 1, 0],
        dataset[1][labels[1] == 1, 1],
        s=1,
        alpha=0.3,
    )
    axs[1, 1].set_xlim([x1_min, x1_max])
    axs[1, 1].set_ylim([x2_min, x2_max])
    axs[1, 1].set_xlabel("Feature 0")
    axs[1, 1].set_ylabel("Feature 1")
    if 1 == 0:
        axs[1, 1].set_title("Training sample distribution")
    elif 1 == 1:
        axs[1, 1].set_title("Validation sample distribution")

    correlation_coefficients[1] = np.corrcoef(dataset[1][:, 0], dataset[1][:, 1])[
        0, 1
    ]

    # axs[1, i].text(
    #     0.6,
    #     -1.2,
    #     f"L. correlation = {correlation_coefficients[i]:.2}",
    #     bbox=props,
    # )

    axs[1, 1].text(
        (x1_max - x1_min) * 0.7 + x1_min,
        (x2_max - x2_min) * 0.75 + x2_min,
        f"L. correlation = {correlation_coefficients[1]:.2}",
        bbox=props,
    )

    axs[1, 1].legend(["Single beta", "Double beta"])

    return fig


def plot_data_nd(
    dataset: list[np.ndarray], labels: list[np.ndarray], nfeatures: int
) -> plt.figure:
    """Creating a picture that displays feature distribution of a n-dimensional dataset.

    Parameters
    -----------
    dataset: list[np.ndarray]
        The featurespace for SVM.
    labels: list[np.ndarray]
        The truth labels.
    nfeatures: int
        The number of features in the dataset.

    Returns
    -------
    fig: plt.figure
        Figure showing the feature distributions.
    fig: plt.figure
        Figure showing the correlation matrix.
    """
    rows = (nfeatures - 1) // 2 + 1
    if nfeatures == 1:
        cols = 1
    else:
        cols = 2
    fig, axs = plt.subplots(rows, cols)
    fig.set_figheight(5 * rows)
    fig.set_figwidth(5 * cols)

    for i in range(nfeatures):
        x_min, x_max = np.min(dataset[0][:, i]), np.max(dataset[0][:, i])
        col = i % 2
        row = i // 2
        axs[row, col].hist(
            dataset[0][labels[0] == 0, i], range=[x_min, x_max], bins=50, alpha=0.6
        )
        axs[row, col].hist(
            dataset[0][labels[0] == 1, i], range=[x_min, x_max], bins=50, alpha=0.6
        )
        axs[row, col].legend(["Single beta", "Double beta"])
        axs[row, col].set_title(f" Feature {i}")

    fig_correlation_matrix = plt.matshow(
        np.abs(np.asmatrix(np.corrcoef(dataset[0].T))),
        interpolation="nearest",
        origin="upper",
        cmap="Blues",
    ).figure
    plt.xticks(
        np.arange(nfeatures), [f"feature{i}" for i in range(nfeatures)], fontsize=8
    )
    plt.yticks(
        np.arange(nfeatures), [f"feature{i}" for i in range(nfeatures)], fontsize=8
    )

    plt.colorbar(orientation="vertical")
    plt.title("Correlation matrix (abs values)")
    return fig, fig_correlation_matrix


def train_classic(
    training_dataset: np.ndarray,
    training_labels: np.ndarray,
    val_dataset: np.ndarray,
    test_dataset: np.ndarray,
    opts: list[dict],
) -> tuple([list[SVC], list[np.ndarray], list[np.ndarray], list[np.ndarray]]):
    """Training an ensamble of classical SVMs on the same dataset.

    Parameters
    -----------
    training_dataset: np.ndarray
        Dataset for training.
    training_labels: np.ndarray
        Truth labels.
    val_dataset: np.ndarray
        Dataset for validation.
    test_dataset: np.ndarray
        Dataset for test.
    opts: list[dict]
        Hyperparameters settings.

    Returns
    -------
    svcs: list[SVC]:
        Model list.
    pred_train: list[np.ndarray]
        Train prediction list.
    pred_val: list[np.ndarray]
        Validation prediction list.
    pred_test: list[np.ndarray]
        Test prediction list.
    """
    svcs = []
    pred_train = []
    pred_val = []
    pred_test = []
    svcs.append(SVC(**opts[0]).fit(training_dataset, training_labels))
    pred_train.append(svcs[-1].predict(training_dataset))
    pred_val.append(svcs[-1].predict(val_dataset))
    pred_test.append(svcs[-1].predict(test_dataset))
    svcs.append(SVC(**opts[1]).fit(training_dataset, training_labels))
    pred_train.append(svcs[-1].predict(training_dataset))
    pred_val.append(svcs[-1].predict(val_dataset))
    pred_test.append(svcs[-1].predict(test_dataset))
    svcs.append(SVC(**opts[2]).fit(training_dataset, training_labels))
    pred_train.append(svcs[-1].predict(training_dataset))
    pred_val.append(svcs[-1].predict(val_dataset))
    pred_test.append(svcs[-1].predict(test_dataset))
    return svcs, pred_train, pred_val, pred_test


def train_quantum(
    training_dataset: np.ndarray,
    training_labels: np.ndarray,
    val_dataset: np.ndarray,
    test_dataset: np.ndarray,
    quantum_kernels: list[QuantumKernel],
    cs: list[float],
) -> tuple(
    [
        list[SVC],
        list[np.ndarray],
        list[np.ndarray],
        list[np.ndarray],
        list[np.ndarray],
    ]
):
    """Training an ensamble of classical QSVMs on the same dataset.

    Parameters
    -----------
    training_dataset: np.ndarray
        Dataset for training.
    training_labels: np.ndarray
        Truth labels.
    val_dataset: np.ndarray
        Dataset for validation.
    test_dataset: np.ndarray
        Dataset for test.
    quantum_kernels: list[QuantumKernel]
        Quantum kernels of the QSVMs.
    cs: list[float]:
        Cost hyperparameters.

    Returns
    -------
    svcs: list[SVC]:
        Model list.
    pred_train: list[np.ndarray]
        Train prediction list.
    pred_val: list[np.ndarray]
        Validation prediction list.
    pred_test: list[np.ndarray]
        Test prediction list.
    kers: list[np.ndarray]
        Training kernel matrix.
    """
    kers = []
    svcs = []
    pred_train = []
    pred_val = []
    pred_test = []
    for q, encoding in enumerate(quantum_kernels):
        ker_matrix_train = encoding.evaluate(x_vec=training_dataset)
        ker_matrix_val = encoding.evaluate(x_vec=val_dataset, y_vec=training_dataset)
        ker_matrix_test = encoding.evaluate(x_vec=test_dataset, y_vec=training_dataset)
        if training_labels.shape[0] < 201:
            kers.append(np.real(ker_matrix_train))
        clf = SVC(kernel="precomputed", C=cs[q]).fit(ker_matrix_train, training_labels)
        svcs.append(clf)
        pred_train.append(clf.predict(ker_matrix_train))
        pred_val.append(clf.predict(ker_matrix_val))
        pred_test.append(clf.predict(ker_matrix_test))

    return svcs, pred_train, pred_val, pred_test, kers


class SvmsComparison:
    """Class that trains and compares SVMs and QSVMs."""

    def __init__(
        self,
        x: ParameterVector = None,
        quantum_featuremaps: list[QuantumCircuit] = [],
        quantum_kernels: list[QuantumKernel] = [],
        cs: list[float] = None,
        backend: Union[Aer.get_backend, QuantumInstance] = Aer.get_backend(
            "statevector_simulator"
        ),
        folder_name: Path = None,
        training_size: list[int] = [10, 20, 50, 100, 200],
        val_size: int = 200,
        test_size: int = 200,
        folds: int = 20,
        kernel_names: list[str] = None,
        classic_opts=None,
    ):
        """
        Parameters:
        x: ParameterVector
            The free parameters of the circuit.
        quantum_featuremaps: list[QuantumCircuit]
            The quantum featuremaps.
        quantum_kernels: list[QuantumKernel]
            The quantum kernels.
        cs: list[float]
            Penalty hyperparameters for the SVM algorithm.
        backend: Union[Aer.get_backend, QuantumInstance]
            Backend for kernel matrices computations.
        training_size: list[int]
            Sizes of the training dataset.
        val_size: int
            Size of the validation dataset.
        test_size: int
            Size of the testing dataset.
        folds: int
            Number of trainings to execute for each element of training_size.
        folder_name: Path
            Folder name in which to save results.
        Kernel_Names list[str]:
            Names of the quantum encodings.
        """
        self.x = x
        self.quantum_featuremaps = quantum_featuremaps
        self.quantum_kernels = quantum_kernels
        self.cs = cs
        self.training_size = training_size
        self.val_size = val_size
        self.test_size = test_size
        self.folds = folds
        self.opts = classic_opts
        if folder_name:
            self.path = Path("../../") / folder_name
        self.titles = ["Linear", "Polynomial", "Rbf"] + kernel_names
        self.backend = backend
        self.alignment = False
        for kernels in self.quantum_kernels:
            if kernels.user_parameters:
                self.alignment = True
                break

    def make_folder(self):
        """Creating the folder in the path stored in self.path. If self.path does not exists, the folder name is the datetime."""

        if not hasattr(self, "path"):
            t = time.strftime("%Y_%m_%d-%Hh%Mm")
            self.path = Path("../../" + str(t))
        self.path.mkdir(exist_ok=True)

    def plot_data(self, dataset: list[np.ndarray], labels: list[np.ndarray]):
        """Plotting the feature distributions.

        Parameters:
        ----------
        dataset: list[np.ndarray]
            The featurespace for SVM.
        labels: list[np.ndarray]
            The truth labels.
        """
        logger.info(f"Plotting the dataset")
        nfeatures = dataset[0].shape[1]
        if nfeatures == 2:
            self.feature_distributions = plot_data_2d(dataset, labels)
        elif nfeatures > 2:
            self.feature_distributions, self.correlation_matrix = plot_data_nd(
                dataset, labels, nfeatures
            )

    def train_svms(self, dataset: list[np.ndarray], labels: list[np.ndarray]):
        """Training classical and quantum SVMs and getting the predictions for different training set size and subsamples.

        Parameters:
        -----------
        dataset: list[np.ndarray]
            The featurespae for SVM.
        labels: list[np.ndarray]
            The truth labels.
        """
        logger.info(f"Starting the training session")
        svms_batch = []  # [trsize, folds, number of kernels]
        train_batch = []  # [trsize, folds, 0]; [trsize, folds, 1]
        validation_batch = []
        test_batch = []
        kernels_batch = []  # [trsize, folds, number of quantum kernels]
        training_preds_batch = []
        validation_preds_batch = []
        test_preds_batch = []

        seed = np.arange(166, 166 + self.folds)  # era 1

        self.do_kernel_alignment(dataset[0], labels[0])
        for trs in self.training_size:
            svms = []
            train = []
            validation = []
            test = []
            kernels = []
            train_preds = []
            validation_preds = []
            test_preds = []
            for i in range(0, self.folds):
                logger.info(f"Training subset {i} with {trs} samples.")
                subset_train_data, subset_train_labels = get_subsample(
                    dataset[0], labels[0], trs, seed[i]
                )
                subset_val_data, subset_val_labels = get_subsample(
                    dataset[1],
                    labels[1],
                    self.val_size,
                    seed[i],
                )

                subset_test_data, subset_test_labels = get_subsample(
                    dataset[2],
                    labels[2],
                    self.test_size,
                    seed[i],
                )

                svcs = []
                kers = []
                tr_preds = []
                val_preds = []
                te_preds = []
                classic_output = train_classic(
                    subset_train_data,
                    subset_train_labels,
                    subset_val_data,
                    subset_test_data,
                    self.opts,
                )
                quantum_output = train_quantum(
                    subset_train_data,
                    subset_train_labels,
                    subset_val_data,
                    subset_test_data,
                    self.quantum_kernels,
                    self.cs,
                )
                tot_output = []
                for k in range(4):
                    tot_output.append(classic_output[k] + quantum_output[k])
                svcs, tr_preds, val_preds, te_preds = tot_output
                kers = quantum_output[-1]

                svms.append(svcs)
                train.append([subset_train_data, subset_train_labels])
                validation.append([subset_val_data, subset_val_labels])
                test.append([subset_test_data, subset_test_labels])
                kernels.append(kers)
                train_preds.append(tr_preds)
                validation_preds.append(val_preds)
                test_preds.append(te_preds)

            svms_batch.append(svms)
            train_batch.append(train)
            validation_batch.append(validation)
            test_batch.append(test)
            if trs < 201:
                kernels_batch.append(kernels)
            training_preds_batch.append(train_preds)
            validation_preds_batch.append(validation_preds)
            test_preds_batch.append(test_preds)

        self.svms = svms_batch
        self.train = train_batch
        self.validation = validation_batch
        self.test = test_batch
        if kernels_batch:
            self.kernels = kernels_batch
        self.train_preds = training_preds_batch
        self.validation_preds = validation_preds_batch
        self.test_preds = test_preds_batch

    def save(self, setting: dict):
        """Saving results and specifications into a folder, if they were previously produced.

        Parameters:
        -----------
        setting: dict
            Training session specifications.
        """
        logger.info(f"Saving data in {self.path}")
        self.make_folder()
        save_object(self.path, setting, "setup.pkl")
        if hasattr(self, "svms"):
            save_object(self.path, self.svms, "SVMS.pkl")
        if hasattr(self, "train"):
            save_object(self.path, self.train, "TRAIN.pkl")
        if hasattr(self, "validation"):
            save_object(self.path, self.validation, "VALIDATION.pkl")
        if hasattr(self, "test"):
            save_object(self.path, self.test, "TEST.pkl")
        if hasattr(self, "kernels"):
            save_object(self.path, self.kernels, "KERNELS.pkl")
        if hasattr(self, "train_preds"):
            save_object(self.path, self.train_preds, "TRAIN_PREDICTIONS.pkl")
        if hasattr(self, "validation_preds"):
            save_object(self.path, self.validation_preds, "VALIDATION_PREDICTIONS.pkl")
        if hasattr(self, "test_preds"):
            save_object(self.path, self.test_preds, "TEST_PREDICTIONS.pkl")
        if hasattr(self, "feature_distributions"):
            save_object(
                self.path, self.feature_distributions, "feature_distributions.png"
            )
        if hasattr(self, "correlation_matrix"):
            save_object(self.path, self.correlation_matrix, "correlation_matrix.png")
        if hasattr(self, "learning_curve"):
            save_object(self.path, self.learning_curve, "learning_curve.png")
        if hasattr(self, "learning_curve_cv"):
            save_object(self.path, self.learning_curve_cv, "learning_curve_cv.png")
        if hasattr(self, "kernel_plot"):
            save_object(self.path, self.kernel_plot, "kernel_plot.png")
        if hasattr(self, "backend_compare_scores"):
            save_object(
                self.path, self.backend_compare_scores, "ACCURACY_other_backend.pkl"
            )
        if hasattr(self, "backend_compare_scores_all"):
            save_object(
                self.path,
                self.backend_compare_scores_all,
                "ACCURACY_other_backend_all.pkl",
            )
        if hasattr(self, "opt_data"):
            save_object(self.path, self.opt_data, "Alignment_data.pkl")

        if hasattr(self, "backend_plot"):
            subfolder = self.path / Path("Backend Comparisons")
            subfolder.mkdir(exist_ok=True)
            for i in range(len(self.backend_plot)):
                save_object(
                    subfolder, self.backend_plot[i], self.titles[3 + i] + ".png"
                )

        if hasattr(self, "featuremaps_plot"):
            subfolder = self.path / Path("Featuremaps")
            subfolder.mkdir(exist_ok=True)
            for i in range(len(self.featuremaps_plot)):
                save_object(
                    subfolder, self.featuremaps_plot[i], self.titles[3 + i] + ".png"
                )

        # if hasattr(self, "bloch_sphere_list"):
        #     subfolder = self.path / Path("Bloch Spheres")
        #     subfolder.mkdir(exist_ok=True)
        #     for i in range(len(self.bloch_sphere_list)):
        #         save_object(
        #             subfolder,
        #             self.bloch_sphere_list[i],
        #             "Bloch_Spheres" + self.titles[3 + i] + ".png",
        #         )

    def load_files(self, path: Path):
        """Loading results contained in a folder into class fields.

        Parameters:
        path: Path
            Output folder name.
        """
        logger.info(f"Loading data from {self.path}")
        with open(path / Path("SVMS.pkl"), "rb") as f:
            self.svms = pickle.load(f)
        with open(path / Path("TRAIN.pkl"), "rb") as f:
            self.train = pickle.load(f)
        with open(path / Path("VALIDATION.pkl"), "rb") as f:
            self.validation = pickle.load(f)
        with open(path / Path("TEST.pkl"), "rb") as f:
            self.test = pickle.load(f)
        with open(path / Path("KERNELS.pkl"), "rb") as f:
            self.kernels = pickle.load(f)
        with open(path / Path("TRAIN_PREDICTIONS.pkl"), "rb") as f:
            self.train_preds = pickle.load(f)
        with open(path / Path("VALIDATION_PREDICTIONS.pkl"), "rb") as f:
            self.validation_preds = pickle.load(f)
        with open(path / Path("TEST_PREDICTIONS.pkl"), "rb") as f:
            self.test_preds = pickle.load(f)
        if (path / Path("Alignment_data.pkl")).is_file():
            with open(path / Path("Alignment_data.pkl"), "rb") as f:
                self.test_preds = pickle.load(f)

    def learning_curves(self):
        """Plotting learning curves for the different kernels."""
        logger.info("Plotting the learning curves")
        fig = plt.figure(figsize=(50, 100))
        fig, axs = plt.subplots(2, 2)
        fig.set_figheight(10)
        fig.set_figwidth(15)

        acc_train = np.zeros((len(self.titles), len(self.training_size), self.folds))
        acc_validation = np.zeros(
            (len(self.titles), len(self.training_size), self.folds)
        )
        acc_test = np.zeros((len(self.titles), len(self.training_size), self.folds))
        for i, (tr_pred1, val_pred1, te_pred1) in enumerate(
            zip(self.train_preds, self.validation_preds, self.test_preds)
        ):
            for j, (tr_pred2, val_pred2, te_pred2) in enumerate(
                zip(tr_pred1, val_pred1, te_pred1)
            ):
                for k, (tr_pred3, val_pred3, te_pred3) in enumerate(
                    zip(tr_pred2, val_pred2, te_pred2)
                ):
                    acc_train[k, i, j] = accuracy(
                        np.array(self.train[i][j][1]), tr_pred3
                    )
                    acc_validation[k, i, j] = accuracy(
                        np.array(self.validation[i][j][1]), val_pred3
                    )
                    acc_test[k, i, j] = accuracy(np.array(self.test[i][j][1]), te_pred3)
        n = np.sqrt(acc_train[0][0].shape[0])
        y = [
            np.mean(acc_train, axis=2),
            np.mean(acc_validation, axis=2),
            np.mean(acc_test, axis=2),
        ]
        yerr = [
            np.std(acc_train, axis=2) / n,
            np.std(acc_validation, axis=2) / n,
            np.std(acc_test, axis=2) / n,
        ]

        ylims = [[0, 1], [0, 1], [0, 1]]
        subtitle = [
            "Accuracy on training set",
            "Accuracy on validation set",
            "Accuracy on testing set",
        ]
        col = 0 % 2
        row = 0 // 2
        for i in range(len(self.titles)):
            if yerr[0][i].sum() == 0:
                axs[row, col].plot(
                    self.training_size, y[0][i], linewidth=2, marker="."
                )
            else:
                axs[row, col].errorbar(
                    x=self.training_size, y=y[0][i], yerr=yerr[0][i]
                )
        axs[row, col].legend(self.titles)
        axs[row, col].set_title(subtitle[0])
        axs[row, col].set_xlabel("Training set size")
        axs[row, col].set_ylim(ylims[0])
        col = 1 % 2
        row = 1 // 2
        for i in range(len(self.titles)):
            if yerr[1][i].sum() == 0:
                axs[row, col].plot(
                    self.training_size, y[1][i], linewidth=2, marker="."
                )
            else:
                axs[row, col].errorbar(
                    x=self.training_size, y=y[1][i], yerr=yerr[1][i]
                )
        axs[row, col].legend(self.titles)
        axs[row, col].set_title(subtitle[1])
        axs[row, col].set_xlabel("Training set size")
        axs[row, col].set_ylim(ylims[1])
        col = 2 % 2
        row = 2 // 2
        for i in range(len(self.titles)):
            if yerr[2][i].sum() == 0:
                axs[row, col].plot(
                    self.training_size, y[2][i], linewidth=2, marker="."
                )
            else:
                axs[row, col].errorbar(
                    x=self.training_size, y=y[2][i], yerr=yerr[2][i]
                )
        axs[row, col].legend(self.titles)
        axs[row, col].set_title(subtitle[2])
        axs[row, col].set_xlabel("Training set size")
        axs[row, col].set_ylim(ylims[2])
        self.learning_curve = fig

    def plot_kernels(self):
        """Plotting the kernel matrices and returning the sum of all the elements as an indicator of data sparsity."""
        if not hasattr(self, "kernels"):
            return
        logger.info("Plotting kernel matrices")
        nkernels = len(self.quantum_kernels)
        fig = plt.figure(constrained_layout=True)
        rows = (nkernels - 1) // 2 + 1

        if nkernels != 1:
            for j in range(nkernels):

                try:
                    ker = self.kernels[-1][0][j]
                except:
                    try:
                        ker = self.kernels[-1][j]
                    except:
                        ker = self.kernels[j]

                if nkernels == 2:
                    ax = fig.add_subplot(1, 2, j + 1)
                    kern_img = ax.imshow(
                        np.asmatrix(ker),
                        interpolation="nearest",
                        origin="upper",
                        cmap="Blues",
                    )
                    ax.set_title(f'{self.titles[j + 3]} {" sum: "} {np.sum(ker):.0f}')
                    fig.colorbar(kern_img, ax=ax, fraction=0.046, pad=0.04)
                else:
                    ax = fig.add_subplot(rows, 2, j + 1)
                    kern_img = ax.imshow(
                        np.asmatrix(ker),
                        interpolation="nearest",
                        origin="upper",
                        cmap="Blues",
                    )
                    ax.set_title(f'{self.titles[j + 3]} {" sum: "} {np.sum(ker):.0f}')
                    fig.colorbar(kern_img, ax=ax, fraction=0.046, pad=0.04)
        else:
            ker = self.kernels[-1][0][0]
            plt.imshow(
                np.asmatrix(ker), interpolation="nearest", origin="upper", cmap="Blues"
            )
            plt.title(f'{self.titles[3]} {" sum: "}  {np.sum(ker):.0f}')
            plt.colorbar(fraction=0.046, pad=0.04)

        self.kernel_plot = fig

    def plot_decision_boundaries(self, cheap_version: bool = True):
        """Plotting and saving several decision boundaries for different training size and subsamples.

        Parameters
        ----------
        cheap_version: bool
            If true, creates only the datapoints colored according to the svms predictions.
        """
        logger.info("Creating decision boundaries")
        self.make_folder()
        subfolder = self.path / Path("Decision Boundaries")
        subfolder.mkdir(exist_ok=True)
        x_min, x_max = np.min(self.train[-1][0][0][:, 0]), np.max(
            self.train[-1][0][0][:, 0]
        )
        y_min, y_max = np.min(self.train[-1][0][0][:, 1]), np.max(
            self.train[-1][0][0][:, 1]
        )
        ndims = self.train[0][0][0].shape[1]

        for i, trs in enumerate(self.training_size):
            for k, kern_titles in enumerate(self.titles):
                contour = plt.figure(constrained_layout=True)
                contour.set_figheight(8)
                contour.set_figwidth(12)
                if self.folds <= 3:
                    cols = self.folds
                    rows = 1
                    contour.set_figheight(4)
                    contour.set_figwidth(4 * self.folds)
                    titlesize = 20
                else:
                    rows = 2
                    cols = 3
                    contour.set_figheight(8)
                    contour.set_figwidth(12)
                    titlesize = 30
                if k < 3:
                    h = 0.05
                else:
                    h = 0.05
                xx, yy = np.meshgrid(
                    np.arange(x_min, x_max, h), np.arange(y_min, y_max, h)
                )

                for fld in range(np.min([self.folds, 6])):
                    print(i, fld, k)
                    ax = contour.add_subplot(rows, cols, fld + 1)
                    clf = self.svms[i][fld][k]
                    if not cheap_version and ndims == 2:
                        if k < 3:
                            z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
                        else:
                            grid_kernel = self.quantum_kernels[k - 3].evaluate(
                                x_vec=np.c_[xx.ravel(), yy.ravel()],
                                y_vec=self.train[i][fld][0],
                            )
                            z = clf.predict(grid_kernel)
                        z = z.reshape(xx.shape)
                        ax.contourf(xx, yy, z, cmap=plt.cm.seismic, alpha=0.5)
                        ax.scatter(
                            self.train[i][fld][0][:, 0],
                            self.train[i][fld][0][:, 1],
                            c=self.train[i][fld][1],
                            cmap=plt.cm.seismic,
                            s=1,
                        )
                    else:
                        z = self.train_preds[i][fld][k]
                        ax.scatter(
                            self.train[i][fld][0][:, 0],
                            self.train[i][fld][0][:, 1],
                            c=z,
                            cmap=plt.cm.bwr,
                            s=1,
                        )

                    xmin, ymin = (
                        np.arange(x_min, x_max, 0.2).min(),
                        np.arange(y_min, y_max, 0.2).min(),
                    )
                    xmax, ymax = (
                        np.arange(x_min, x_max, 0.2).max(),
                        np.arange(y_min, y_max, 0.2).max(),
                    )
                    ax.set_xlabel("Feature 1")
                    ax.set_ylabel("Feature 2")
                    ax.set_xlim([xmin, xmax])
                    ax.set_ylim([ymin, ymax])
                    ax.set_xticks(())
                    ax.set_yticks(())
                contour.suptitle(
                    f"{kern_titles} with {trs} samples", y=1.1, fontsize=titlesize
                )
                save_object(
                    self.path / Path("Decision Boundaries"),
                    contour,
                    "Contours" + str(trs) + kern_titles + ".png",
                )
                plt.close(contour)

    def plot_bloch_spheres(
        self,
        dataset: list[np.ndarray],
        labels: list[np.ndarray],
        with_prediction: bool = False,
    ):
        """Plotting the Bloch spheres for every circuit.

        Parameters:
        -----------
        dataset: list[np.ndarray]
            The dataset containing feature distribution to encode
        labels: list[np.ndarray]
            The truth labels
        with_prediction: bool
            If True, colormap corresponds to classifier prediction. If False, to label.
        """
        self.do_kernel_alignment(dataset[1], labels[1])
        self.make_folder()

        if not hasattr(self, "train"):
            logger.info("Plotting distributions on Bloch spheres")
            save_path = self.path / Path("Bloch Speres Distributions")
            save_path.mkdir(exist_ok=True)
            train_dataset, color = get_subsample(dataset[0], labels[0], 500, 42)
            for i, qker in enumerate(self.quantum_kernels):
                plot_bloch(
                    self.x, qker, train_dataset, color, save_path, self.titles[3 + i]
                )
        elif with_prediction:
            logger.info("Plotting predictions on Bloch spheres")
            save_path = self.path / Path("Bloch Speres Predictions")
            save_path.mkdir(exist_ok=True)
            train_dataset = self.train[-1][0][0]
            if train_dataset.shape[0] > 500:
                train_dataset = train_dataset[:500]
            for i, qker in enumerate(self.quantum_kernels):
                color = self.train_preds[-1][0][i + 3]
                if color.shape[0] > 500:
                    color = color[:500]
                plot_bloch(
                    self.x, qker, train_dataset, color, save_path, self.titles[3 + i]
                )
        else:
            logger.info("Plotting distributions on Bloch spheres")
            save_path = self.path / Path("Bloch Speres Distributions")
            save_path.mkdir(exist_ok=True)
            train_dataset = self.train[-1][0][0]
            color = self.train[-1][0][1]
            if color.shape[0] > 500:
                train_dataset = train_dataset[:500]
                color = color[:500]
            for i, qker in enumerate(self.quantum_kernels):
                plot_bloch(
                    self.x, qker, train_dataset, color, save_path, self.titles[3 + i]
                )

    def train_svms_cv(self, dataset: list[np.ndarray], labels: list[np.ndarray]):
        """Training classical and quantum svms on a fixed subsample for every training size with cross-validation.

        Parameters
        ----------
        dataset: list[np.ndarray]
            The dataset containing the training subsets.
        labels: list[np.ndarray]
            The truth labels.
        """
        logger.info("Doing cross validated trainings")
        linear = {"kernel": "linear", "C": 1, "gamma": 10}
        poly = {"kernel": "poly", "C": 0.1, "degree": 3}
        rbf = {"kernel": "rbf", "C": 1, "gamma": 10}
        opts = [linear, poly, rbf]

        train_dataset, train_labels = dataset[0], labels[0]
        self.do_kernel_alignment(dataset[1], labels[1])
        fig = plt.figure(constrained_layout=True)
        fig.set_figheight(5)
        fig.set_figwidth(5)

        folds = 5
        scores = np.zeros((len(self.training_size), folds))
        for i, trs in enumerate(self.training_size):
            subset, labels = get_subsample(train_dataset, train_labels, trs, 42)
            clf = SVC(**opts[0])
            scores[i] = cross_val_score(clf, subset, labels, cv=folds)
        avg_scores = np.mean(scores, axis=1)
        std_scores = np.std(scores, axis=1) / np.sqrt(folds)
        plt.errorbar(x=self.training_size, y=avg_scores, yerr=std_scores)
        scores = np.zeros((len(self.training_size), folds))
        for i, trs in enumerate(self.training_size):
            subset, labels = get_subsample(train_dataset, train_labels, trs, 42)
            clf = SVC(**opts[1])
            scores[i] = cross_val_score(clf, subset, labels, cv=folds)
        avg_scores = np.mean(scores, axis=1)
        std_scores = np.std(scores, axis=1) / np.sqrt(folds)
        plt.errorbar(x=self.training_size, y=avg_scores, yerr=std_scores)
        scores = np.zeros((len(self.training_size), folds))
        for i, trs in enumerate(self.training_size):
            subset, labels = get_subsample(train_dataset, train_labels, trs, 42)
            clf = SVC(**opts[2])
            scores[i] = cross_val_score(clf, subset, labels, cv=folds)
        avg_scores = np.mean(scores, axis=1)
        std_scores = np.std(scores, axis=1) / np.sqrt(folds)
        plt.errorbar(x=self.training_size, y=avg_scores, yerr=std_scores)

        for q, encoding in enumerate(self.quantum_kernels):
            scores = np.zeros((len(self.training_size), folds))
            for i, trs in enumerate(self.training_size):
                subset, labels = get_subsample(train_dataset, train_labels, trs, 42)
                ker = encoding
                ker_matrix = ker.evaluate(x_vec=subset)
                clf = SVC(kernel="precomputed", C=self.cs[q])
                scores[i] = cross_val_score(clf, ker_matrix, labels, cv=folds)
            avg_scores = np.mean(scores, axis=1)
            std_scores = np.std(scores, axis=1) / np.sqrt(folds)
            plt.errorbar(x=self.training_size, y=avg_scores, yerr=std_scores)

        plt.ylim([0, 1])
        plt.title("Cross validated learning curve")
        plt.xlabel("Sample size")
        plt.ylabel("Accuracy")
        plt.legend(self.titles)

        self.learning_curve_cv = fig

    def plot_featuremaps(self):
        """Plotting the quantum featuremaps in the circuit representation."""
        logger.info("Drawing the featuremaps")
        self.featuremaps_plot = []
        large_font = {
            "fontsize": 10,
            "subfontsize": 8,
        }
        for i, fm in enumerate(self.quantum_featuremaps):
            fig = plt.figure(constrained_layout=True)
            fig.set_figheight(5)
            fig.set_figwidth(15)
            fig = fm.draw(
                output="mpl",
                plot_barriers=False,
                initial_state=True,
                style=large_font,
                fold=20,
            )
            plt.title(f"{self.titles[3+i]} featuremap", y=0.9, fontsize=15)
            self.featuremaps_plot.append(fig)

    def do_kernel_alignment(self, dataset: list[np.ndarray], labels: list[np.ndarray]):
        """Checking if the input kernels need alignment. If so, perform kernel alignment.

        Parameters
        ----------
        dataset: list[np.ndarray]
            Alignment dataset.
        labels: list[np.ndarray]
            The truth labels.
        """
        if self.alignment:
            kernels = self.quantum_kernels
            for i, kers in enumerate(kernels):
                if kers.user_parameters:
                    logger.info(f"Doing kernel alignment of {self.titles[3+i]}  kernel")
                    self.quantum_kernels[i], self.opt_data = align_kernel(
                        kers, dataset, labels, self.cs[i]
                    )
            self.alignment = False

    def compare_backend(
        self,
        dataset: list[np.ndarray],
        labels: list[np.ndarray],
        new_instance: Union[Aer.get_backend, QuantumInstance],
    ):
        """Training the models with an alternative backend.

        Parameters
        ----------
        dataset: list[np.ndarray]
            The dataset containing the training subsets.
        labels: list[np.ndarray]
            The truth labels.
        new_instance: Union[Aer.get_backend, QuantumInstance])
            The new backend for comparison.
        """
        train_dataset, train_labels = dataset[0], labels[0]
        self.do_kernel_alignment(dataset[1], labels[1])

        new_kernels = make_kernels(self.quantum_featuremaps, new_instance)

        folds = 5  # *np.ones_like(self.training_size) #np.rint(np.sqrt(self.training_size)/2).astype(np.int32)
        scores_1, mean_1, std_1 = self.cv_scores(
            train_dataset, train_labels, folds, self.quantum_kernels
        )
        scores_2, mean_2, std_2 = self.cv_scores(
            train_dataset, train_labels, folds, new_kernels
        )
        self.backend_compare_scores = [[mean_1, std_1], [mean_2, std_2]]
        self.backend_compare_scores_all = [scores_1, scores_2]

        self.backend_plot = []

        for k in range(len(self.quantum_kernels)):
            fig = plt.figure(constrained_layout=True)
            fig.set_figheight(5)
            fig.set_figwidth(5)
            plt.errorbar(x=self.training_size, y=mean_1[:, k], yerr=std_1[:, k])
            plt.errorbar(x=self.training_size, y=mean_2[:, k], yerr=std_2[:, k])
            plt.ylim([0, 1])
            plt.xlabel("Sample size")
            plt.ylabel("Accuracy")
            plt.legend([type(self.backend).__name__, type(new_instance).__name__])
            self.backend_plot.append(fig)

    def cv_scores(
        self,
        train_dataset: np.ndarray,
        train_labels: np.ndarray,
        folds: int,
        kernels: list[QuantumCircuit],
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Evaluating quantum classifier scores with cross-validation.

        Parameters
        ----------
        train_dataset: np.ndarray
            The training featurespace.
        train_labels: np.ndarray
            The training truth values.
        folds: int
            Number of folds for running the cross-validation.
        kernels: list[QuantumCircuit]
            The quantum kernels.

        Returns:
        --------
        score: np.ndarray
            Classifier scores for different training subsets and fold.
        mean: np.ndarray
            The mean of the cross-validation reults scores.
        std: np.ndarray
            The mean standard deviation of the cross-validation scores.
        """
        mean = np.zeros((len(self.training_size), len(kernels)))
        std = np.zeros((len(self.training_size), len(kernels)))
        score = np.zeros((len(self.training_size), len(kernels), folds))
        for q, encoding in enumerate(kernels):
            for i, trs in enumerate(self.training_size):
                subset, labels = get_subsample(train_dataset, train_labels, trs, 2)
                ker = encoding
                ker_matrix = ker.evaluate(x_vec=subset)
                clf = SVC(kernel="precomputed", C=self.cs[q])
                score[i, q] = cross_val_score(clf, ker_matrix, labels, cv=folds)
                save_object(self.path, score, "score_TEMP.pkl")
        mean, std = np.mean(score, axis=2), np.std(score, axis=2) / np.sqrt(folds)
        return score, mean, std
