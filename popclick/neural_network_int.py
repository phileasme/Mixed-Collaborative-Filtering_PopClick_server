from numpy import exp, array, random, dot
import numpy as np
import itertools

class NeuralNetwork():
    def __init__(self):
        # Seed the random number generator, so it generates the same numbers
        # every time the program runs.
        random.seed(1)

        # We model a single neuron, with 3 input connections and 1 output connection.
        # We assign random weights to a 3 x 1 matrix, with values in the range -1 to 1
        # and mean 0.

    # The Sigmoid function and its derivative.
    # This is the gradient of the Sigmoid curve.
    def __sigmoid_and_deriv(self, x, deriv=False):
        if(deriv==True):
            return x*(1-x)
        return 1/(1+np.exp(-x))
    # We train the neural network through a process of trial and error.
    # Adjusting the synaptic weights each time.
    def train(self, t_inputs, t_outputs, iterations):
        for iteration in range(iterations):
            # Pass the training set through our neural network (a single neuron).
            output = self.think(t_inputs)
            # Calculate the error (The difference between the desired output
            # and the predicted output).
            error = np.subtract(t_outputs, output)
            # Multiply the error by the input and again by the gradient of the Sigmoid curve.
            # This means less confident weights are adjusted more.
            # This means inputs, which are zero, do not cause changes to the weights.
            adjustment = dot(t_inputs.T, error * self.__sigmoid_and_deriv(output, deriv=True))

            # Adjust the weights.
            self.synaptic_weights += adjustment

    # The neural network thinks.
    def think(self, inputs):
        # Pass inputs through our neural network (our single neuron).
        return self.__sigmoid_and_deriv(dot(inputs, self.synaptic_weights))

def fuzzy_permutation(input_output):
    la = input_output[0:-1]
    lb = input_output[-1]
    list_input = []
    list_output = []
    for idx, _ in enumerate(input_output):
        if idx != 0:
            lb_prev = lb
            lb = la[-idx]
            la[-idx] = lb_prev
        list_input.append((idx, la[:]))
        list_output.append((idx, lb))
    return (list_input, list_output)

def initialise_train_result(input_i, output_i, think_input):
    neural_network = NeuralNetwork()
    neural_network.synaptic_weights = np.array(2 * random.random((len(think_input), 1)) - 1)
    t_inputs = np.array(input_i)
    t_outputs = np.array(output_i)
    neural_network.train(t_inputs, t_outputs, 2000)
    return neural_network.think(think_input)[0]
    
# Example of what is expected
def runNN(selectables_interests=[[0.0, 0.1, 0.6, 0.7], [0.0, 0.5, 0.6, 1]], profile_interests = [0.0, 0.1, 0.2, 0.3]):
    #Intialise a single neuron neural network.
    # From selections
    Interest_Array_Inputs = [[] for i in range(len(selectables_interests[0]))]
    Interest_Array_Outputs = [[] for i in range(len(selectables_interests[0]))]
    for ida, ll in enumerate(selectables_interests):
        for index in range(len(fuzzy_permutation(ll)[0])):
            Interest_Array_Inputs[fuzzy_permutation(ll)[0][index][0]].append(fuzzy_permutation(ll)[0][index][1][:])
            Interest_Array_Outputs[fuzzy_permutation(ll)[1][index][0]].append([fuzzy_permutation(ll)[1][index][1]])
    profile_Interest_Inputs = []
    for index, inputList in enumerate(fuzzy_permutation(profile_interests)[0]):
        profile_Interest_Inputs.append(inputList[1])

    collected_interests = []
    # Training on each individual interest
    for i in range(len(profile_interests)):
        collected_interests.append(initialise_train_result(Interest_Array_Inputs[i], Interest_Array_Outputs[i], profile_Interest_Inputs[i]))
    well_ordered_interests = collected_interests[::-1]
    return well_ordered_interests
# runNN()