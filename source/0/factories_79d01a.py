# https://github.com/jaybuie1969/QuantumRandomNumberGenerator/blob/683e8b5fbb2378b867f22d0c13ea4c0550dd3b3c/com/buie/quantum/factories.py
"""
com.buie.quantum.factories
This module holds the class definitions for "factory" objects that either create and return items produced using a quantum processor
"""

import numpy
import qiskit

class RandomBitStringFactory():
    """
    This class is designed to generate strings of random ones and zeros generated by measuring the collapse of superposition quantum states in an
    IBM quantum processor
    One quantum state is collapsed for each bit used in the bit string
    By default, this factory produces strings of up to 8 kilobytes, or 8,192 one or zero characters; and all bits are weighted with an equal 50/50
    chance of producing either a zero or a one
    This factory can be used as a superclass for other random-related factories
    """

    # Initialize a default object parameters
    apiToken = ""
    numberOfBits = 4
    bitWeights = None
    quantumCircuits = None
    qubitsPerCircuit = 5
    maximumBits = 8192

    def __init__(self, **kwargs) -> None:
        """
        When instantiatated, this object initialization method looks for three named parameters:
        * bits - A positive integer setting the bit size of the integers to be generated by this Factory instance
        * weights - A dictionary containing a desired set of probability weightings for individual bits; by default, each bit has a 50/50 chance of being a zero or a one; bit weight values are floating-point number ranging from 0 to 100
        * apiToken - A string containing the API access/authentication token for submiting a job to an IBM quantum processor; a missing or empty API token will cause any quantum interaction to be simulated

        :param kwargs: A dictionary of named parameters passed into this class upon initialization, the three expected keys are "apiToken", "numberOfBits" and "bitWeights"
        :type kwargs: dict, defaults to an empty dictionary
        """

        self.bitWeights = {}
        self.quantumCircuits = []

        # Look for a non-empty incoming API token
        self.apiToken = kwargs["apiToken"].strip() if (("apiToken" in kwargs) and (type(kwargs["apiToken"]) == str)) else ""

        # Look for a valid number of bits
        if (("bits" in kwargs) and (kwargs["bits"] != None)):
            # The "bits" named parameter is present and is not None, see if it is a positive integer

            try:
                bits = int(kwargs["bits"])
                if ((bits >= 1) and (bits <= self.maximumBits)):
                    # The "bits" named parameter is a valid value (between 1 and self.maximumBits), retain it
                    self.numberOfBits = bits

            except:
                # The "bits" named parameter could not be converted to an integer, do nothing and keep the default numberOfBits value
                pass

        # Look for a valid dictionary of bit weightings
        if (("weights" in kwargs) and (type(kwargs["weights"]) == dict)):
            # A presumed dictionary of bit weightings was found, iterate over it and retain the valid ones

            for position, weight in kwargs["weights"].items():
                if (
                    (type(position) == int)
                    and (position >= 0) and (position < self.numberOfBits)
                    and (type(weight) in [int, float])
                    and (weight >= 0) and (weight <= 100)
                ):
                    # This key is a valid integer value and this weight is a valid integer/floating-point value, retain them as a bit weighting
                    self.bitWeights[position] = weight

        # Now that all expected kwargs have been handled, build the set of quantum circuit to be used
        self.buildQuantumCircuits()

    def setBits(bits:int=0) -> None:
        """
        This method re-sets the bit size of the integers being generated by this factory object

        :param bits: A positive integer between 1 and 32 that designates the desired bit size for this factory
        :type bits: int, defaults to 0
        """

        if ((bits >= 1) and (bits <= 32)):
            # bits is a valid value, re-set the integer bit size for this factory, and re-build the set of quantum circuits used

            self.numberOfBits = bits
            self.buildQuantumCircuits()

    def clearWeights(self) -> None:
        """
        Calling this method clears all of the bit weightings for this factory, and then re-builds the set of quantum circuits used
        """

        self.bitWeights = {}
        self.buildQuantumCircuits()

    def setWeights(self, weights:dict={}, keepOriginal:bool=True) -> None:
        """
        This method adds a set of bit weightings to this factory; any non-default weighting that already exists for a bit will be overwritted by this method
        Optionally, any pre-existing weightings will be removed before the new weights are added

        :param weights: A dictionary of new bit weights to be added to this factory object
        :type weights: dict, defaults to an empty ditionary
        :param keepOriginal: A Boolean flag indicating whether or not to keep any existing bit weightings; by default weightings are kept
        :type keepOriginal: bool, default to True
        """

        if (not keepOriginal):
            # The original weightings are flagged to be cleared, clear them before doing anything else
            self.bitWeights = {}

        for position, weight in weights.items():
            if (
                (type(position) == int)
                and (position >= 0) and (position < self.numberOfBits)
                and (type(weight) in [int, float])
                and (weight >= 0) and (weight <= 100)
            ):
                 # This key is a valid integer value and this weight is a valid integer/floating-point value, retain them as a bit weighting
                 self.bitWeights[position] = weight

        # Now re-build the set of quantum circuits used
        self.buildQuantumCircuits()

    def buildQuantumCircuits(self) -> None:
        """
        This method clears and attempts to (re-)build the set of quantum circuits used to generate random integers by this factory
        Each integer is the result of a single collapsing qubit's quantum state and there are only five qubits per processor
        More than five bits means that a set of experiments will have to be set up, each with five bits, and the results concatenated together
        """

        # Initialize self.quantumCircuits to an empty list and iterater over self.numberOfBits, five at a time
        self.quantumCircuts = []
        for i in range(0, self.numberOfBits, self.qubitsPerCircuit):
            # This top-level iteration represents the set of quantum circuits needed to generate this random number
            # Each time through this loop, a new quantum circuit object will be created and added to self.quantumCircuits

            # Compute the number of qubits needed in this quantum circuit, then initialize the apprporiate-sized registers
            # If this is the last(only) circuit required, the number of qubits could be few as one
            # If the factory is generating integers larger than five bits, all circuits except the last one will all have five qubits
            numberOfQubits = min([(self.numberOfBits - i), self.qubitsPerCircuit])
            quantumRegister = qiskit.QuantumRegister(numberOfQubits)
            classicalRegister = qiskit.ClassicalRegister(numberOfQubits)

            # Initialize the circuit and apply a Hadamard gate to each qubit in the quantum register
            quantumCircuit = qiskit.QuantumCircuit(quantumRegister, classicalRegister)
            quantumCircuit.h(quantumRegister)

            # Itearate over the number of qubits in this circuit and set up a series of H-U1-H gates to each
            for j in range(numberOfQubits):

                # Set the bit number (index) and then use a U1 gate to rotatethe qubit the desired amount
                # If this bit does not have any weighting, the default quibit rotation is half (50%) of PI
                # If the bit is weighted, the qubit rotation is the weight's value is a number between 0 - 100 and is treated as a percentage of PI
                index = i + j
                quantumCircuit.u1(((self.bitWeights[index] if (index in self.bitWeights) else 50) * numpy.pi) / 100, quantumRegister[j])

            # Finish up the quantum circuit with a Hadamard gate to each qubit in the quantum register, and then measure each qubit to collapse
            # its superposition into either a zero or a one
            quantumCircuit.h(quantumRegister)
            quantumCircuit.measure(quantumRegister, classicalRegister)

            # Add the newly-created quatum circuit to self.quatumCircuits
            self.quantumCircuits.append(quantumCircuit)

    def get(self) -> str:
        """
        This is the Money Method - this is the method that submits the quantum circuit to IBM for processing and produces the final integer
        """

        # Initialize the bit string being returned as an empty string and the quantum job result to None
        returnString = ""
        result = None

        if (self.apiToken == ""):

            # No API Token was included with this object, run it as a simulator
            job = qiskit.execute(self.quantumCircuits, backend=qiskit.Aer.get_backend("qasm_simulator"), shots=1)
            result = job.result()

        else:
            # An API Token was included with this object, submit the circuit set to a live IBM quantum processor

            # Use the API Token to connect to IBM and get the set of back end quantum processors available from IBM
            qiskit.IBMQ.enable_account(self.apiToken)
            backends = qiskit.IBMQ.backends()

            iTo = len(backends)
            if (iTo > 0):
                # At least one quantum processor is available, start with the first one, and submit the job to it; iterate through the list of available
                # processors until one is able to accept the job

                i = 0
                while ((i < iTo) and (result == None)):
                    # This loop is not yet at the end of the list, and no result has yet been retrieved from a quantum processor, attempt to submit the circuit to 
                    # the processor at the current position in the list

                    if (str(backends[i]).lower().find("simulator") == -1):
                        # This processor is a real one and not a simulator, attempt to submit the quantum circuit to it

                        try:
                            # The job submission is enclosed within a try/except block so that it will not throw an error if the job could not be submitted or retrieved
                            job = qiskit.execute(self.quantumCircuits, backend=backends[i], shots=1)
                            result = job.result()
                        except:
                            # The job submission or retrieval threw an error, swallow it and simply move to the next back-end processor in the list
                            pass

                    # Incremenent the back-end list counter before attemptint to iterate through this loop again
                    i = i + 1

        if (result != None):
            # The quantum circuit set was run successfully, display the results and let the player know whether or not they won

            # Get the first (should be the only) key from the dictionary object of counts that were returned from the test run
            # Pre-pend that key to bitString as this quantum circuit's contribution to the random integer
            for i, quantumCircuit in enumerate(self.quantumCircuits):
                returnString = list(result.get_counts(quantumCircuit).keys())[0] + returnString

        return returnString

    def __str__(self) -> str:
        """
        I just wanted to have some fun with the stringified version of this object
        """
        return 'This is a {0} object with {1} bit{2} that have weights of {3}, dude!  Oh, and it {4} an API token'.format(self.__class__.__name__, self.numberOfBits, "s" if (self.numberOfBits > 1) else "", self.bitWeights, "has" if (self.apiToken != "") else "doesn't have")


