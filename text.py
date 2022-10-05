import pygame
from vector import Vector2
from constants import *


class Text(object):
    def __init__(self, text, color, x, y, size, time=None, id=None, visible=True):
        """Initialize class variables"""
        self.id = id
        self.text = text
        self.color = color
        self.size = size
        self.visible = visible
        self.position = Vector2(x, y)
        self.timer = 0
        self.lifespan = time
        self.label = None
        self.destroy = False
        self.setupFont("PressStart2P-Regular.ttf")
        self.createLabel()

    def setupFont(self, fontpath):
        """Sets up the font used"""
        self.font = pygame.font.Font(fontpath, self.size)

    def createLabel(self):
        """Creates the label"""
        self.label = self.font.render(self.text, 1, self.color)

    def setText(self, newtext):
        """Sets the value of the text"""
        self.text = str(newtext)
        self.createLabel()

    def update(self, dt):
        """Game loop called once per frame of the game"""
        if self.lifespan is not None:
            self.timer += dt
            if self.timer >= self.lifespan:
                self.timer = 0
                self.lifespan = None
                self.destroy = True

    def render(self, screen):
        """Draws text onto the screen"""
        if self.visible:
            x, y = self.position.asTuple()
            screen.blit(self.label, (x, y))


class TextGroup(object):
    """Groups all Text objects together"""
    def __init__(self):
        """Initialize class variables"""
        self.nextid = 10
        self.alltext = {}
        self.setupText()
        self.showText(READYTXT)

    def addText(self, text, color, x, y, size, time=None, id=None):
        """Adds Text object to list of objects"""
        self.nextid += 1
        self.alltext[self.nextid] = Text(text, color, x, y, size, time=time, id=id)
        return self.nextid

    def removeText(self, id):
        """Removes Text object from list of objects"""
        self.alltext.pop(id)

    def setupText(self):
        """Sets up all Text objects needed for the game"""
        size = TILEHEIGHT
        self.alltext[SCORETXT] = Text("0".zfill(8), WHITE, 0, TILEHEIGHT, size)
        self.alltext[LEVELTXT] = Text(str(1).zfill(3), WHITE, 23 * TILEWIDTH, TILEHEIGHT, size)
        self.alltext[READYTXT] = Text("READY!", YELLOW, 11.25 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False)
        self.alltext[PAUSETXT] = Text("PAUSED!", YELLOW, 10.625 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False)
        self.alltext[GAMEOVERTXT] = Text("GAMEOVER!", YELLOW, 10 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False)
        self.addText("SCORE", WHITE, 0, 0, size)
        self.addText("LEVEL", WHITE, 23 * TILEWIDTH, 0, size)

    def update(self, dt):
        """Game loop called once per frame of the game"""
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].update(dt)
            if self.alltext[tkey].destroy:
                self.removeText(tkey)

    def showText(self, id):
        """Displays the text"""
        self.hideText()
        self.alltext[id].visible = True

    def hideText(self):
        """Hides the text"""
        self.alltext[READYTXT].visible = False
        self.alltext[PAUSETXT].visible = False
        self.alltext[GAMEOVERTXT].visible = False

    def updateScore(self, score):
        """Updates the score text"""
        self.updateText(SCORETXT, str(score).zfill(8))

    def updateLevel(self, level):
        """Updates the level text"""
        self.updateText(LEVELTXT, str(level + 1).zfill(3))

    def updateText(self, id, value):
        """Updates the text"""
        if id in self.alltext.keys():
            self.alltext[id].setText(value)

    def render(self, screen):
        """Draws text onto the screen"""
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].render(screen)