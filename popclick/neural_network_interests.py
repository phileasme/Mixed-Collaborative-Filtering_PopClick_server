""" 
* ©Copyrights, all rights reserved at the exception of the used libraries.
* @author: Phileas Hocquard 
* Neural Network class and its running methods.
* Location : /mainsite/popclick/neural_network_interests.py
"""
# Third party libraries
# All used for Mathematical Operations / Third Party
from numpy import exp, array, random, dot
import numpy as np
from sklearn.preprocessing import normalize
import itertools

# Neural Network class
class ArtificialNeuralNetwork():
    """    
    The single neuron, neural network.
    Params:
        weights : Weight of neural nets neuron
    """
    def __init__(self):
        # Seed the random number generator running the same number at every run
        random.seed(1)

    # The Sigmoid function and its derivative.
    def __sigmoid_and_deriv(self, x, deriv=False):
        if(deriv==False):
            return 1/(1+np.exp(-x))
        return x*(1-x)

    # We train the neural network through a process of trial and error.
    # Adjusting the synaptic weights each time.
    def train(self, t_inputs, t_outputs, iterations):
        for iteration in range(iterations):
            # Forward propagation
            output = self.think(t_inputs)

            error = np.subtract(t_outputs, output)

            # Applying Backpropagation
            rectification = np.dot(t_inputs.T, error * self.__sigmoid_and_deriv(output, deriv=True))

            # Adjust the synaptic weights.
            self.weights += rectification

    # The neural network thinks.
    def think(self, inputs):
        """ Pass inputs through our neural network (our single neuron).
        Returns:
            Sigmoid derivation or sigmoid of the dot product of the given input and weight.
        """
        return self.__sigmoid_and_deriv(np.dot(inputs, self.weights))

def fuzzy_permutation(input_output):
    """ Permutating only around unique permutations for a subset of length -1
    
    Args:
        input_output (Array<Float>): An Array of interests
    Returns:
       (list_input, list_output)(tuple2<Array,Array>): The input layers and output layers under a tuple
    """
    # Acts as input array up to -1 of the array
    la = input_output[0:-1]
    # Last element of the array (acts as output)
    lb = input_output[-1]
    list_input = []
    list_output = []
    # For every array within input_output
    for idx, _ in enumerate(input_output):
        # The first one does not require permutation 
        # however is still split
        if idx != 0:
            lb_prev = lb
            lb = la[-idx]
            la[-idx] = lb_prev
        # Append the corresponding input to the list of inputs
        list_input.append((idx, la[:]))
        # Append the corresponding output to the list of outputs
        list_output.append((idx, lb))
    return (list_input, list_output)

def initialise_train_result(input_i, output_i, think_input):
    """ Initialise ANN, Train and return result
    Args: 
        input_i (2dArray) : Array containing arrays of interests
        output_i (2dArray) : Array containing arrays of single interest's
        think_input (Array) : Standardised representation of profil interest
    Return:
        Single learned interest
    """
    neural_network = ArtificialNeuralNetwork()
    # We model a  neural network with a single neuron, with X input connections and 1 output connection.
    # Were X is the number the number of interests - 1
    neural_network.weights = np.array(2 * random.random((len(think_input), 1)) - 1)
    # Convert to numpy arrays
    t_inputs = np.array(input_i)
    t_outputs = np.array(output_i)
    # Train neural network for 2000 iterations
    neural_network.train(t_inputs, t_outputs, 2000)
    # Compute new single interest from the particular trained weight
    return neural_network.think(think_input)[0]
    
#                                   Example of what is expected.
def runNN(selectables_interests=[[0.0, 0.1, 0.6, 0.7], [0.0, 0.5, 0.6, 1]], profile_interests = [0.0, 0.1, 0.2, 0.3]):
    """ runNN sets the multiple permutations required for the input and output layers,
        and then calls the initial training_result method for the number of existing interests;
        feeding PageobjectInterest's as an input and output for the training and the profile_interests for the usage.
    Args: 
        selectables_interests (2dArray) : Array containing pageobject interests
        profile_interests (Array) : Standardised representation of profil interests
    """
    #Intialise a single neuron neural network.
    # Apply vertical normalisation for the pageobject interests
    selectables_interests = normalize(selectables_interests, axis=0, norm='l1')
    # For the given size of the first element in the array (number of interests) add a dimension of such size
    Interest_Array_Inputs = [[] for i in range(len(selectables_interests[0]))]
    Interest_Array_Outputs = [[] for i in range(len(selectables_interests[0]))]
    # Creating instances of 3 dimensional Inputs/Outputs sets
    for ida, ll in enumerate(selectables_interests):
        # For the number of permutations
        current_fuzzy_element_permutation = fuzzy_permutation(ll)
        for index in range(len(current_fuzzy_element_permutation[0])):
            # Insert array inside column Interest for the input, output.
            Interest_Array_Inputs[current_fuzzy_element_permutation[0][index][0]].append(current_fuzzy_element_permutation[0][index][1][:])
            Interest_Array_Outputs[current_fuzzy_element_permutation[1][index][0]].append([current_fuzzy_element_permutation[1][index][1]])
    profile_Interest_Inputs = []
    # Creating the list of inputs (Leaving out an interest to be predicted)
    for index, inputList in enumerate(fuzzy_permutation(profile_interests)[0]):
        profile_Interest_Inputs.append(inputList[1])

    collected_interests = []
    # Training on each individual interest
    for i in range(len(profile_interests)):
        collected_interests.append(initialise_train_result(Interest_Array_Inputs[i], Interest_Array_Outputs[i], profile_Interest_Inputs[i]))
    well_ordered_interests = collected_interests[::-1]
    # Returns the outcoming interests.
    return well_ordered_interests