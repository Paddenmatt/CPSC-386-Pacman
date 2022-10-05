import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from modes import ModeController
from sprites import GhostSprites


class Ghost(Entity):
    def __init__(self, node, pacman=None, blinky=None):
        """Initialize class variables"""
        Entity.__init__(self, node)
        self.name = GHOST
        self.points = 200
        self.goal = Vector2()
        self.directionMethod = self.goalDirection
        self.pacman = pacman
        self.mode = ModeController(self)
        self.blinky = blinky
        self.homeNode = node

    def update(self, dt):
        """Game loop called once per frame of the game"""
        self.sprites.update(dt)
        self.mode.update(dt)
        if self.mode.current is SCATTER:
            self.scatter()
        elif self.mode.current is CHASE:
            self.chase()
        Entity.update(self, dt)

    def scatter(self):
        """Scatter goal is the top left corner of the screen"""
        self.goal = Vector2()

    def chase(self):
        """Chase goal is Pacman's position"""
        self.goal = self.pacman.position

    def startFreight(self):
        """Leaves the ghosts vulnerable to being eaten by Pacman"""
        self.mode.setFreightMode()
        if self.mode.current == FREIGHT:
            self.setSpeed(50)
            self.directionMethod = self.randomDirection

    def normalMode(self):
        """Resets things back to normal"""
        self.setSpeed(100)
        self.directionMethod = self.goalDirection
        self.homeNode.denyAccess(DOWN, self)

    def spawn(self):
        """Sets goal to be the location of that node"""
        self.goal = self.spawnNode.position

    def setSpawnNode(self, node):
        """Defines the spawn node"""
        self.spawnNode = node

    def startSpawn(self):
        """Checks to make sure we can start the SPAWN mode"""
        self.mode.setSpawnMode()
        if self.mode.current == SPAWN:
            self.setSpeed(150)
            self.directionMethod = self.goalDirection
            self.spawn()

    def reset(self):
        """Resets the Ghosts"""
        Entity.reset(self)
        self.points = 200
        self.directionMethod = self.goalDirection


class Blinky(Ghost):
    def __init__(self, node, pacman=None, blinky=None):
        """Initialize class variables"""
        Ghost.__init__(self, node, pacman, blinky)
        self.name = BLINKY
        self.color = RED
        self.sprites = GhostSprites(self)


class Pinky(Ghost):
    def __init__(self, node, pacman=None, blinky=None):
        """Initialize class variables"""
        Ghost.__init__(self, node, pacman, blinky)
        self.name = PINKY
        self.color = PINK
        self.sprites = GhostSprites(self)

    def scatter(self):
        """Goal is in the upper left corner"""
        self.goal = Vector2(TILEWIDTH*NCOLS, 0)

    def chase(self):
        """Target 4 tiles ahead of Pacman"""
        self.goal = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 4


class Inky(Ghost):
    def __init__(self, node, pacman=None, blinky=None):
        """Initialize class variables"""
        Ghost.__init__(self, node, pacman, blinky)
        self.name = INKY
        self.color = TEAL
        self.sprites = GhostSprites(self)

    def scatter(self):
        """Goal is in the lower right corner of the maze"""
        self.goal = Vector2(TILEWIDTH*NCOLS, TILEHEIGHT*NROWS)

    def chase(self):
        """Uses Pacmans and Blinkys position to find goal"""
        vec1 = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 2
        vec2 = (vec1 - self.blinky.position) * 2
        self.goal = self.blinky.position + vec2


class Clyde(Ghost):
    def __init__(self, node, pacman=None, blinky=None):
        """Initialize class variables"""
        Ghost.__init__(self, node, pacman, blinky)
        self.name = CLYDE
        self.color = ORANGE
        self.sprites = GhostSprites(self)

    def scatter(self):
        """Goal is in the bottom left corner of the maze"""
        self.goal = Vector2(0, TILEHEIGHT*NROWS)

    def chase(self):
        """Goal changes depending on how close he is to Pacman
        If he's less than 8 tiles away from Pacman, he retreats to his scatter goal.
        When he's far away from Pacman then he changes his mind and acts like Pinky"""
        d = self.pacman.position - self.position
        ds = d.magnitudeSquared()
        if ds <= (TILEWIDTH * 8)**2:
            self.scatter()
        else:
            self.goal = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 4


class GhostGroup(object):
    """Deals with the ghosts as a group rather than individually"""
    def __init__(self, node, pacman):
        """Initialize class variables"""
        self.blinky = Blinky(node, pacman)
        self.pinky = Pinky(node, pacman)
        self.inky = Inky(node, pacman, self.blinky)
        self.clyde = Clyde(node, pacman)
        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]

    def __iter__(self):
        """Loop through the ghost list"""
        return iter(self.ghosts)

    def update(self, dt):
        """Game loop called once per frame of the game"""
        for ghost in self:
            ghost.update(dt)

    def startFreight(self):
        """Leaves the ghosts vulnerable to being eaten by Pacman"""
        for ghost in self:
            ghost.startFreight()
        self.resetPoints()

    def setSpawnNode(self, node):
        """Defines the spawn node"""
        for ghost in self:
            ghost.setSpawnNode(node)

    def updatePoints(self):
        """Doubles ghosts point value for each ghost eating during a power pellet"""
        for ghost in self:
            ghost.points *= 2

    def resetPoints(self):
        """Resets the ghosts point value when the power pellet is done"""
        for ghost in self:
            ghost.points = 200

    def reset(self):
        """Resets a ghost"""
        for ghost in self:
            ghost.reset()

    def hide(self):
        """Hide a ghost"""
        for ghost in self:
            ghost.visible = False

    def show(self):
        """Shows the ghost"""
        for ghost in self:
            ghost.visible = True

    def render(self, screen):
        """Draws a Ghost onto the screen"""
        for ghost in self:
            ghost.render(screen)
