import pygame
from vector import Vector2
from constants import *
import numpy as np


class Pellet(object):
    def __init__(self, row, column):
        """Initialize class variables"""
        self.name = PELLET
        self.position = Vector2(column * TILEWIDTH, row * TILEHEIGHT)
        self.color = WHITE
        self.radius = int(4 * TILEWIDTH / 16)
        self.collideRadius = int(4 * TILEWIDTH / 16)
        self.points = 10
        self.visible = True

    def render(self, screen):
        """Draws Pellets onto the screen"""
        if self.visible:
            p = self.position.asInt()
            pygame.draw.circle(screen, self.color, p, self.radius)


class PowerPellet(Pellet):
    def __init__(self, row, column):
        """Initialize class variables"""
        Pellet.__init__(self, row, column)
        self.name = POWERPELLET
        self.radius = int(8 * TILEWIDTH / 16)
        self.points = 50
        self.flashTime = 0.2
        self.timer = 0

    def update(self, dt):
        """Game loop called once per frame of the game"""
        self.timer += dt
        if self.timer >= self.flashTime:
            self.visible = not self.visible
            self.timer = 0


class PelletGroup(object):
    """Groups all the pellets together in a list"""
    def __init__(self, pelletfile):
        """Initialize class variables"""
        self.pelletList = []
        self.powerpellets = []
        self.createPelletList(pelletfile)
        self.numEaten = 0

    def update(self, dt):
        """Game loop called once per frame of the game"""
        for powerpellet in self.powerpellets:
            powerpellet.update(dt)

    def createPelletList(self, pelletfile):
        """Creates a list of Pellets"""
        data = self.readPelletfile(pelletfile)
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                if data[row][col] in ['.', '+']:
                    self.pelletList.append(Pellet(row, col))
                elif data[row][col] in ['P', 'p']:
                    pp = PowerPellet(row, col)
                    self.pelletList.append(pp)
                    self.powerpellets.append(pp)

    def readPelletfile(self, textfile):
        """Reads in text file"""
        return np.loadtxt(textfile, dtype='<U1')

    def isEmpty(self):
        """Checks to see when the pelletList is empty"""
        if len(self.pelletList) == 0:
            return True
        return False

    def render(self, screen):
        """Draws each Pellet onto the screen"""
        for pellet in self.pelletList:
            pellet.render(screen)