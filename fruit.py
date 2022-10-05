import pygame
from entity import Entity
from constants import *


class Fruit(Entity):
    def __init__(self, node):
        """Initialize class variables"""
        Entity.__init__(self, node)
        self.name = FRUIT
        self.color = GREEN
        self.lifespan = 5
        self.timer = 0
        self.destroy = False
        self.points = 100
        self.setBetweenNodes(RIGHT)

    def update(self, dt):
        """Game loop called once per frame of the game"""
        self.timer += dt
        if self.timer >= self.lifespan:
            self.destroy = True