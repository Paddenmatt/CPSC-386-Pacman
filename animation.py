from constants import *


class Animator(object):
    def __init__(self, frames=[], speed=20, loop=True):
        """Initialize class variables"""
        self.frames = frames
        self.current_frame = 0
        self.speed = speed
        self.loop = loop
        self.dt = 0
        self.finished = False

    def reset(self):
        """Resets the animation"""
        self.current_frame = 0
        self.finished = False

    def update(self, dt):
        """Game loop called once per frame of the game"""
        if not self.finished:
            self.nextFrame(dt)
        if self.current_frame == len(self.frames):
            if self.loop:
                self.current_frame = 0
            else:
                self.finished = True
                self.current_frame -= 1
   
        return self.frames[self.current_frame]

    def nextFrame(self, dt):
        """Moves animation to the next frame"""
        self.dt += dt
        if self.dt >= (1.0 / self.speed):
            self.current_frame += 1
            self.dt = 0





                        
