import numpy as np
from random import randint
from random import random
from random import gauss


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def relu(x):
    return x * (x > 0)


class nn:
    def __init__(self, shapes: list):  # shapes = inp, hid, out
        self.shape = shapes
        self.W = [np.ones((shapes[i], shapes[i + 1]))
                  for i in range(len(shapes) - 1)]
        self.B = [np.ones((1)) for i in range(1, len(shapes))]

        self.randomize()

    def forward(self, inputs):
        a = inputs
        for l in range(len(self.W) - 1):
            z = np.dot(a, self.W[l]) + self.B[l]
            a = np.tanh(z)
        z = np.dot(a, self.W[-1]) + self.B[-1]
        a = sigmoid(z)
        return 1 if a > 0.5 else 0

    def randomize(self):
        for i in range(len(self.W)):
            for j in range(len(self.W[i])):
                for k in range(len(self.W[i][j])):
                    self.W[i][j][k] = random() * 2 - 1

        for i in range(len(self.B)):
            self.B[i][0] = random() * 2 - 1

    def mutate(self, rate):
        for i in range(len(self.W)):
            for j in range(len(self.W[i])):
                for k in range(len(self.W[i][j])):
                    # random -> [0,1], rate should be float
                    if random() < rate:
                        self.W[i][j][k] += gauss(0, 0.1)

        for i in range(len(self.B)):
            if random() < rate:
                self.B[i][0] += gauss(0, 0.1)

