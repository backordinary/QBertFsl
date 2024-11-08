# https://github.com/yaleqc/qtcodes/blob/85f1fed792017892dc3367d157d695b8ba3572ef/qtcodes/circuits/xxzz.py
"""
XXZZ Surface Code Encoder Classes
"""
from typing import Tuple, Optional
from qiskit import ClassicalRegister
from qiskit.circuit import Qubit

from qtcodes.circuits.base import (
    _Stabilizer,
    LatticeError,
)
from qtcodes.circuits.rotated_surface import _RotatedLattice, RotatedQubit


TQubit = Tuple[float, float, float]


class _XXXX(_Stabilizer):
    """
    X-syndrome plaquette of the rotated CSS (XXXX/ZZZZ) surface code.
    """

    def entangle(self) -> None:
        """
        Traverse in reverse "Z" pattern
        """
        syndrome = self.qubit_indices[0]
        top_l = self.qubit_indices[1]
        top_r = self.qubit_indices[2]
        bot_l = self.qubit_indices[3]
        bot_r = self.qubit_indices[4]

        if (top_r and not top_l) or (bot_r and not bot_l):
            raise LatticeError("Inconsistent X syndrome connections")

        self.circ.h(syndrome)
        if top_r:
            self.circ.cx(syndrome, top_r)
            self.circ.cx(syndrome, top_l)
        if bot_r:
            self.circ.cx(syndrome, bot_r)
            self.circ.cx(syndrome, bot_l)
        self.circ.h(syndrome)


class _ZZZZ(_Stabilizer):
    """
    Z-syndrome plaquette of the rotated CSS (XXXX/ZZZZ) surface code.
    """

    def entangle(self) -> None:
        """
        Traverse in reverse "N" pattern
        """
        syndrome = self.qubit_indices[0]
        top_l = self.qubit_indices[1]
        top_r = self.qubit_indices[2]
        bot_l = self.qubit_indices[3]
        bot_r = self.qubit_indices[4]

        if (top_r and not bot_r) or (top_l and not bot_l):
            raise LatticeError("Inconsistent Z syndrome connections")

        if top_r:
            self.circ.cx(top_r, syndrome)
            self.circ.cx(bot_r, syndrome)
        if top_l:
            self.circ.cx(top_l, syndrome)
            self.circ.cx(bot_l, syndrome)


