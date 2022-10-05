import pygame
from vector import Vector2
from constants import *
import numpy as np


class Node(object):
    def __init__(self, x, y):
        """Initialize class variables"""
        self.position = Vector2(x, y)
        self.neighbors = {UP: None, DOWN: None, LEFT: None, RIGHT: None, PORTAL:None}
        # The values of the keys are the entities that have access to travel in that direction
        self.access = {UP: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       DOWN: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       LEFT: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       RIGHT: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT]}

    def render(self, screen):
        """Draws a single Node onto the screen"""
        for n in self.neighbors.keys():
            if self.neighbors[n] is not None:
                line_start = self.position.asTuple()
                line_end = self.neighbors[n].position.asTuple()
                pygame.draw.line(screen, WHITE, line_start, line_end, 4)
                pygame.draw.circle(screen, RED, self.position.asInt(), 12)

    def denyAccess(self, direction, entity):
        """Restrict entity from moving in any direction"""
        if entity.name in self.access[direction]:
            self.access[direction].remove(entity.name)

    def allowAccess(self, direction, entity):
        """Allow entity to move in any direction"""
        if entity.name not in self.access[direction]:
            self.access[direction].append(entity.name)


class NodeGroup(object):
    """Creates all the individual nodes"""
    def __init__(self, level):
        """Initialize class variables"""
        self.level = level
        self.nodesLUT = {}
        self.nodeSymbols = ['+', 'P', 'n']
        self.pathSymbols = ['.', '-', '|', 'p']
        data = self.readMazeFile(level)
        self.createNodeTable(data)
        self.connectHorizontally(data)
        self.connectVertically(data)
        self.homekey = None

    def createHomeNodes(self, xoffset, yoffset):
        """Creates the Ghost's home"""
        homedata = np.array([['X','X','+','X','X'],
                             ['X','X','.','X','X'],
                             ['+','X','.','X','+'],
                             ['+','.','+','.','+'],
                             ['+','X','X','X','+']])

        self.createNodeTable(homedata, xoffset, yoffset)
        self.connectHorizontally(homedata, xoffset, yoffset)
        self.connectVertically(homedata, xoffset, yoffset)
        self.homekey = self.constructKey(xoffset+2, yoffset)
        return self.homekey

    def connectHomeNodes(self, homekey, otherkey, direction):
        """Connects the topmost node to any other node"""
        key = self.constructKey(*otherkey)
        self.nodesLUT[homekey].neighbors[direction] = self.nodesLUT[key]
        self.nodesLUT[key].neighbors[direction * -1] = self.nodesLUT[homekey]

    def readMazeFile(self, textfile):
        """Read in the Maze text file"""
        return np.loadtxt(textfile, dtype='<U1')

    def createNodeTable(self, data, xoffset=0, yoffset=0):
        """Creates a Node Object Look Up Table"""
        for row in list(range(data.shape[0])):
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    x, y = self.constructKey(col+xoffset, row+yoffset)
                    self.nodesLUT[(x, y)] = Node(x, y)

    def constructKey(self, x, y):
        """Converts a row and column in a text file to actual pixel values on
        the screen by multiplying them by the values of the tile sizes"""
        return x * TILEWIDTH, y * TILEHEIGHT

    def connectHorizontally(self, data, xoffset=0, yoffset=0):
        """ Horizontally connects the Nodes from the dictionary"""
        for row in list(range(data.shape[0])):
            key = None
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col+xoffset, row+yoffset)
                    else:
                        otherkey = self.constructKey(col+xoffset, row+yoffset)
                        self.nodesLUT[key].neighbors[RIGHT] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[LEFT] = self.nodesLUT[key]
                        key = otherkey
                elif data[row][col] not in self.pathSymbols:
                    key = None

    def connectVertically(self, data, xoffset=0, yoffset=0):
        """Vertically connects the Nodes from the dictionary"""
        """The array used is being transposed (columns become rows and the rows become columns)"""
        dataT = data.transpose()
        for col in list(range(dataT.shape[0])):
            key = None
            for row in list(range(dataT.shape[1])):
                if dataT[col][row] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col+xoffset, row+yoffset)
                    else:
                        otherkey = self.constructKey(col+xoffset, row+yoffset)
                        self.nodesLUT[key].neighbors[DOWN] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[UP] = self.nodesLUT[key]
                        key = otherkey
                elif dataT[col][row] not in self.pathSymbols:
                    key = None

    def getNodeFromPixels(self, xpixel, ypixel):
        """Gets a node from the (x, y) pixel location"""
        if (xpixel, ypixel) in self.nodesLUT.keys():
            return self.nodesLUT[(xpixel, ypixel)]
        return None

    def getNodeFromTiles(self, col, row):
        """Gets a node from the (column, row) pixel location"""
        x, y = self.constructKey(col, row)
        if (x, y) in self.nodesLUT.keys():
            return self.nodesLUT[(x, y)]
        return None

    def getStartTempNode(self):
        nodes = list(self.nodesLUT.values())
        return nodes[0]

    def setPortalPair(self, pair1, pair2):
        """Takes in two tuple values"""
        """Connect two Nodes together using the PORTAL key"""
        key1 = self.constructKey(*pair1)
        key2 = self.constructKey(*pair2)
        if key1 in self.nodesLUT.keys() and key2 in self.nodesLUT.keys():
            self.nodesLUT[key1].neighbors[PORTAL] = self.nodesLUT[key2]
            self.nodesLUT[key2].neighbors[PORTAL] = self.nodesLUT[key1]

    def render(self, screen):
        """Draws all the Nodes onto the screen"""
        for node in self.nodesLUT.values():
            node.render(screen)

    def denyAccess(self, col, row, direction, entity):
        """Restrict entity from moving in any direction"""
        node = self.getNodeFromTiles(col, row)
        if node is not None:
            node.denyAccess(direction, entity)

    def allowAccess(self, col, row, direction, entity):
        """Allow entity to move in any direction"""
        node = self.getNodeFromTiles(col, row)
        if node is not None:
            node.allowAccess(direction, entity)

    def denyAccessList(self, col, row, direction, entities):
        """List of restricted locations per entity"""
        for entity in entities:
            self.denyAccess(col, row, direction, entity)

    def allowAccessList(self, col, row, direction, entities):
        """List of allowed locations per entity"""
        for entity in entities:
            self.allowAccess(col, row, direction, entity)

    def denyHomeAccess(self, entity):
        """Deny access of entity to access home"""
        self.nodesLUT[self.homekey].denyAccess(DOWN, entity)

    def allowHomeAccess(self, entity):
        """Allow access of entity to access home"""
        self.nodesLUT[self.homekey].allowAccess(DOWN, entity)

    def denyHomeAccessList(self, entities):
        """List of restricted entities to access home"""
        for entity in entities:
            self.denyHomeAccess(entity)

    def allowHomeAccessList(self, entities):
        """List of allowed entities to access home"""
        for entity in entities:
            self.allowHomeAccess(entity)