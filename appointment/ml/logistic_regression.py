import math
import numpy as np


class LogisticRegression:

    def __init__(self, learning_rate=0.01, epochs=1000):

        self.learning_rate = learning_rate
        self.epochs = epochs

        # weights for the input features
        self.weights = []

        # bias value
        self.bias = 0

    # convert any value into a probability between 0 and 1
    def sigmoid(self, z):

        return 1 / (1 + math.exp(-z))

    # calculate the probability for one data sample
    def predict_probability(self, features):

        z = self.bias

        for i in range(len(features)):
            z += self.weights[i] * features[i]

        return self.sigmoid(z)

    # train the model using batch gradient descent
    def train(self, X, Y):

        X = np.array(X, dtype=float)
        Y = np.array(Y, dtype=float)

        # initialize one weight for each feature
        self.weights = np.zeros(X.shape[1])

        # initialize bias
        self.bias = 0.0

        # repeat training for the given number of epochs
        for epoch in range(self.epochs):

            # calculate predictions for all training samples
            z = np.dot(X, self.weights) + self.bias

            predictions = 1 / (1 + np.exp(-z))

            # calculate prediction errors
            errors = predictions - Y

            # calculate the gradient for all weights
            weight_gradient = np.dot(X.T, errors) / len(X)

            # calculate the gradient for the bias
            bias_gradient = np.mean(errors)

            # update weights
            self.weights -= self.learning_rate * weight_gradient

            # update bias
            self.bias -= self.learning_rate * bias_gradient

        # convert weights back to a normal Python list
        self.weights = self.weights.tolist()

    # predict whether the patient will no show
    def predict(self, features):

        probability = self.predict_probability(features)

        if probability >= 0.5:
            return 1

        return 0

    # calculate the accuracy of the model
    def accuracy(self, X, Y):

        correct = 0

        for i in range(len(X)):

            prediction = self.predict(X[i])

            if prediction == Y[i]:
                correct += 1

        return correct / len(X)

    # save the learned weights and bias
    def save_weights(self, filename):

        with open(filename, "w") as file:

            for weight in self.weights:
                file.write(str(weight) + "\n")

            file.write(str(self.bias))

    # load the learned weights and bias
    def load_weights(self, filename):

        with open(filename, "r") as file:

            values = [
                line.strip()
                for line in file
                if line.strip()
            ]

        self.weights = []

        for value in values[:-1]:
            self.weights.append(float(value))

        self.bias = float(values[-1])