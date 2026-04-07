import pygame
import sys

pygame.init()

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('platformer game')

#spill variabler
tile_size = 200


# load img
bg_img = pygame.image.load('assets/img/sky.png')

def draw_grid():
    for line in range(0, 6):
        pygame.draw.line(screen, (255,255,255), (0, line * tile_size), (screen_width, line * tile_size ))
        pygame.draw.line(screen, (255,255,255), ( line * tile_size, 0), (line * tile_size, screen_height ))


world_data = [

]

run = True
while run:
    screen.blit(bg_img, (0, 0))

    draw_grid()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()