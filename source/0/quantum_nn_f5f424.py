# https://github.com/qismib/TraNQI/blob/ede9886c3ee2f906d7f726b6f1a9b6d8daa17ccd/programs/Quantum_NN.py

#importing packages
import numpy as np
import matplotlib.pyplot as plt

import torch
from torch.autograd import Function
from torchvision import datasets, transforms
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F

import qiskit
from qiskit import transpile, assemble
from qiskit.visualization import *

#######################
#IMPLEMENTING QUANTUM CLASS: 1 trainable parameter
#Hadamard gate (superposition) + Rotation_Y (trainable parameter) + Measure_Z. Returning the expectation value over n_shots
class QuantumCircuit:
    """
    This class provides an interface to interact with our Quantum Circuit
    """

    def __init__(self, n_qubits, backend, shots):

        #-----Circuit definition
        self._circuit = qiskit.QuantumCircuit(n_qubits)

        self.theta = qiskit.circuit.Parameter('theta')

        all_qubits = [i for i in range (n_qubits)]#qubits vector

        self._circuit.h(all_qubits)#over all the qubits
        self._circuit.barrier()
        self._circuit.ry(self.theta, all_qubits)
        self._circuit.measure_all()
        #-----

        self.backend = backend
        self.shots = shots

    def run(self, thetas):
        #acting on a simulator
        t_qc = transpile(self._circuit,
                         self.backend)#matching the features of a quantum device

        qobj = assemble(t_qc,
                    shots = self.shots,
                    parameter_binds = [{self.theta: theta} for theta in thetas])#assembling features (circuit, sampling, parameter list)

        job = self.backend.run(qobj)#running on the simulator

        result = job.result().get_counts() #counts for each values: |0> or |1>. DIVERSO DA LINK

        counts = np.array(list(result.values()))
        states = np.array(list(result.keys())).astype(float)

        # Compute probability for each state
        probabilities = counts / self.shots
        # Get state expectation
        expectation = np.sum(states * probabilities)

        return np.array([expectation])


#testing the implementation
simulator = qiskit.Aer.get_backend('qasm_simulator')
n_qubits = 1
circuit = QuantumCircuit(n_qubits, simulator, 100)

print(circuit._circuit)
#circuit._circuit.draw(output='mpl')#to print as a pyplot figure (new library needed)

exp = circuit.run([np.pi])
print('Expected value for rotation pi: {}'.format(exp[0]))


#######################
#CREATING A QUANTUM CLASSICAL CLASS
#extending autograd functions for a quantum layer(forward and backward)

class HybridFunction(Function):
    """Hybrid quantum-classical function definition"""

    @staticmethod
    def forward(ctx, input, quantum_circuit, shift):
        """Forward pass computation"""

        ctx.shift = shift
        ctx.quantum_circuit = quantum_circuit
        # context variable (it may take multiple values and return them related to the context). Used to keep track for backpropagation

        expectation_z = ctx.quantum_circuit.run(input[0].tolist()) #evaluating model with trainable parameter
        result = torch.tensor([expectation_z])
        ctx.save_for_backward(input, result) #saves a given tensor for a future call to backward (trainable parameter and the result obtained)

        return result

    @staticmethod
    def backward(ctx, grad_output): #grad_output os previous gradient

        """Backward computation"""

        input, expectation =ctx.saved_tensors #evaluated in forward
        input_list = np.array(input.tolist())

        #shifting parameters
        shift_right = input_list + np.ones(input_list.shape) * ctx.shift
        shift_left = input_list - np.ones(input_list.shape) * ctx.shift

        gradients=[]

        for i in range(len(input_list)):
            #evaluating model after shift
            expectation_right = ctx.quantum_circuit.run(shift_right[i])
            expectation_left = ctx.quantum_circuit.run(shift_left[i])

            #evaluating gradient with finite difference formula
            gradient = torch.tensor([expectation_right]) - torch.tensor([expectation_left])
            gradients.append(gradient)

        gradients = np.array([gradients]).T
        return torch.tensor([gradients]).float() * grad_output.float(), None, None
        #returns the chain of previous gradient and evaluated gradient

class Hybrid(nn.Module):
    """Hybrid quantum-cassical layer definition"""

    def __init__(self, n_qubits ,backend, shots, shift):
        super(Hybrid, self).__init__()

        self.quantum_circuit = QuantumCircuit(n_qubits, backend, shots)
        self.shift = shift #parameter shift

    def forward(self, input):
        return HybridFunction.apply(input, self.quantum_circuit, self.shift) #calling forward and backward



##################3
#DATA LOADING
#training data
n_samples=100
X_train=datasets.MNIST(root='./data', train=True, download=True, transform=transforms.Compose([transforms.ToTensor()]))
#keeping only labels 0 and 1
idx=np.append(np.where(X_train.targets == 0)[0][:n_samples], np.where(X_train.targets == 1)[0][:n_samples])


X_train.data = X_train.data[idx] #tensor values
X_train.targets = X_train.targets[idx]#tensor labels

