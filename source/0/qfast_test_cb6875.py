# https://github.com/Serock3/Master_thesis_QEC_simulation/blob/bfc808d5e73b7e0bc77f7a36bdc373f7d27a4c8f/trash/qfast_test.py
# Test of the QFAST software. It does not seem to speed up our encoding, but maybe with better settings.
# Needs to be moved out of trash to be run.
#%%
from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister, ClassicalRegister, Aer, execute
from simulator_program.stabilizers import*
from simulator_program.custom_transpiler import *
from simulator_program.custom_transpiler import WACQT_device_properties
from simulator_program.idle_noise import get_circuit_time
from qfast import synthesize
# %% Def encoding circ and its unitary
registers = StabilizerRegisters()
circ = encode_input_v2(registers)
# circ.save_unitary()
utry = execute(circ,Aer.get_backend('unitary_simulator')).result().get_unitary(circ)


# %% Reduced coupling list
couplinglist = [[0, 1], [0, 4], [1, 4], [2, 3],
                [2, 4], [3, 4]]
reverse_couplinglist = [[y, x] for [x, y] in couplinglist]

# %% Synthesie the OPENQasm code 
synthesize(utry, basis_gates=WACQT_device_properties['basis_gates'], coupling_graph=[(a,b) for (a,b) in couplinglist+reverse_couplinglist])
# %% I put it into IBM quantum experience and got back qiskit code
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from numpy import pi

qreg_q = QuantumRegister(5, 'q')

circuit = QuantumCircuit(qreg_q)

