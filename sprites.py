import pygame
from constants import *
import numpy as np
from animation import Animator

BASETILEWIDTH = 16
BASETILEHEIGHT = 16
DEATH = 5


class Spritesheet(object):
    def __init__(self):
        """Initialize class variables"""
        self.sheet = pygame.image.load("images/spritesheet.png").convert()
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)
        width = int(self.sheet.get_width() / BASETILEWIDTH * TILEWIDTH)
        height = int(self.sheet.get_height() / BASETILEHEIGHT * TILEHEIGHT)
        self.sheet = pygame.transform.scale(self.sheet, (width, height))

    def getImage(self, x, y, width, height):
        """Extracts an image from the spritesheet and returns it to whoever is asking for it"""
        x *= TILEWIDTH
        y *= TILEHEIGHT
        self.sheet.set_clip(pygame.Rect(x, y, width, height))
        return self.sheet.subsurface(self.sheet.get_clip())


class PacmanSprites(Spritesheet):
    """Contains references to all the Pacman sprites"""

    def __init__(self, entity):
        """Initialize class variables"""
        Spritesheet.__init__(self)
        self.entity = entity
        self.entity.image = self.getStartImage()
        self.animations = {}
        self.defineAnimations()
        self.stopimage = (8, 0)

    def defineAnimations(self):
        """Sets Pacman's animations for each direction"""
        self.animations[LEFT] = Animator(((8, 0), (0, 0), (0, 2), (0, 0)))
        self.animations[RIGHT] = Animator(((10, 0), (2, 0), (2, 2), (2, 0)))
        self.animations[UP] = Animator(((10, 2), (6, 0), (6, 2), (6, 0)))
        self.animations[DOWN] = Animator(((8, 2), (4, 0), (4, 2), (4, 0)))
        self.animations[DEATH] = Animator(((0, 12), (2, 12), (4, 12), (6, 12), (8, 12), (
            10, 12), (12, 12), (14, 12), (16, 12), (18, 12), (20, 12)), speed=6, loop=False)

    def update(self, dt):
        """Game loop called once per frame of the game"""
        if self.entity.alive == True:
            if self.entity.direction == LEFT:
                self.entity.image = self.getImage(
                    *self.animations[LEFT].update(dt))
                self.stopimage = (8, 0)
            elif self.entity.direction == RIGHT:
                self.entity.image = self.getImage(
                    *self.animations[RIGHT].update(dt))
                self.stopimage = (10, 0)
            elif self.entity.direction == DOWN:
                self.entity.image = self.getImage(
                    *self.animations[DOWN].update(dt))
                self.stopimage = (8, 2)
            elif self.entity.direction == UP:
                self.entity.image = self.getImage(
                    *self.animations[UP].update(dt))
                self.stopimage = (10, 2)
            elif self.entity.direction == STOP:
                self.entity.image = self.getImage(*self.stopimage)
        else:
            self.entity.image = self.getImage(
                *self.animations[DEATH].update(dt))

    def reset(self):
        """Resets Pacman's animations"""
        for key in list(self.animations.keys()):
            self.animations[key].reset()

    def getStartImage(self):
        """Starting image for Pacman"""
        return self.getImage(8, 0)

    def getImage(self, x, y):
        """Retrieves an images from the spritesheet"""
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)


