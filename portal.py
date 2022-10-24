import pygame
from entity import Entity
from constants import *
from timer import Timer


class Portal(Entity):
    def __init__(self, node, game):
        Entity.__init__(self, node)

        # Get screen obj
        self.screen = game.screen
        self.direction = game.pacman.direction

        # Portal animation code
        portalImages = [pygame.image.load(
            f'images/portal{n}.png') for n in range(3)]
        self.timer = Timer(frames=portalImages)
        self.rect = pygame.image.load('images/portal0.png').get_rect()

        self.speed = 5
        self.exists = False
        self.open = False

        # Fire portal
        self.fire()

    def fire(self):
        self.exists = True
        self.rect.center = (self.node.position.x, self.node.position.y)

    def draw(self):
        self.screen.blit(self.timer.imagerect(), self.rect)

    def update(self, dt):
        """Only update direction of portal"""
        self.position += self.directions[self.direction]*self.speed*dt
        self.draw()
