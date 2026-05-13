import pygame
import sys

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('platformer game')

# definerer spill variabler
tile_size = 50

# load img
bg_img = pygame.image.load('assets/img/sky.png')

#lager karakter/spilleren
class Player():
    def __init__(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        # lager en liste for alle sprites
        for num in range (1, 3):
            img_right = pygame.image.load(f'assets/img/sprite{num}.png') 
            img_right = pygame.transform.scale(img_right, (100, 100)) # skalerer karakteren
            img_left = pygame.transform.flip(img_right, True, False) # snur Y-aksen og ikke X-aksen
            self.images_right.append(img_right)
            self.images_left.append(img_left) # legger til bildene i listen
        self.image = self.images_right[self.index] # bruker første bilde når man starter spillet
        self.rect = self.image.get_rect()
        # x & y variabler
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0

    def update(self):
        dx = 0
        dy = 0
        walk_cooldown = 5

        #registerer trykk
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] and self.jumped == False:
            self.vel_y = -15
            self.jumped = True
        if key[pygame.K_SPACE] == False:
            self.jumped = False
        if key[pygame.K_LEFT]:
            dx -= 5
            self.counter += 1
            self.direction = -1
        if key[pygame.K_a]:
            dx -= 5
            self.counter += 1
            self.direction = -1
        if key[pygame.K_RIGHT]:
            dx += 5
            self.counter += 1
            self.direction = 1
        if key[pygame.K_d]:
            dx += 5
            self.counter += 1
            self.direction = 1
        # setter sprite tilbake til sprite1
        if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False and key[pygame.K_a] == False and key[pygame.K_d] == False:
            self.counter = 0
            self.index = 0
            self.image = self.images_right[self.index]
            #karakter ser mot høyre statisk
            if self.direction == 1:
                self.image = self.images_right[self.index]
            #karakter ser mot venstre statisk
            if self.direction == -1:
                self.image = self.images_left[self.index]
        #animasjon
        
        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            # bytter til neste bilde hvis self.counter er større enn walk_cooldown
            if self.index >= len(self.images_right):
                self.index = 0
            if self.direction == 1:
                self.image = self.images_right[self.index]
            if self.direction == -1:
                self.image = self.images_left[self.index]

        #GRAVITY
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        #kollisjon
        for tile in world.tile_list:
            #sjekk for kollisjon i x-akse
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0

            # check for kollisjon i y-asken
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #sjekk om karakter er under bakken (hoppe)
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top # flytter på karakter til hodet kolliderer med noe
                    self.vel_y = 0
                #sjekk om karakter er over bakken (falle)
                elif self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom # samme logikk men snudd

        #oppdater spiller posisjon
        self.rect.x += dx
        self.rect.y += dy
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            dy = 0
            
        # tegn spiller på skjerm
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, ( 255, 255, 255), self.rect, 2)

#spill vinduet/selve verden
class World():
    def __init__(self, data):
        self.tile_list = []

        #load img
        lava_img = pygame.image.load('assets/img/lava.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(lava_img, (tile_size, tile_size)) # setter bildene til størrelsen av grid
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

world_data = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

player = Player(100, screen_height - 130)
world = World(world_data)

run = True
while run:
    clock.tick(fps)
    screen.blit(bg_img, (0, 0))
    world.draw()
    player.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()