from constants import *


class MainMode(object):
    def __init__(self):
        """Initialize class variables"""
        self.timer = 0
        self.scatter()

    def update(self, dt):
        """Game loop called once per frame of the game"""
        self.timer += dt
        if self.timer >= self.time:
            if self.mode is SCATTER:
                self.chase()
            elif self.mode is CHASE:
                self.scatter()

    def scatter(self):
        """Tells the ghosts to scatter to one of the four corners of the maze"""
        self.mode = SCATTER
        self.time = 7
        self.timer = 0

    def chase(self):
        """Tells the ghosts to track Pacman"""
        self.mode = CHASE
        self.time = 20
        self.timer = 0


class ModeController(object):
    def __init__(self, entity):
        """Initialize class variables"""
        self.timer = 0
        self.time = None
        self.mainmode = MainMode()
        self.current = self.mainmode.mode
        self.entity = entity 

    def update(self, dt):
        """Game loop called once per frame of the game"""
        self.mainmode.update(dt)
        if self.current is FREIGHT:
            self.timer += dt
            if self.timer >= self.time:
                self.time = None
                self.entity.normalMode()
                self.current = self.mainmode.mode
        elif self.current in [SCATTER, CHASE]:
            self.current = self.mainmode.mode

        if self.current is SPAWN:
            if self.entity.node == self.entity.spawnNode:
                self.entity.normalMode()
                self.current = self.mainmode.mode

    def setFreightMode(self):
        """Controls the settings of Freight mode"""
        if self.current in [SCATTER, CHASE]:
            self.timer = 0
            self.time = 7
            self.current = FREIGHT
        elif self.current is FREIGHT:
            self.timer = 0

    def setSpawnMode(self):
        """Set the current mode to SPAWN only if the ghost is in FREIGHT mode"""
        if self.current is FREIGHT:
            self.current = SPAWN