""" Imports to Python functions """
import math
import numpy as np

from controlled_gate import mc_gate

from qiskit import QuantumCircuit
from qiskit.circuit.library import MCXGate, QFT


def to_binary(number:int, nbits:int=None):
    
    '''
    This function transforms an integer to its binary form (string).
    If a determined number of bits is required (more than the needed ones),
    it can be passed as a parameter too, nbits, None by default.
    It is needed that the number of bits passed as a parameter is larger
    than the number of bits needed to write the number in binary. 

    Input:
        - number (integer): Number to transform.
        - nbits (integer) None by default: Number of bits.

    Output:
        - binary (string): containing the number in its binary form.
        It writes 0s in front if nbits is larger than the number of bits needed
        to write the binary form.
    '''

    if nbits is None:
        return bin(number)[2:]
    else:
        binary = bin(number)[2:]
        if nbits < len(binary):
            print('Error, nbits must be larger than %d.'%(len(binary)))
        else:
            return '0' * (nbits - len(binary)) + binary

def multi_control_z(nqubits:int):
    '''
    Function to create a multi-controlled Z gate.

    Input:
        - nqubits (Integer): number of qubits in the gate (controls and target)
        This means that the gate has nqubits-1 controls and 1 target.

    Output:
        - circuit: QuantumCircuit containing a multi-controlled Z gate.
        It has to be transformed with method .to_gate() to append to a QuantumCircuit larger.

    Example:

    main_circuit = QuantumCircuit(nqubits)

    gate_multi_z = multi_control_z(nqubits)

    main_circuit.append(gate_multi_z.to_gate(), range(nqubits))
    '''
    circuit=QuantumCircuit(nqubits,name=' CZ (%d)' %(nqubits))
    mc_gate(np.array([[1, 0], [0, -1]]), circuit=circuit, controls=list(range(nqubits-1)), targ=nqubits-1)
    return circuit


def multi_control_z_old(nqubits):
    '''
    Function to create a multi-controlled Z gate.

    Input:
        - nqubits (Integer): number of qubits in the gate (controls and target)
        This means that the gate has nqubits-1 controls and 1 target.

    Output:
        - circuit: QuantumCircuit containing a multi-controlled Z gate.
        It has to be transformed with method .to_gate() to append to a QuantumCircuit larger.

    Example:

    main_circuit = QuantumCircuit(nqubits)

    gate_multi_z = multi_control_z(nqubits)

    main_circuit.append(gate_multi_z.to_gate(), range(nqubits))
    '''
    circuit=QuantumCircuit(nqubits,name=' CZ (%d)' %(nqubits))
    circuit.h(nqubits-1)
    gate = MCXGate(nqubits-1)
    circuit.append(gate, range(nqubits))
    circuit.h(nqubits-1)
    return circuit



def phiADD(circuit:QuantumCircuit, target_reg:list, num_sum:int, inv:bool=False):
    '''
    This function performs the quantum addition using Drapper addition.

    This addition is realized using direct QFT before and inverse QFT after.
    IMPORTANT: These QFTs do need to NOT apply swap gates.

    Input:
        - circuit (QuantumCircuit): In which to perform the addition.

        - target_reg (list): Quantum Register with the list of qubits where
            the addition is performed.

        - num_sum (int): Value to be added.

        - inv (bool): If value is False, performs an addition. If True,
            performs the opposite, a substraction.

    '''

    nqubits = len(target_reg)

    angles = ((-1)**inv) * getAngles(num_sum, nqubits)

    for i in range(nqubits):
        circuit.p(angles[i], target_reg[i])



def phaseAddition(target_reg:list, num_sum:int, inv:bool=False, approx_QFT:int=0, name:str=None):
    '''
    This function constructs the whole addition pipeline.

    Input:
        - target_reg (list): Quantum Register with the list of qubits where
            the addition is performed.

        - num_sum (int): Value to be added.

        - inv (bool): If value is False, performs an addition. If True,
            performs the opposite, a substraction.

        - approx_QFT (int): Approximation degree of the QFT.

    '''

    nqubits = len(target_reg)

    # Construction of the circuit
    if name:# If name is provided give such name to the circuit
        circuit = QuantumCircuit(nqubits, name=name)
    else: # Otherwise, the name is just " < number"
        circuit = QuantumCircuit(nqubits, name = ' + %d '%num_sum)

    #  Direct QFT
    circuit.append(QFT(num_qubits=nqubits, do_swaps=False, approximation_degree=approx_QFT), target_reg)
    
    # Addition using phase
    phiADD(circuit=circuit, target_reg=target_reg, num_sum=num_sum, inv=inv)
    
    # Inverse QFT
    circuit.append(QFT(num_qubits=nqubits, do_swaps=False, inverse=True, approximation_degree=approx_QFT), target_reg)

    return circuit



def getAngles(num_sum:int, nqubits:int):
    '''
    Calculates the angles corresponding to sum the value "num_sum" via phase.

    Input:

        - num_sum (integer): Number to be added

        - nqubits (integer): Number of qubits

    Output:
        - angles (list): List of angles (in order of qubits)

    '''

    s = to_binary(num_sum, nqubits)

    angles = [sum([math.pow(2, i-j) for j in range(i, nqubits) if s[j]=='1'])*np.pi
              for i in range(nqubits-1, -1, -1)]

    return angles



