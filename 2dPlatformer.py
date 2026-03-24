import pygame
from pygame.locals import *
import sys

pygame.init()

screen_width = 1820
screen_height = 1080

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')


# load image
sun_img = pygame.image.load('assets/img/sun.png')
bg_img = pygame.image.load('assets/img/sky.png')

run = True
while run:

    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()