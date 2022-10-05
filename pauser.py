class Pause(object):
    def __init__(self, paused=False):
        """Initialize class variables"""
        self.paused = paused
        self.timer = 0
        self.pauseTime = None
        self.func = None

    def update(self, dt):
        """Game loop called once per frame of the game"""
        if self.pauseTime is not None:
            self.timer += dt
            if self.timer >= self.pauseTime:
                self.timer = 0
                self.paused = False
                self.pauseTime = None
                return self.func
        return None

    def setPause(self, playerPaused=False, pauseTime=None, func=None):
        """Called for our various pausing needs. Player or in-game pause"""
        self.timer = 0
        self.func = func
        self.pauseTime = pauseTime
        self.flip()

    def flip(self):
        """Flips the paused value"""
        self.paused = not self.paused
