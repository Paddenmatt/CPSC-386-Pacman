import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from random import randint


class Entity(object):
    """Any object that inherits from this class will have the basic ability to move around the maze on its own"""

    def __init__(self, node):
        """Initialize class variables"""
        self.name = None
        self.directions = {UP: Vector2(0, -1), DOWN: Vector2(0, 1),
                           LEFT: Vector2(-1, 0), RIGHT: Vector2(1, 0), STOP: Vector2()}
        self.direction = STOP
        self.setSpeed(100)
        self.radius = 10
        self.collideRadius = 5
        self.color = WHITE
        self.visible = True
        self.disablePortal = False
        self.goal = None
        self.directionMethod = self.randomDirection
        self.setStartNode(node)
        self.image = None

    def setPosition(self):
        """Sets the position of the Entity"""
        self.position = self.node.position.copy()

    def update(self, dt):
        """Game loop called once per frame of the game"""
        self.position += self.directions[self.direction]*self.speed*dt

        if self.overshotTarget():
            self.node = self.target
            directions = self.validDirections()
            direction = self.directionMethod(directions)
            if not self.disablePortal:
                if self.node.neighbors[PORTAL] is not None:
                    self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            self.setPosition()

    def validDirection(self, direction):
        """Checks if the pressed key is a valid direction"""
        if direction is not STOP:
            if self.name in self.node.access[direction]:
                if self.node.neighbors[direction] is not None:
                    return True
        return False

    def getNewTarget(self, direction):
        """Checks if there is a Node in a direction,
         If True move Pacman to that node automatically"""
        if self.validDirection(direction):
            return self.node.neighbors[direction]
        return self.node

    def overshotTarget(self):
        """Checks to see if the Entity has overshot the target node he is moving towards"""
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node2Target = vec1.magnitudeSquared()
            node2Self = vec2.magnitudeSquared()
            return node2Self >= node2Target
        return False

    def reverseDirection(self):
        """Allows the Entity to reverse directions at any time"""
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp

    def oppositeDirection(self, direction):
        """Checks to see if the input direction is the opposite of the Entity's current direction"""
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False

    def validDirections(self):
        """Gets a list of valid directions the Entity can move in"""
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                if key != self.direction * -1:
                    directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

    def randomDirection(self, directions):
        """Chooses one of the directions randomly"""
        return directions[randint(0, len(directions)-1)]

    def find_path(self, maze_map, start, target):  # A variation on A-Star
        """Determine a path in the maze map from the start to the target tile"""
        path = []   # path list
        tried = set()   # set for faster membership checks
        done = False
        curr_tile = start
        while not done:
            if curr_tile == target:
                done = True     # if at target tile, we are done
            else:
                options = [     # possible moves
                    (curr_tile[0] + 1, curr_tile[1]),
                    (curr_tile[0] - 1, curr_tile[1]),
                    (curr_tile[0], curr_tile[1] + 1),
                    (curr_tile[0], curr_tile[1] - 1)
                ]
                test = (abs(target[0] - start[0]), abs(target[1] - start[0]))
                prefer = test.index(max(test[0], test[1]))
                if prefer == 0:
                    options.sort(key=lambda x: x[0], reverse=True)
                else:
                    options.sort(key=lambda x: x[1], reverse=True)
                backtrack = True    # assume we must backtrack
                for opt in options:
                    try:
                        if maze_map[opt[0]][opt[1]] not in ('x', ) and opt not in tried:
                            backtrack = False   # if we haven't tried this option before, and it's not blocked
                            # then add to the path, and remember that it's been tried
                            path.append(opt)
                            tried.add(opt)
                            curr_tile = opt
                            break
                    except IndexError:
                        continue
                if backtrack:   # backtrack to the previous position in the path
                    curr_tile = path.pop()
        return path

    def goalDirection(self, directions):
        """Gives the Entity a 'Goal' to head towards"""
        distances = []
        for direction in directions:
            vec = self.node.position + \
                self.directions[direction]*TILEWIDTH - self.goal
            distances.append(vec.magnitudeSquared())
        index = distances.index(min(distances))
        return directions[index]

    def setStartNode(self, node):
        """Defines a starting node"""
        self.node = node
        self.startNode = node
        self.target = node
        self.setPosition()

    def setBetweenNodes(self, direction):
        """Set any entity between 2 nodes"""
        if self.node.neighbors[direction] is not None:
            self.target = self.node.neighbors[direction]
            self.position = (self.node.position + self.target.position) / 2.0

    def reset(self):
        """Reset some level components if Pacman dies"""
        self.setStartNode(self.startNode)
        self.direction = STOP
        self.speed = 100
        self.visible = True

    def setSpeed(self, speed):
        """Sets the speed of the Entity"""
        self.speed = speed * TILEWIDTH / 16

    def render(self, screen):
        """Draws the Entity onto the screen"""
        if self.visible:
            if self.image is not None:
                adjust = Vector2(TILEWIDTH, TILEHEIGHT) / 2
                p = self.position - adjust
                screen.blit(self.image, p.asTuple())
            else:
                p = self.position.asInt()
                pygame.draw.circle(screen, self.color, p, self.radius)
