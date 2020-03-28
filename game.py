import pygame
from nnetwork import nn
import numpy as np
import random
from random import randint
from pygame.locals import *

pygame.init()
pygame.display.set_caption('Flappy Bird')

blue = (0, 0, 255)
red = (255, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)


class box:
    def __init__(self, spaceHeight, boxWidth, spaceForInit=0):
        self.x = 1300 + spaceForInit
        self.boxWidth = boxWidth
        self.y1 = 0
        self.y1_height = randint(0, 720 - spaceHeight)
        self.y2 = self.y1_height + spaceHeight
        self.y2_height = 720 - self.y2

    def drawBox(self, Displayer, closestBox):
        if not self == closestBox:
            pygame.draw.rect(Displayer, black, [
                self.x, self.y2, self.boxWidth, self.y2_height])
            pygame.draw.rect(Displayer, black, [
                self.x, self.y1, self.boxWidth, self.y1_height])
        else:
            pygame.draw.rect(Displayer, (255, 0, 255), [
                self.x, self.y2, self.boxWidth, self.y2_height])
            pygame.draw.rect(Displayer, (255, 0, 255), [
                self.x, self.y1, self.boxWidth, self.y1_height])


class bird:
    def __init__(self, withAI, brain=None):
        self.alive = True
        self.radius = 15
        self.x = 200
        self.y = 100 if not withAI else randint(5, 715)
        self.gravity = 14
        self.velocity = 1
        self.score = 0
        self.fitness = 0
        self.brain = nn([4, 4, 1])
        if brain is not None:
            self.brain.W = [w.copy() for w in brain.W]
            self.brain.B = [b.copy() for b in brain.B]
            # 0.1 is probability of mutation for each node
            self.brain.mutate(0.1)

    def drawBird(self, Displayer):
        if self.alive:
            pygame.draw.circle(
                Displayer, red, [self.x, self.y], self.radius)

    def isAlive(self, closestBox):
        if self.y >= 720 or self.y <= 0:
            self.alive = False
        else:
            dist = closestBox.x - 200
            if dist >= -75 and dist <= self.radius:
                if self.y - self.radius <= closestBox.y1_height or self.y + self.radius >= closestBox.y2:
                    self.alive = False
        return self.alive

    def update(self):
        if self.alive:
            self.score += 1
        self.gravity = min(15, self.gravity)
        self.gravity += self.velocity
        self.y += self.gravity

    def jump(self):
        self.gravity = -6

    def think(self, closestBox):
        inputs = [self.y / 720,
                  closestBox.y2/720,
                  closestBox.y1_height/720,
                  closestBox.x/1300
                  ]
        if self.brain.forward(inputs) == 1:
            self.jump()


class game:
    def __init__(self, amountOfBirds):
        self.gameDisplay = pygame.display.set_mode((1280, 720))
        self.iteration = 0
        self.slide = 5
        self.amountOfBirds = amountOfBirds
        self.boxes = [box(200, 75, i * 400) for i in range(5)]
        self.closestBox = self.boxes[0]
        self.minDistance = 1300
        self.birds = [bird(True) for i in range(self.amountOfBirds)]
        self.birdsSaved = []
        self.birdCounter = len(self.birds)
        self.clock = pygame.time.Clock()
        self.run = True

    def draw(self):
        self.gameDisplay.fill(white)
        for box in self.boxes:
            box.drawBox(self.gameDisplay, self.closestBox)
        for bird in self.birds:
            bird.drawBird(self.gameDisplay)

    def calculate_fitness(self):
        sum = 0
        for bird in self.birdsSaved:
            sum += bird.score
        for bird in self.birdsSaved:
            bird.fitness = bird.score / sum

    def call_next_generation(self):
        self.calculate_fitness()
        for i in range(len(self.birdsSaved)):
            brain = self.pickBrain()
            self.birds.append(bird(True, brain))
        self.birdsSaved = []
        self.boxes = [box(200, 75, i * 400) for i in range(5)]
        self.minDistance = 1300
        self.closestBox = self.boxes[0]

    def pickBrain(self):
        index = 0
        r = np.random.rand(1)[0]

        while r > 0:
            r -= self.birdsSaved[index].fitness
            index += 1
        bird = self.birdsSaved[index-1]
        return bird.brain

    def play(self):
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
            self.iteration += 1
            self.closestBox = self.boxes[0]
            self.minDistance = 1300
            for i in range(len(self.boxes)):
                self.boxes[i].x -= self.slide
                tempDistance = self.boxes[i].x - 200  # 200 = bird's x
                if tempDistance > -76 and tempDistance < self.minDistance:
                    self.closestBox = self.boxes[i]
                    self.minDistance = tempDistance
                if self.boxes[i].x < -100:
                    self.boxes[i] = box(200, 75, 550)
            for bird in self.birds:
                bird.think(self.closestBox)
                bird.y -= 11
                bird.update()
                if not bird.isAlive(self.closestBox):
                    self.birdsSaved.append(bird)
                    self.birds.remove(bird)
            self.draw()
            pygame.display.update()

            if len(self.birds) == 0:  # play again
                self.calculate_fitness()
                self.call_next_generation()
            self.clock.tick(200)


if __name__ == '__main__':
    game = game(amountOfBirds=1000)
    game.play()
