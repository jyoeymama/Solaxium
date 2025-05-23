import pygame

pygame.init()               
pygame.mixer.init()          
pygame.mixer.music.load('bgmusic.wav')
pygame.mixer.music.play(-1, 0.0)


import time
time.sleep(10)