circuit.u3(1.570796342543612, 2.069160345952213, 3.1415926431461325, qreg_q[0])
circuit.u3(1.5707963347862661, 2.2588688083827044, 3.5774956618816898, qreg_q[4])
circuit.cz(qreg_q[0], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[0])
circuit.rz(6.2831853066743495, qreg_q[0])
circuit.rx(1.5707963267948966, qreg_q[0])
circuit.rz(5.150597871704571, qreg_q[0])
circuit.u3(4.712388990988463, 3.5395265574493586, 2.4535201806670033, qreg_q[4])
circuit.cz(qreg_q[0], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[0])
circuit.rz(5.3142485401016515, qreg_q[0])
circuit.rx(1.5707963267948966, qreg_q[0])
circuit.rz(0.11432813382846627, qreg_q[0])
circuit.u3(1.7984128807127167, 6.154451857160892, 4.904707139287386, qreg_q[4])
circuit.u3(3.75122900862644, 3.378783022379789, 1.857528654309458, qreg_q[2])
circuit.u3(2.513877600656069, 2.962214697558632, 1.374626462669599, qreg_q[4])
circuit.cz(qreg_q[2], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(4.712388991072937, qreg_q[2])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(1.4391674425931382, qreg_q[2])
circuit.u3(1.7098459431602464, 2.481453499573181, 4.713272534819384, qreg_q[4])
circuit.cz(qreg_q[2], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(6.2831852775569015, qreg_q[2])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(0.4049536470163334, qreg_q[2])
circuit.u3(4.575118953034685, 6.114455659736541, 2.785741790971282, qreg_q[4])
circuit.cz(qreg_q[2], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(5.221709174360444, qreg_q[2])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(2.5159352688456176, qreg_q[2])
circuit.u3(1.9870846108450013, 4.988924064346217, 5.322178113938395, qreg_q[4])
circuit.u3(1.6641776384272227, 4.90679064447882, 3.1249163516096763, qreg_q[3])
circuit.u3(4.105987283600262, 4.454543968603073, 4.640700075589087, qreg_q[4])
circuit.cz(qreg_q[3], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[3])
circuit.rz(6.283185304803015, qreg_q[3])
circuit.rx(1.5707963267948966, qreg_q[3])
circuit.rz(4.6737190623617515, qreg_q[3])
circuit.u3(3.5365229208750453, 2.6401879182197665, 2.3468939701448477, qreg_q[4])
circuit.cz(qreg_q[3], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[3])
circuit.rz(5.0557067930914945, qreg_q[3])
circuit.rx(1.5707963267948966, qreg_q[3])
circuit.rz(0.2101325959481867, qreg_q[3])
circuit.u3(5.51520071427251, 2.156186148041626, 0.6792155142126797, qreg_q[4])
circuit.u3(0.3116940462338201, 3.0800340122925416, 4.40041743248561, qreg_q[0])
circuit.u3(1.896258602505966, 5.118505406345309, 0.6112904536491852, qreg_q[1])
circuit.cz(qreg_q[0], qreg_q[1])
circuit.rx(1.5707963267948966, qreg_q[0])
circuit.rz(3.1415926538523924, qreg_q[0])
circuit.rx(1.5707963267948966, qreg_q[0])
circuit.rz(4.077944615176829, qreg_q[0])
circuit.u3(3.1415926551834255, 5.291946436327993, 2.1838606209467915, qreg_q[1])
circuit.cz(qreg_q[0], qreg_q[1])
circuit.rx(1.5707963267948966, qreg_q[0])
circuit.rz(2.533924108613516, qreg_q[0])
circuit.rx(1.5707963267948966, qreg_q[0])
circuit.rz(4.111670810370472, qreg_q[0])
circuit.u3(6.124144059487311, 2.9288497942256773, 4.475356379834622, qreg_q[1])
circuit.u3(3.9688771363432647, 3.1191463835443596, 2.958962604609695, qreg_q[1])
circuit.u3(4.589204736145513, 1.5448948140337357, 2.4276490307563727, qreg_q[4])
circuit.cz(qreg_q[1], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[1])
circuit.rz(8.393908679238393e-09, qreg_q[1])
circuit.rx(1.5707963267948966, qreg_q[1])
circuit.rz(0.9199631775614252, qreg_q[1])
circuit.u3(5.020807420741784, 0.8407796905184545, 3.1070978020714843, qreg_q[4])
circuit.u3(5.8963934736103365, 5.693849657429232, 1.3214308805061559, qreg_q[3])
circuit.u3(3.4685335168309903, 4.670570313679091, 1.9511187859933818, qreg_q[4])
circuit.cz(qreg_q[3], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[3])
circuit.rz(3.141592686789865, qreg_q[3])
circuit.rx(1.5707963267948966, qreg_q[3])
circuit.rz(5.203445423387663, qreg_q[3])
circuit.u3(3.1814943058640712, 5.373644278861795, 5.992465213740783, qreg_q[4])
circuit.cz(qreg_q[3], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[3])
circuit.rz(5.131412999510351, qreg_q[3])
circuit.rx(1.5707963267948966, qreg_q[3])
circuit.rz(0.8783734663679685, qreg_q[3])
circuit.u3(0.35740227009046566, 5.062845186388524, 0.9095466452165557, qreg_q[4])
circuit.cz(qreg_q[3], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[3])
circuit.rz(5.4718041719860535, qreg_q[3])
circuit.rx(1.5707963267948966, qreg_q[3])
circuit.rz(0.35332698559252995, qreg_q[3])
circuit.u3(0.6542891645434485, 0.12586350453589734, 4.876162528852053, qreg_q[4])
circuit.u3(3.852043733638525, 2.8795381898417993, 3.091387528230046, qreg_q[2])
circuit.u3(5.604667520076035, 1.9750801110865905, 5.846597593114194, qreg_q[3])
circuit.cz(qreg_q[2], qreg_q[3])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(0.5462365147768469, qreg_q[2])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(2.3409101959853156, qreg_q[2])
circuit.u3(4.799818646359717, 5.628665924248523, 3.424436772576779, qreg_q[3])
circuit.cz(qreg_q[2], qreg_q[3])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(3.172704217848907, qreg_q[2])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(5.826391068740031, qreg_q[2])
circuit.u3(5.359668202825704, 2.33293003282364, 5.314546764108509, qreg_q[3])
circuit.cz(qreg_q[2], qreg_q[3])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(3.7510754794921004, qreg_q[2])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(2.6987350693290053, qreg_q[2])
circuit.u3(1.833075296566542, 0.08305383325201099, 5.423945425129641, qreg_q[3])
circuit.u3(0.5652145194081396, 3.2203544921740823, 3.392635819791777, qreg_q[0])
circuit.u3(4.4083785066021886, 2.9661129401733426, 1.0235245546580067, qreg_q[4])
circuit.cz(qreg_q[0], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[0])
circuit.rz(3.141592649929718, qreg_q[0])
circuit.rx(1.5707963267948966, qreg_q[0])
circuit.rz(4.2291116117815255, qreg_q[0])
circuit.u3(1.9405877486933576, 4.962500133854696, 4.696674382739497, qreg_q[4])
circuit.u3(0.8079083765553241, 3.821705603197645, 2.632407185055634, qreg_q[2])
circuit.u3(5.942878900896554, 5.272656673022956, 0.612625029007624, qreg_q[3])
circuit.cz(qreg_q[2], qreg_q[3])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(1.679447165615794, qreg_q[2])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(1.5842048422766917, qreg_q[2])
circuit.u3(3.49217901183238, 1.4096734660380774, 0.8740496961680287, qreg_q[3])
circuit.cz(qreg_q[2], qreg_q[3])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(4.039577960356154, qreg_q[2])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(2.173455827832127, qreg_q[2])
circuit.u3(3.017573998033533, 4.860121120996679, 6.086603585972168, qreg_q[3])
circuit.cz(qreg_q[2], qreg_q[3])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(4.973480468053313, qreg_q[2])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(4.788904348307148, qreg_q[2])
circuit.u3(5.78059186517587, 1.6599347197054792, 2.460758068486451, qreg_q[3])
circuit.u3(2.618622024323834, 5.973559709565388, 0.8372645872594102, qreg_q[2])
circuit.u3(1.7058768706501013, 1.0982716800047956, 2.838775984038972, qreg_q[4])
circuit.cz(qreg_q[2], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(3.141592642472626, qreg_q[2])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(2.4844707212725146, qreg_q[2])
circuit.u3(5.56771246452814, 5.114093567255131, 4.811556249452705, qreg_q[4])
circuit.cz(qreg_q[2], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(4.094572403836858, qreg_q[2])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(4.694615998880109, qreg_q[2])
circuit.u3(4.1862071309457844, 3.3374732381161802, 1.1690916898997477, qreg_q[4])
circuit.cz(qreg_q[2], qreg_q[4])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(3.2762005645256045e-08, qreg_q[2])
circuit.rx(1.5707963267948966, qreg_q[2])
circuit.rz(0.9628096666275525, qreg_q[2])
circuit.u3(4.246004186974382, 1.5707963137541554, 6.087304670902108, qreg_q[4])

#%% Traspile it back to remove the rx gates

circuit_t = transpile(circuit,**WACQT_device_properties,optimization_level=1)
print(circuit_t)
circ_t = transpile(circ,**WACQT_device_properties,optimization_level=1)
print(circ_t)

#%%

print(get_circuit_time(circuit_t))
print(get_circuit_time(circ_t))
# %%
