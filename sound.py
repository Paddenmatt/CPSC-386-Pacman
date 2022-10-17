import pygame


class Sound:
    def __init__(self):
        pygame.mixer.init()
        self.startupsound = pygame.mixer.Sound('sounds/pacman_beginning.wav')
        self.munchpellet = pygame.mixer.Sound(
            'sounds/pacman_chomp_trimmed.wav')
        self.munchfruit = pygame.mixer.Sound('sounds/pacman_eatfruit.wav')
        self.munchghost = pygame.mixer.Sound('sounds/pacman_eatghost.wav')
        self.ghostsiren = pygame.mixer.Sound('sounds/ghostsiren.wav')
        self.death = pygame.mixer.Sound('sounds/pacman_death.wav')
        self.freightsiren = pygame.mixer.Sound('sounds/freightsiren.wav')

    def play_ghost_sound(self):
        pygame.mixer.Channel(1).unpause()
        pygame.mixer.Channel(1).play(self.ghostsiren, loops=-1)

    def play_freight_sound(self):
        pygame.mixer.Channel(1).play(self.freightsiren, loops=-1)

    def pause_ghost_sound(self):
        pygame.mixer.Channel(1).pause()

    def play_startup(self):
        pygame.mixer.Channel(0).play(self.startupsound)

    def play_death(self):
        pygame.mixer.Channel(0).play(self.death)

    def play_munch_ghost(self):
        pygame.mixer.Channel(0).play(self.munchghost)

    def play_munch_fruit(self):
        pygame.mixer.Channel(0).play(self.munchfruit)

    def play_munch_pellet(self):
        if not pygame.mixer.Channel(0).get_busy():
            pygame.mixer.Channel(0).play(self.munchpellet)
