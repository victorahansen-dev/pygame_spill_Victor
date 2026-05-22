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
game_over = 0

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
            img_right = pygame.image.load(f'assets/img/sprite_idle{num}.png') 
            img_right = pygame.transform.scale(img_right, (100,100)) # skalerer karakteren
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

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5


        if game_over == 0:
        
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

            #sjekk for kollisjon med fiender
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1

            #sjekk for kollisjon med lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1

            #oppdater spiller posisjon
            self.rect.x += dx
            self.rect.y += dy

            
        # tegn spiller på skjerm
    if game_over == 0:
        screen.blit(self.image, self.rect)

        return game_over

#spill vinduet/selve verden
class World():
    def __init__(self, data):
        self.tile_list = []

        #load img
        lava_img = pygame.image.load('assets/img/lava.png')
        dirt_img = pygame.image.load('assets/img/tile_dirt.png')
        grass_img = pygame.image.load('assets/img/tile_grass.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    lava = Lava(col_count * tile_size, row_count * tile_size)
                    lava_group.add(lava)
                if tile == 2:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size)) # setter bildene til størrelsen av grid
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size)) # setter bildene til størrelsen av grid
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 4:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('assets/img/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

world_data = [
[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 2],
[2, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
]

player = Player(100, screen_height - 130)

lava_group = pygame.sprite.Group()

blob_group = pygame.sprite.Group()

world = World(world_data)

run = True
while run:
    clock.tick(fps)
    screen.blit(bg_img, (0, 0))

    world.draw()

    if game_over == 0:
        blob_group.update()
    blob_group.draw(screen)
    lava_group.draw(screen)

    game_over = player.update(game_over)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()