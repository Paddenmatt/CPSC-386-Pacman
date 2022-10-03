import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup


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
        self.nodes = NodeGroup()
        self.nodes.setupTestNodes()
        self.pacman = Pacman()

    def update(self):
        """Game loop called once per frame of the game"""
        dt = self.clock.tick(30) / 1000.0
        self.pacman.update(dt)
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
        self.nodes.render(self.screen)
        self.pacman.render(self.screen)
        pygame.display.update()


if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()