import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from pauser import Pause


class GameController(object):
    def __init__(self):
        """Initialize class variables"""
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.pause = Pause(True)
        self.level = 0  # Current level
        self.lives = 5  # Pacmans lives

    def restartGame(self):
        """Restarts the game"""
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.startGame()

    def resetLevel(self):
        """Resets the level"""
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None

    def nextLevel(self):
        """Advances the player to the next level"""
        self.showEntities()
        self.level += 1
        self.pause.paused = True
        self.startGame()

    def update(self):
        """Game loop called once per frame of the game"""
        dt = self.clock.tick(30) / 1000.0
        if not self.pause.paused:       # Freezes updates if the game is paused
            self.pacman.update(dt)      # Updates Pacman
            self.ghosts.update(dt)      # Updates Ghosts
            self.pellets.update(dt)     # Updates Pellets
            self.checkPelletEvents()
            if self.fruit is not None:
                self.fruit.update(dt)
            self.checkGhostEvents()
            self.checkFruitEvents()
        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()
        self.checkEvents()
        self.render()

    def checkFruitEvents(self):
        """Fruit related events"""
        if self.pellets.numEaten == 50 or self.pellets.numEaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.getNodeFromTiles(9, 20))
        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def setBackground(self):
        """Sets background color to black"""
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def startGame(self):
        """Starts Pacman game"""
        self.setBackground()
        self.nodes = NodeGroup("maze1.txt")     # Creates the map using nodes
        self.nodes.setPortalPair((0, 17), (27, 17))     # Connects two Nodes as a Portal
        homekey = self.nodes.createHomeNodes(11.5, 14)  # Creates the Ghost's home nodes
        self.nodes.connectHomeNodes(homekey, (12, 14), LEFT)    # Connects Ghost's home nodes together
        self.nodes.connectHomeNodes(homekey, (15, 14), RIGHT)   # Connects Ghost's home nodes together
        self.pacman = Pacman(self.nodes.getNodeFromTiles(15, 26))     # Creates Pacman between two nodes
        self.pellets = PelletGroup("maze1.txt")     # Creates the pellets on the map
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)  # Creates the ghosts
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(2+11.5, 0+14))  # Spawns Blinky
        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(2+11.5, 3+14))   # Spawns Pinky
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(0+11.5, 3+14))    # Spawns Inky
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(4+11.5, 3+14))   # Spawns Clyde
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(2 + 11.5, 3 + 14))  # Determines spawn location of the ghosts
        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.nodes.denyAccessList(2+11.5, 3+14, LEFT, self.ghosts)
        self.nodes.denyAccessList(2+11.5, 3+14, RIGHT, self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.nodes.denyAccessList(12, 14, UP, self.ghosts)
        self.nodes.denyAccessList(15, 14, UP, self.ghosts)
        self.nodes.denyAccessList(12, 26, UP, self.ghosts)
        self.nodes.denyAccessList(15, 26, UP, self.ghosts)

    def checkGhostEvents(self):
        """Check if Pacman has collided with the Ghost.
        If so check to see if the ghosts is in FREIGHT mode.
        If he is, then we start his spawn mode."""
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.pacman.visible = False
                    ghost.visible = False
                    self.pause.setPause(pauseTime=1, func=self.showEntities)
                    ghost.startSpawn()
                    self.nodes.allowHomeAccess(ghost)
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -= 1
                        self.pacman.die()
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.pause.setPause(pauseTime=3, func=self.restartGame)
                        else:
                            self.pause.setPause(pauseTime=3, func=self.resetLevel)

    def showEntities(self):
        """Makes entities visible"""
        self.pacman.visible = True
        self.ghosts.show()

    def hideEntities(self):
        """Hides entities"""
        self.pacman.visible = False
        self.ghosts.hide()

    def checkEvents(self):
        """Checks for certain key game events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            # Pauses the game is the spacebar is pressed
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.pacman.alive:
                        self.pause.setPause(playerPaused=True)
                        if not self.pause.paused:
                            self.showEntities()
                        else:
                            self.hideEntities()

    def render(self):
        """Draws the images onto the screen"""
        self.screen.blit(self.background, (0, 0))
        self.nodes.render(self.screen)      # Draws the Nodes onto the screen
        self.pellets.render(self.screen)    # Draws the Pellets onto the screen
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)     # Draws Pacman onto the screen
        self.ghosts.render(self.screen)     # Draws the Ghosts onto the screen
        pygame.display.update()

    def checkPelletEvents(self):
        """Handles all the Pellet events"""
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            if self.pellets.numEaten == 30:     # Allow Inky to leave home once 30 pellets are eaten
                self.ghosts.inky.startNode.allowAccess(RIGHT, self.ghosts.inky)
            if self.pellets.numEaten == 70:     # Allow Clyde to leave home once 70 pellets are eaten
                self.ghosts.clyde.startNode.allowAccess(LEFT, self.ghosts.clyde)
            self.pellets.pelletList.remove(pellet)
            # Sends Ghost's into FREIGHT mode when a power pellet is consumed
            if pellet.name == POWERPELLET:
                self.ghosts.startFreight()
            # If all pellets are consumed, pause the game for 3 seconds and advance to the next level
            if self.pellets.isEmpty():
                self.hideEntities()
                self.pause.setPause(pauseTime=3, func=self.nextLevel)


if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()