class _XXZZLattice(_RotatedLattice):
    """
    This class contains all the lattice geometry
    specifications regarding the XXZZ (CSS) Rotated Surface Code.
    """

    stabilizer_shortnames = {"mx": _XXXX, "mz": _ZZZZ}

    def reset_x(self) -> None:
        self.circ.reset(self.qregisters["data"])
        self.circ.h(self.qregisters["data"])
        self.circ.barrier()

    def reset_z(self) -> None:
        self.circ.reset(self.qregisters["data"])
        self.circ.barrier()

    def x(self) -> None:
        for i in range(0, self.params["num_data"], self.params["d"][self.W]):
            self.circ.x(self.qregisters["data"][i])
        self.circ.barrier()

    def z(self) -> None:
        for i in range(self.params["d"][self.W]):
            self.circ.z(self.qregisters["data"][i])
        self.circ.barrier()

    def x_c_if(self, classical: ClassicalRegister, val: int) -> None:
        """
        Classically conditioned logical X operator on the topological qubit.
        Defined as the left-most column.
        """
        for i in range(0, self.params["num_data"], self.params["d"][self.W]):
            self.circ.x(self.qregisters["data"][i]).c_if(classical, val)
        self.circ.barrier()

    def z_c_if(self, classical: ClassicalRegister, val: int) -> None:
        """
        Classically conditioned logical Z operator on the topological qubit.
        Defined as the top-most row.
        """

        for i in range(self.params["d"][self.W]):
            self.circ.z(self.qregisters["data"][i]).c_if(classical, val)
        self.circ.barrier()

    def cx(self, control: Optional[Qubit] = None, target: Optional[Qubit] = None):
        """
        Logical CX Gate

        Args:
            control (Optional[Qubit]): If provided, then this gate will implement
                a logical x gate on this tqubit conditioned on source

            target (Optional[Qubit]): If provided, then this gate will implement
                a logical x gate on target conditioned on this tqubit
        """
        if control:
            # Taking left-most column
            for i in range(0, self.params["num_data"], self.params["d"][self.W]):
                self.circ.cx(control, self.qregisters["data"][i])
            self.circ.barrier()
        elif target:
            self._readout_z_into_ancilla()
            # TODO: we may not want to read into the ancilla,
            # let's try to eliminate this intermediate method,
            self.circ.cx(self.qregisters["ancilla"], target)

    def _readout_x_into_ancilla(self) -> None:
        """
        Convenience method to read-out the
        logical-X projection into an ancilla qubit.
        Uses the left-most column.
        """
        self.circ.reset(self.qregisters["ancilla"])
        self.circ.h(self.qregisters["ancilla"])
        for i in range(0, self.params["num_data"], self.params["d"][self.W]):
            self.circ.cx(self.qregisters["ancilla"], self.qregisters["data"][i])
        self.circ.h(self.qregisters["ancilla"])

    def readout_x(self, readout_creg: Optional[ClassicalRegister] = None) -> None:
        if not readout_creg:
            self.params["num_readout"] += 1
            creg_name = self.name + "_readout_" + str(self.params["num_readout"])
            readout = ClassicalRegister(1, name=creg_name)

            self.circ.add_register(readout)

            self.cregisters[creg_name] = readout
            readout_creg = self.cregisters[creg_name]

        self._readout_x_into_ancilla()
        self.circ.measure(self.qregisters["ancilla"], readout_creg)
        self.circ.barrier()

    def _readout_z_into_ancilla(self) -> None:
        """
        Convenience method to read-out the
        logical-Z projection into an ancilla qubit.
        Uses the top-most row.
        """
        self.circ.reset(self.qregisters["ancilla"])
        for i in range(self.params["d"][self.W]):
            self.circ.cx(self.qregisters["data"][i], self.qregisters["ancilla"])

    def readout_z(self, readout_creg: Optional[ClassicalRegister] = None) -> None:
        if not readout_creg:
            self.params["num_readout"] += 1
            creg_name = self.name + "_readout_" + str(self.params["num_readout"])
            readout = ClassicalRegister(1, name=creg_name)

            self.circ.add_register(readout)

            self.cregisters[creg_name] = readout
            readout_creg = self.cregisters[creg_name]
        self._readout_z_into_ancilla()
        self.circ.measure(self.qregisters["ancilla"], readout_creg)
        self.circ.barrier()

    def lattice_readout_x(self) -> None:
        self.params["num_lattice_readout"] += 1
        creg_name = (
            self.name + "_lattice_readout_" + str(self.params["num_lattice_readout"])
        )
        readout = ClassicalRegister(self.params["num_data"], name=creg_name,)

        self.circ.add_register(readout)
        self.cregisters[creg_name] = readout

        # H|+> = |0>, H|-> = |1>
        self.circ.h(self.qregisters["data"])
        self.circ.measure(self.qregisters["data"], self.cregisters[creg_name])
        self.circ.barrier()

    def lattice_readout_z(self) -> None:
        self.params["num_lattice_readout"] += 1
        creg_name = (
            self.name + "_lattice_readout_" + str(self.params["num_lattice_readout"])
        )
        readout = ClassicalRegister(self.params["num_data"], name=creg_name,)

        self.circ.add_register(readout)

        self.cregisters[creg_name] = readout

        self.circ.measure(self.qregisters["data"], self.cregisters[creg_name])
        self.circ.barrier()


class XXZZQubit(RotatedQubit):
    """
    A single, logical XXZZ surface code qubit.
    """

    lattice_type = _XXZZLattice