#making batches (dim = 1). Ir returns an iterable(pytorch tensor)
train_loader = torch.utils.data.DataLoader(X_train, batch_size=1, shuffle=True)
data_iter = iter(train_loader)#making the iterable an iterator, an object with the next method that can be used in a for cycle


#showing samples
n_samples_show = 6
fig, axes = plt.subplots(nrows=1, ncols=int(n_samples_show), figsize=(10, 3))
#subolot returns the figure and axis that are indipendent as default

while n_samples_show > 0:
    images, targets = data_iter.__next__()

    axes[int(n_samples_show) - 1].imshow(images[0].numpy().squeeze(), cmap='gray')#squeeze removes unuseful dim(1). Converting into a numpy vector
    axes[int(n_samples_show) - 1].set_xticks([])
    axes[int(n_samples_show) - 1].set_yticks([])
    axes[int(n_samples_show) - 1].set_title("Labeled: {}".format(targets.item()))

    n_samples_show -= 1


#validation data
n_samples = 50

X_test = datasets.MNIST(root='./data', train=False, download=True,
                        transform=transforms.Compose([transforms.ToTensor()]))

idx = np.append(np.where(X_test.targets == 0)[0][:n_samples],
                np.where(X_test.targets == 1)[0][:n_samples])

X_test.data = X_test.data[idx]
X_test.targets = X_test.targets[idx]

test_loader = torch.utils.data.DataLoader(X_test, batch_size=1, shuffle=True)

#########################
#CREATING THE NN
class Net(nn.Module):

    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 6, kernel_size=5) #input = gray scale
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5)
        self.dropout = nn.Dropout2d() #deactivating randomly some neurons to avoid overfitting
        self.fc1 = nn.Linear(256, 64) #input dimension: CH(16) x Matrix_dim (4x4)
        self.fc2 = nn.Linear(64,1)
        self.hybrid = Hybrid(n_qubits, qiskit.Aer.get_backend('qasm_simulator'), 100, np.pi/2 )

    def forward(self, x):
        x = F.max_pool2d(F.relu(self.conv1(x)),2)
        x = F.max_pool2d(F.relu(self.conv2(x)),2)
        x = self.dropout(x)
        x = x.view(1,-1) #reshaping tensor
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        x = self.hybrid(x) #calling the forward method

        return torch.cat((x, 1-x),-1)#returning probabilities




#######################
#TRAINING AND TESTING
#function to train the nn
def training_loop (n_epochs, optimizer, model, loss_fn, train_loader):
    loss_values = []
    for epoch in range(0, n_epochs, +1):
        total_loss = []

        for batch_idx, (data, target) in enumerate(train_loader):
            optimizer.zero_grad()#getting rid of previous gradients

            output = model(data)#forward pass
            loss = loss_fn(output, target)
            loss.backward()

            optimizer.step()#updating parameters
            total_loss.append(loss.item())#item transforms into a number

        loss_values.append(sum(total_loss)/len(total_loss))#obtainign the average loss
        print('Training [{:.0f}%]   Loss: {:.4f}'.format(100*(epoch+1)/n_epochs, loss_values[-1]))

    return loss_values

#defining a function to test our net
def validate(model, test_loader, loss_function, n_test, axes):
    correct = 0
    total_loss = []
    count = 0

    with torch.no_grad():  # disabling the gradient as we don't want to update parameters
        for batch_idx, (data, target) in enumerate(test_loader):
            output = model(data)  #evaluating the model on test data

            # evaluating the accuracy of our model
            pred = output.argmax(dim=1,
                                 keepdim=True)  # we are interested in the max value of probability
            correct += pred.eq(target.view_as(pred)).sum().item()  # checking if it matches with label

            #evluating loss function
            loss = loss_function(output, target)
            total_loss.append(loss.item())

            #printing the resut as images
            if count >= n_test:
                continue
            else:
                axes[count].imshow(data[0].numpy().squeeze(), cmap='gray')

                axes[count].set_xticks([])
                axes[count].set_yticks([])
                axes[count].set_title('Predicted {}'.format(pred.item()))
            count += 1

        print('Performance on test data: \n\tLoss: {:.4f}\n\tAccuracy: {:.1f}%'
              .format(sum(total_loss)/len(total_loss),(correct / len(test_loader))*100))


#Training the NN
#we can use any optimiser, learning rate and cost/loss function to train over multiple epochs

model = Net()
params = list(model.parameters())

learning_rate = 0.001
optimizer = optim.Adam(params, learning_rate)
loss_func = nn.NLLLoss()

epochs = 20
loss_list = []
model.train() #training the module in training mode(specifying the intention to the layers). Used for dropout or batchnorm

loss_list = (training_loop(epochs, optimizer, model, loss_func, train_loader))


#plotting the training graph
plt.figure(num=2)
plt.plot(loss_list)
plt.title('Hybrid NN Training convergence')
plt.xlabel('Training Iterations')
plt.ylabel('Neg Log Likelihood Loss')

###########################
#TESTING THE NN
n_test_show = 6
fig, axes = plt.subplots(nrows=1, ncols=n_test_show, figsize=(10, 3))

model.eval()
validate(model, test_loader, loss_func, n_test_show, axes)

plt.show()