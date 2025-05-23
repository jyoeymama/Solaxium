import pygame
from pygame import mixer

pygame.init()               # Initialize all imported pygame modules
mixer.init()                # Initialize the mixer module

sound_1 = mixer.Sound('pewpew.wav')
sound_1.play()

# Optional: keep the program running long enough to hear the sound
import time
time.sleep(2)