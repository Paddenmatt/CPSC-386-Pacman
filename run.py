import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import Ghost


class GameController(object):
    def __init__(self):
        """Initialize class variables"""
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.clock = pygame.time.Clock()

    def setBackground(self):
        """Sets background color to black"""
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def startGame(self):
        """Starts Pacman game"""
        self.setBackground()
        self.nodes = NodeGroup("maze1.txt")
        self.nodes.setPortalPair((0, 17), (27, 17))     # Connects two Nodes as a Portal
        self.pacman = Pacman(self.nodes.getStartTempNode())
        self.pellets = PelletGroup("maze1.txt")
        self.ghost = Ghost(self.nodes.getStartTempNode())

    def update(self):
        """Game loop called once per frame of the game"""
        dt = self.clock.tick(30) / 1000.0
        self.pacman.update(dt)      # Updates Pacman
        self.ghost.update(dt)       # Updates Ghosts
        self.pellets.update(dt)     # Updates Pellets
        self.checkPelletEvents()
        self.checkEvents()
        self.render()

    def checkEvents(self):
        """Checks for certain key game events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

    def render(self):
        """Draws the images onto the screen"""
        self.screen.blit(self.background, (0, 0))
        self.nodes.render(self.screen)      # Draws the Nodes onto the screen
        self.pellets.render(self.screen)    # Draws the Pellets onto the screen
        self.pacman.render(self.screen)     # Draws Pacman onto the screen
        self.ghost.render(self.screen)      # Draws the Ghosts onto the screen
        pygame.display.update()

    def checkPelletEvents(self):
        """Handles all the Pellet events"""
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            self.pellets.pelletList.remove(pellet)


if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()