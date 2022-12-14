import pygame
from entity import Entity
from constants import *
from sprites import FruitSprites


class Fruit(Entity):
    """Initialize class variables"""

    def __init__(self, node, level=0):
        Entity.__init__(self, node)
        self.name = FRUIT
        self.color = GREEN
        self.lifespan = 20
        self.timer = 0
        self.destroy = False
        self.points = 100 + level*20
        self.setBetweenNodes(RIGHT)
        self.sprites = FruitSprites(self, level)

    def update(self, dt):
        """Game loop called once per frame of the game"""
        self.timer += dt
        if self.timer >= self.lifespan:
            self.destroy = True
