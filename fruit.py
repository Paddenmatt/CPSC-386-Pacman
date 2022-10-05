import pygame
from entity import Entity
from constants import *
from sprites import FruitSprites


class Fruit(Entity):
    def __init__(self, node, level=0):
        """Initialize class variables"""
        Entity.__init__(self, node)
        self.name = FRUIT
        self.color = GREEN
        self.lifespan = 5
        self.timer = 0
        self.destroy = False
        self.points = 100 + level * 20
        self.setBetweenNodes(RIGHT)
        self.sprites = FruitSprites(self, level)

    def update(self, dt):
        """Game loop called once per frame of the game"""
        self.timer += dt
        if self.timer >= self.lifespan:
            self.destroy = True