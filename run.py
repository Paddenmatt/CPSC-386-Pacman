from cgi import test
from tabnanny import check
import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from pauser import Pause
from text import TextGroup
from sprites import LifeSprites
from sprites import MazeSprites
from mazedata import MazeData
from sound import Sound
from timer import Timer
import os  # needed for highscore functionality
import time


class GameController(object):
    def __init__(self):
        """Initialize class variables"""
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.background_norm = None
        self.background_flash = None
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.pause = Pause(True)
        self.level = 0  # Current level
        self.lives = 5  # Pacmans lives
        self.score = 0  # Starting score
        self.textgroup = TextGroup()
        self.lifesprites = LifeSprites(self.lives)
        self.flashBG = False
        self.flashTime = 0.2
        self.flashTimer = 0
        self.fruitCaptured = []
        self.fruitNode = None
        self.mazedata = MazeData()

        # Added by Daniel C
        self.sound = Sound()

        # To control menu
        # self.running, self.playing = True, False
        self.font = RETRO_FONT
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        self.DISPLAY_W, self.DISPLAY_H = SCREENWIDTH, SCREENWIDTH
        self.mid_w, self.mid_h = self.DISPLAY_W/2, self.DISPLAY_H/2
        self.startx, self.starty = self.mid_w, self.mid_h + 227
        self.highscorex, self.highscorey = self.mid_w, self.mid_h + 50 + 205
        self.exitx, self.exity = self.mid_w, self.mid_h + 70 + 215
        self.cursor_rect = pygame.Rect(0, 0, 20, 20)
        self.offset = -100
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
        self.state = 'Start'
        self.menu = True

        menu_image_list = [pygame.transform.scale(pygame.image.load(f'chasing{n}.jpg'), (300, 80)) for n in range(2)]
        self.menu_timer = Timer(frames=menu_image_list, wait=250)
        self.image_position_menu_y = self.mid_h + 80

        # Fetch highscore
        self.highscore = None
        self.getHighScore()

    def getHighScore(self):
        # Check if hiscore.txt already exists
        if os.path.exists('hiscore.txt'):
            with open('hiscore.txt', 'r') as f:
                highscore = int(f.readline())
                self.highscore = highscore
        else:
            self.highscore = 0  # Default if high score does not exist

    def draw_image(self, image, x, y):
        image_rect = image.get_rect()
        image_rect.center = (x, y)
        self.screen.blit(image, image_rect)

    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(RETRO_FONT, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False

    def setBackground(self):
        """Sets background color to black"""
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.mazesprites.constructBackground(
            self.background_norm, self.level % 5)
        self.background_flash = self.mazesprites.constructBackground(
            self.background_flash, 5)
        self.flashBG = False
        self.background = self.background_norm

    def startGame(self):
        """Starts Pacman game"""
        self.mazedata.loadMaze(self.level)
        self.mazesprites = MazeSprites(
            self.mazedata.obj.name+".txt", self.mazedata.obj.name+"_rotation.txt")
        self.setBackground()
        self.nodes = NodeGroup(self.mazedata.obj.name+".txt")
        self.mazedata.obj.setPortalPairs(self.nodes)
        self.mazedata.obj.connectHomeNodes(self.nodes)
        self.pacman = Pacman(self.nodes.getNodeFromTiles(
            *self.mazedata.obj.pacmanStart))
        self.pellets = PelletGroup(self.mazedata.obj.name+".txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman, self.sound)

        self.ghosts.pinky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.inky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(0, 3)))
        self.ghosts.clyde.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(4, 3)))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(
            *self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.blinky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 0)))

        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.mazedata.obj.denyGhostsAccess(self.ghosts, self.nodes)

    def update(self):
        """Game loop called once per frame of the game"""
        dt = self.clock.tick(30) / 1000.0
        self.textgroup.update(dt)
        self.pellets.update(dt)
        if not self.pause.paused:
            self.ghosts.update(dt)
            if self.fruit is not None:
                self.fruit.update(dt)
            self.checkPelletEvents()
            self.checkGhostEvents()
            self.checkFruitEvents()

        if self.pacman.alive:
            if not self.pause.paused:
                self.pacman.update(dt)
        else:
            self.pacman.update(dt)

        if self.flashBG:
            self.flashTimer += dt
            if self.flashTimer >= self.flashTime:
                self.flashTimer = 0
                if self.background == self.background_norm:
                    self.background = self.background_flash
                else:
                    self.background = self.background_norm

        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()
        self.checkEvents()
        self.render()

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
                            self.textgroup.hideText()
                            self.showEntities()
                            self.sound.play_ghost_sound()
                        else:
                            self.sound.pause_ghost_sound()
                            self.textgroup.showText(PAUSETXT)
                            # self.hideEntities()

    def checkPelletEvents(self):
        """Handles all the Pellet events"""
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1

            # Check if channel is busy with other eat pellet sound
            self.sound.play_munch_pellet()

            self.updateScore(pellet.points)
            if self.pellets.numEaten == 30:    # Allow Inky to leave home once 30 pellets are eaten
                self.ghosts.inky.startNode.allowAccess(RIGHT, self.ghosts.inky)
            if self.pellets.numEaten == 70:     # Allow Clyde to leave home once 70 pellets are eaten
                self.ghosts.clyde.startNode.allowAccess(
                    LEFT, self.ghosts.clyde)
            self.pellets.pelletList.remove(pellet)
            # Sends Ghost's into FREIGHT mode when a power pellet is consumed
            if pellet.name == POWERPELLET:
                self.ghosts.startFreight()
                # If all pellets are consumed, pause the game for 3 seconds and advance to the next level
            if self.pellets.isEmpty():
                self.flashBG = True    # Flash background when level is beaten
                self.hideEntities()
                self.pause.setPause(pauseTime=3, func=self.nextLevel)

    def checkGhostEvents(self):
        """Check if Pacman has collided with the Ghost.
         If so check to see if the ghosts is in FREIGHT mode.
         If he is, then we start his spawn mode."""
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.pacman.visible = False
                    ghost.visible = False
                    self.sound.play_munch_ghost()
                    self.updateScore(ghost.points)
                    self.textgroup.addText(
                        str(ghost.points), WHITE, ghost.position.x, ghost.position.y, 8, time=1)
                    self.ghosts.updatePoints()
                    self.pause.setPause(pauseTime=1, func=self.showEntities)
                    ghost.startSpawn()
                    self.nodes.allowHomeAccess(ghost)
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -= 1
                        self.lifesprites.removeImage()
                        # PacMan has died, play his death sound
                        self.sound.play_death()
                        self.pacman.die()
                        self.sound.pause_ghost_sound()
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.textgroup.showText(GAMEOVERTXT)
                            self.pause.setPause(
                                pauseTime=3, func=self.restartGame)
                            self.menu = True
                        else:
                            self.pause.setPause(
                                pauseTime=3, func=self.resetLevel)

    def checkFruitEvents(self):
        """Fruit related events"""
        if self.pellets.numEaten == 50 or self.pellets.numEaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(
                    self.nodes.getNodeFromTiles(9, 20), self.level)
                print(self.fruit)
        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                # Play munch fruit sound!
                self.sound.play_munch_fruit()
                self.updateScore(self.fruit.points)
                self.textgroup.addText(str(
                    self.fruit.points), WHITE, self.fruit.position.x, self.fruit.position.y, 8, time=1)
                fruitCaptured = False
                for fruit in self.fruitCaptured:
                    if fruit.get_offset() == self.fruit.image.get_offset():
                        fruitCaptured = True
                        break
                if not fruitCaptured:
                    self.fruitCaptured.append(self.fruit.image)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def showEntities(self):
        """Makes entities visible"""
        self.pacman.visible = True
        self.ghosts.show()

    def hideEntities(self):
        """Hides entities"""
        self.pacman.visible = False
        self.ghosts.hide()

    def nextLevel(self):
        """Advances the player to the next level"""
        self.showEntities()
        self.level += 1
        self.pause.paused = True
        self.startGame()
        self.textgroup.updateLevel(self.level)

    def restartGame(self):
        """Restarts the game"""
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.startGame()
        self.score = 0
        self.textgroup.updateScore(self.score)
        self.textgroup.updateLevel(self.level)
        self.textgroup.showText(READYTXT)
        self.lifesprites.resetLives(self.lives)
        self.fruitCaptured = []

    def resetLevel(self):
        """Resets the level"""
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.textgroup.showText(READYTXT)

    def updateScore(self, points):
        """Updates game score"""
        self.score += points

        # Log high score
        if self.score > self.highscore:
            self.updateHighscore()

        self.textgroup.updateScore(self.score)

    def updateHighscore(self):
        """Updates highscore"""
        self.highscore = self.score
        with open('hiscore.txt', 'w') as f:
            # Write new high score, if better than last
            f.write(str(self.highscore))

    def render(self):
        """Draws the images onto the screen"""
        self.screen.blit(self.background, (0, 0))
        # self.nodes.render(self.screen)
        self.pellets.render(self.screen)   # Draws the pellets onto the screen
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)     # Draws Pacman onto the screen
        self.ghosts.render(self.screen)     # Draws ghosts onto the screen
        self.textgroup.render(self.screen)  # Draws text onto the screen

        # Display how many lives the player has left
        for i in range(len(self.lifesprites.images)):
            x = self.lifesprites.images[i].get_width() * i
            y = SCREENHEIGHT - self.lifesprites.images[i].get_height()
            self.screen.blit(self.lifesprites.images[i], (x, y))

        # Display the fruit captured onto the screen
        for i in range(len(self.fruitCaptured)):
            x = SCREENWIDTH - self.fruitCaptured[i].get_width() * (i+1)
            y = SCREENHEIGHT - self.fruitCaptured[i].get_height()
            self.screen.blit(self.fruitCaptured[i], (x, y))

        pygame.display.update()

    def check_menu_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_RETURN:
                    self.START_KEY = True
                if key == pygame.K_BACKSPACE:
                    self.BACK_KEY = True
                if key == pygame.K_DOWN:
                    self.DOWN_KEY = True
                if key == pygame.K_UP:
                    self.UP_KEY = True

    def move_cursor(self):
        if self.DOWN_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (
                    self.highscorex + self.offset, self.highscorey)
                self.state = 'Highscores'
            elif self.state == 'Highscores':
                self.cursor_rect.midtop = (
                    self.exitx + self.offset, self.exity)
                self.state = 'Exit'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (
                    self.startx + self.offset, self.starty)
                self.state = 'Start'
        if self.UP_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (
                    self.exitx + self.offset, self.exity)
                self.state = 'Exit'
            elif self.state == 'Highscores':
                self.cursor_rect.midtop = (
                    self.startx + self.offset, self.starty)
                self.state = 'Start'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (
                    self.highscorex + self.offset, self.highscorey)
                self.state = 'Highscores'

    def check_menu_input(self):
        self.move_cursor()
        if self.START_KEY:
            if self.state == 'Start':
                self.menu = False
                self.sound.play_startup()
            elif self.state == 'Highscores':
                exit()
            elif self.state == 'Exit':
                exit()
            self.menu = False

    def draw_cursor(self):
        self.draw_text("*", 20, self.cursor_rect.x, self.cursor_rect.y)

    def main_menu(self):
        self.menu = True
        while self.menu:
            self.check_menu_events()
            self.check_menu_input()

            self.screen.fill(BLACK)
            #self.draw_text('PacMan but he has a gun',
                           #20, self.mid_w, self.mid_h-120)
            pacman_image = pygame.transform.scale(
                pygame.image.load('Pacman image.JPG'), (350, 150))
            self.draw_image(pacman_image, self.mid_w, 100)

            self.draw_text('Play Game', 15, self.startx, 450)
            self.draw_text('High Scores', 15,
                           self.highscorex, 480)
            self.draw_text('Exit', 15, self.exitx, 510)

            self.draw_cursor()

            self.draw_image(self.menu_timer.imagerect(), self.mid_w, self.image_position_menu_y)
            pygame.display.update()

            self.reset_keys()

    # def check_menu_events(self):
    #     for event in pygame.event.get():
    #         for event in pygame.event.get():
    #             if event.type == QUIT:
    #                 exit()
    #             if event.type == pygame.KEYDOWN:
    #                 key = event.key
    #                 if key == pygame.K_RETURN:
    #                     self.START_KEY = True
    #                 if key == pygame.K_BACKSPACE:
    #                     self.BACK_KEY = True
    #                 if key == pygame.K_DOWN:
    #                     self.DOWN_KEY = True
    #                 if key == pygame.K_UP:
    #                     self.UP_KEY = True

    # def reset_keys(self):
    #     self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
