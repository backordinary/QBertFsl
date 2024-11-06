# https://github.com/makotonakai/Mitou-2019-Quantum-GAN/blob/1c3350849e87e61585884b2b2ff8117c6c3f9556/author_code/test.py
from tools.utils import get_zero_state
from tools.qcircuit import *
from frqi.frqi import *
from model.model_pure import *
from generator.gates import *
from generator.circuit import *

from qiskit import * 


size = 5

testimg = [[255,255,255,255], [0, 0, 0, 0], [255, 255, 255, 255], [0, 0, 0, 0]]

#show original image
#plt.imshow(x_train[img_num], cmap='gray')
#plt.savefig('mnistimg'+str(img_num)+'.png')
#plt.show()


nqubits = 6
control = [num for num in range(1,5)]
target = 0
anc = [nqubits-1]

# real image encoding
qc = QuantumCircuit(nqubits)
state = frqiEncoder4(qc, testimg, control, target, anc)
genimg = frqiDecoder4(state, testimg, control)
print(genimg)


# gen = Generator(nqubits)
# qc_fake = gen.qc
# qc_fake = circ_frqiEncoder(qc_fake, testimg, control, target, anc)
# fake_state = gen.getState()
# print(fake_state)











  