def oracle_less_than(number:int, nqubits:int, name:str=None):

    '''
    This function builds a quantum circuit, an oracle, which marks with a pi-phase
    those states which represent numbers strictly smaler than the number given by parameter.

    The procedure is almost the same for all numbers, with the only exception of a difference
    if the first bit of the number in binary is 1 or 0.

    Input:
        - number (integer): containing the objective number,
            or a string (str) with the binary representation of such number.

        - nqubits (integer): number of qubits of the circuit.
            It must be larger than the number of digits of the binary representation of number.
            name (string): default None, name of the circuit.

    Output:
        circuit (QuantumCircuit): which marks with fase pi the states which
        represent in binary the numbers strictly smaller than number.
    '''

    # Construction of the circuit
    if name:# If name is provided give such name to the circuit
        circuit = QuantumCircuit(nqubits, name=name)
    else: # Otherwise, the name is just " < number"
        circuit = QuantumCircuit(nqubits, name = ' < %d '%number)

    # Binary representation of the number
    num_binary = to_binary(number, nqubits)
    
    # Discard the 0s at the end, as they will not be used and save
    # unnecessary X gates
    num_binary = num_binary.rstrip('0')

    
    if num_binary[0] == '1':
        # If the first digit is 1
        # Mark all the states of the form |0q1...>
        circuit.x(nqubits-1)
        circuit.z(nqubits-1)
        circuit.x(nqubits-1)
    else:
        # If first digit is 0
        # Apply X gate to first qubit
        circuit.x(nqubits-1)
    
    # For loop on the remaining digits
    for position1, value in enumerate(num_binary[1:]):
        # Rename the position as it starts with 0 in the second bit and
        # we want it to be 1.
        position = position1 + 1

        if value == '0':
            # If the digit is 0
            # Just apply a X gate
            circuit.x(nqubits-position-1)
        else:
            # If the digit is 1
            # Apply a multi-controlled Z gate to mark states of the shape:
            # |bn...bi+1 0 qi-1...q1>
            # where bn,...,bi+1 are the first n-i bits of m, which is of the shape bn...bi+1 1 bi-1...b1
            # because we just checked that bi is 1.
            # Hence, the numbers of the form bn...bi+1 0 qi-1...q1 are smaller than m.
            circuit.x(nqubits-position-1)
            multi_z = multi_control_z(position + 1)
            circuit.append(multi_z.to_gate(), range(nqubits-1, nqubits-position-2, -1))
            circuit.x(nqubits-position-1)
    
    for position, value in enumerate(num_binary):
        # Apply X gates to qubits in position of bits with a 0 value
        if value == '0':
            circuit.x(nqubits-position-1)
        else:
            pass
    
    return circuit



def oracle_interval_A(target_reg:list, low_boundary:int, upper_boundary:int, name:str=None):

    '''
    This function adds a quantum circuit, an oracle, which marks with a pi-phase
    those states which represent numbers in the interval given by [low_boundary, upper_boundary].

    The procedure is almost the same for all numbers, with the only exception of a difference
    if the first bit of the number in binary is 1 or 0.

    Input:
        - circuit: 
        - number (integer): containing the objective number,
            or a string (str) with the binary representation of such number.

        - nqubits (integer): number of qubits of the circuit.
            It must be larger than the number of digits of the binary representation of number.
            name (string): default None, name of the circuit.

    Output:
        circuit (QuantumCircuit): which marks with fase pi the states which
        represent in binary the numbers strictly smaller than number.
    '''

    nqubits = len(target_reg)

    # Construction of the circuit
    if name:# If name is provided give such name to the circuit
        circuit = QuantumCircuit(target_reg, name=name)
    else: # Otherwise, the name is just " < number"
        circuit = QuantumCircuit(target_reg, name = ' [%d, %d] '%(low_boundary, upper_boundary))

    circuit.append(oracle_less_than(number=upper_boundary+1, nqubits=nqubits), target_reg)

    circuit.append(oracle_less_than(number=low_boundary, nqubits=nqubits), target_reg)

    return circuit



def oracle_interval_B(target_reg:list, low_boundary:int, upper_boundary:int, approx_QFT:int=0, name:str=None):

    '''
    This function adds a quantum circuit, an oracle, which marks with a pi-phase
    those states which represent numbers in the interval given by [low_boundary, upper_boundary].

    The procedure is almost the same for all numbers, with the only exception of a difference
    if the first bit of the number in binary is 1 or 0.

    Input:
        - circuit: 
        - number (integer): containing the objective number,
            or a string (str) with the binary representation of such number.

        - nqubits (integer): number of qubits of the circuit.
            It must be larger than the number of digits of the binary representation of number.
            name (string): default None, name of the circuit.

    Output:
        circuit (QuantumCircuit): which marks with fase pi the states which
        represent in binary the numbers strictly smaller than number.
    '''

    nqubits = len(target_reg)

    # Construction of the circuit
    if name:# If name is provided give such name to the circuit
        circuit = QuantumCircuit(target_reg, name=name)
    else: # Otherwise, the name is just " < number"
        circuit = QuantumCircuit(target_reg, name = ' [%d, %d] '%(low_boundary, upper_boundary))

    circuit.append(oracle_less_than(number=upper_boundary-low_boundary+1, nqubits=nqubits), target_reg)

    circuit.append(phaseAddition(target_reg=target_reg, num_sum=low_boundary, approx_QFT=approx_QFT), target_reg)

    return circuit