class RandomByteStreamFactory(RandomBitStringFactory):
    """
    This class is designed to generate random byte streams generated by measuring the collapse of superposition quantum states in an IBM quantum processor
    One quantum state is collapsed for each bit used in the byte stream
    By default, this factory produces strings of up to 1 kilobyte, or 8,192 individual bits (8192/8 = 1024 bytes = 1 kilobyte); and all bits are weighted
    with an equal 50/50 chance of producing either a zero or a one
    This factory uses the RandomBitStringFactory class as its superclass
    """

    def get(self) -> bytes:
        """
        This is the Money Method - this is the method that submits the quantum circuit to IBM for processing and produces the final byte stream
        """

        # Use the superclass get() method to get the bit string that gets converted to a byte stream
        randomBitString = super().get()
        integerList = None

        if (randomBitString != None):
            # A random bit string was retrieved, convert it to a stream of bytes

            # Add enought zeros to the left side of randomBitString to make sure that its length is evenly divisible by 8 (each byte is eight bits)
            randomBitString = "{}{}".format(("0" * ((8 - (len(randomBitString) % 8)) % 8)), randomBitString)

            # Iterate over each eight-bit grouping in randomBitString, convert each eight-bit chunk into an integer and add it to integerList
            integerList = []
            iTo = len(randomBitString)
            for i in range(0, iTo, 8):
                integerList.append(int(randomBitString[i:(i + 8)], 2))

        return bytes(integerList) if (integerList != None) else None