class GhostSprites(Spritesheet):
    """Contains references to all the Ghost sprites"""

    def __init__(self, entity):
        """Initialize class variables"""
        Spritesheet.__init__(self)
        self.x = {BLINKY: 0, PINKY: 2, INKY: 4, CLYDE: 6}
        self.entity = entity
        self.entity.image = self.getStartImage()
        self.animations = {}
        self.stopimage = (8, 0)
        self.defineAnimations()

    def defineAnimations(self):
        """Sets Pacman's animations for each direction"""
        self.animations[4] = Animator(((10, 4), (30, 4), (10, 6), (30, 6)), speed=8)  # FREIGHT FLASHING
        self.animations[5] = Animator(((10, 4), (30, 4)), speed=8)  # FREIGHT FLASHING

        x = self.x[self.entity.name]
        self.animations[LEFT] = Animator(((x, 8), (x+22, 8)), speed=9)
        self.animations[RIGHT] = Animator(((x, 10), (x+22, 10)), speed=9)
        self.animations[UP] = Animator(((x, 4), (x+22, 4)), speed=9)
        self.animations[DOWN] = Animator(((x, 6), (x+22, 6)), speed=9)

    def update(self, dt):
        """Game loop called once per frame of the game"""

        if self.entity.mode.current in [SCATTER, CHASE]:
            if self.entity.direction == LEFT:
                self.entity.image = self.getImage(*self.animations[LEFT].update(dt))

            elif self.entity.direction == RIGHT:
                self.entity.image = self.getImage(*self.animations[RIGHT].update(dt))

            elif self.entity.direction == DOWN:
                self.entity.image = self.getImage(*self.animations[DOWN].update(dt))

            elif self.entity.direction == UP:
                self.entity.image = self.getImage(*self.animations[UP].update(dt))

        elif self.entity.mode.current == FREIGHT and self.entity.mode.timer <= 5:
            self.entity.image = self.getImage(*self.animations[5].update(dt))

        elif self.entity.mode.current == FREIGHT and self.entity.mode.timer > 5:
            self.entity.image = self.getImage(*self.animations[4].update(dt))

        elif self.entity.mode.current == SPAWN:
            if self.entity.direction == LEFT:
                self.entity.image = self.getImage(8, 8)
            elif self.entity.direction == RIGHT:
                self.entity.image = self.getImage(8, 10)
            elif self.entity.direction == DOWN:
                self.entity.image = self.getImage(8, 6)
            elif self.entity.direction == UP:
                self.entity.image = self.getImage(8, 4)

    def getStartImage(self):
        """Starting image for the Ghosts"""
        return self.getImage(self.x[self.entity.name], 4)

    def getImage(self, x, y):
        """Retrieves an images from the spritesheet"""
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)


class FruitSprites(Spritesheet):
    """Contains references to all the Fruit sprites"""

    def __init__(self, entity, level):
        """Initialize class variables"""
        Spritesheet.__init__(self)
        self.entity = entity
        self.fruits = {0: (16, 8), 1: (18, 8), 2: (
            20, 8), 3: (16, 10), 4: (18, 10), 5: (20, 10)}
        self.entity.image = self.getStartImage(level % len(self.fruits))

    def getStartImage(self, key):
        """Starting image for the Fruit"""
        return self.getImage(*self.fruits[key])

    def getImage(self, x, y):
        """Retrieves an images from the spritesheet"""
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)


class LifeSprites(Spritesheet):
    """Images used to represent lives left"""

    def __init__(self, numlives):
        """Initialize class variables"""
        Spritesheet.__init__(self)
        self.resetLives(numlives)

    def removeImage(self):
        """Removes a life sprite from the screen"""
        if len(self.images) > 0:
            self.images.pop(0)

    def resetLives(self, numlives):
        """Resets life sprites"""
        self.images = []
        for i in range(numlives):
            self.images.append(self.getImage(0, 0))

    def getImage(self, x, y):
        """Retrieves an images from the spritesheet"""
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)


class MazeSprites(Spritesheet):
    """Contains references to all the Maze sprites"""

    def __init__(self, mazefile, rotfile):
        """Initialize class variables"""
        Spritesheet.__init__(self)
        self.data = self.readMazeFile(mazefile)
        self.rotdata = self.readMazeFile(rotfile)

    def getImage(self, x, y):
        """Retrieves an images from the spritesheet"""
        return Spritesheet.getImage(self, x, y, TILEWIDTH, TILEHEIGHT)

    def readMazeFile(self, mazefile):
        """Reads in current maze"""
        return np.loadtxt(mazefile, dtype='<U1')

    def constructBackground(self, background, y):
        """Creates the game background"""
        for row in list(range(self.data.shape[0])):
            for col in list(range(self.data.shape[1])):
                if self.data[row][col].isdigit():
                    x = int(self.data[row][col]) + 12
                    sprite = self.getImage(x, y)
                    rotval = int(self.rotdata[row][col])
                    sprite = self.rotate(sprite, rotval)
                    background.blit(sprite, (col*TILEWIDTH, row*TILEHEIGHT))
                elif self.data[row][col] == '=':
                    sprite = self.getImage(10, 8)
                    background.blit(sprite, (col*TILEWIDTH, row*TILEHEIGHT))

        return background

    def rotate(self, sprite, value):
        """Rotates individual map images"""
        return pygame.transform.rotate(sprite, value*90)