class RandomIntegerFactory(RandomBitStringFactory):
    """
    This class is designed to generate random integers generated by measuring the collapse of superposition quantum states in an IBM quantum processor
    One quantum state is collapsed for each bit used in the integer
    By default, this factory produces unsigned integers of up to 32 bits (0 - 4,294,967,296); and all bits are weighted with an equal 50/50 chance of
    producing either a zero or a one
    This factory uses the RandomBitStringFactory class as its superclass
    """

    maximumBits = 32

    def get(self) -> int:
        """
        This is the Money Method - this is the method that submits the quantum circuit to IBM for processing and produces the final integer
        """

        # Use the superclass get() method to get the bit string that gets converted to an integer
        randomBitString = super().get()

        return int(randomBitString, 2) if (randomBitString != None) else None


class RandomFloatFactory(RandomIntegerFactory):
    """
    This class is designed to generate random floating-point numbers generated by measuring the collapse of superposition quantum states in an IBM quantum processor
    One quantum state is collapsed for each bit used to create the random integer used as the numerator of the floating-point number being returned
    The denominator used to produce the floating-point number being returned is (2 ** number of bits used by factory)
    By default, this factory produces a floating point number in the range from zero (inclusive) to one (exclusive) i.e. [0, 1) with a granularity of
    1 / (2 ** 32), or (1 / 4,294,967,296); and all bits are weighted with an equal 50/50 chance of producing either a zero or a one
    This factory uses the RandomIntegerFactory class as its superclass
    """

    def get(self) -> float:
        """
        This is the Money Method - this is the method that submits the quantum circuit to IBM for processing and produces the final floating-point number
        """

        # Use the superclass get() method to get the integer that gets converted into a float
        randomInteger = super().get()

        return float(randomInteger / (2 ** self.numberOfBits)) if (randomInteger != None) else None


class RandomReciprocalFactory(RandomIntegerFactory):
    """
    This class is designed to generate random floating-point numbers generated by measuring the collapse of superposition quantum states in an IBM quantum processor
    One quantum state is collapsed for each bit used to create the random integer used as the base for thedenominator of the floating-point number being returned
    By default, this factory produces a floating point number in the range from zero (exclusive) to one (inclusive) i.e. (0, 1] with a denominator range
    of one to 2**32, i.e. [1, 4,294,967,296]; and all bits are weighted with an equal 50/50 chance of producing either a zero or a one
    This factory uses the RandomIntegerFactory class as its superclass
    """

    def get(self) -> float:
        """
        This is the Money Method - this is the method that submits the quantum circuit to IBM for processing and produces the final floating-point number
        """

        # Use the superclass get() method to get the integer that gets converted into a float
        randomInteger = super().get()

        return float(1 / (randomInteger + 1)) if (randomInteger != None) else None
