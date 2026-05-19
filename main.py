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

# load img — .convert() for opaque images (no alpha), much faster blitting
bg_img = pygame.image.load('assets/img/sky.png').convert()


# lager karakter/spilleren
class Player():
    def __init__(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0

        # lager en liste for alle sprites
        # FIX: .convert_alpha() on every sprite load — avoids slow per-frame pixel format conversion
        for num in range(1, 3):
            img_right = pygame.image.load(f'assets/img/sprite_idle{num}.png').convert_alpha()
            img_right = pygame.transform.scale(img_right, (100, 100))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
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

        # FIX: collapsed duplicate key checks (K_LEFT/K_a and K_RIGHT/K_d)
        # This also prevents the double-speed bug when both keys are held at once
        key = pygame.key.get_pressed()
        moving_left  = key[pygame.K_LEFT] or key[pygame.K_a]
        moving_right = key[pygame.K_RIGHT] or key[pygame.K_d]
        jump         = key[pygame.K_SPACE]

        if jump and not self.jumped:
            self.vel_y = -15
            self.jumped = True
        if not jump:
            self.jumped = False

        if moving_left:
            dx -= 5
            self.counter += 1
            self.direction = -1
        if moving_right:
            dx += 5
            self.counter += 1
            self.direction = 1

        # setter sprite tilbake til sprite1
        if not moving_left and not moving_right:
            self.counter = 0
            self.index = 0
            if self.direction == 1:
                self.image = self.images_right[self.index]
            elif self.direction == -1:
                self.image = self.images_left[self.index]

        # animasjon
        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right):
                self.index = 0
            if self.direction == 1:
                self.image = self.images_right[self.index]
            elif self.direction == -1:
                self.image = self.images_left[self.index]

        # GRAVITY
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # kollisjon
        for tile in world.tile_list:
            # sjekk for kollisjon i x-akse
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # sjekk for kollisjon i y-aksen
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0  # FIX: also reset vel_y on landing so gravity doesn't accumulate

        # oppdater spiller posisjon
        self.rect.x += dx
        self.rect.y += dy
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            dy = 0

        # tegn spiller på skjerm
        screen.blit(self.image, self.rect)


# spill vinduet/selve verden
class World():
    def __init__(self, data):
        self.tile_list = []

        # FIX: load and scale each unique tile image ONCE, outside the tile loop,
        # instead of calling image.load() + transform.scale() for every single tile.
        # This was the biggest performance issue — now O(tile types) not O(tile count).
        lava_img  = pygame.transform.scale(
            pygame.image.load('assets/img/lava.png').convert(), (tile_size, tile_size))
        dirt_img  = pygame.transform.scale(
            pygame.image.load('assets/img/tile_dirt.png').convert(), (tile_size, tile_size))
        grass_img = pygame.transform.scale(
            pygame.image.load('assets/img/tile_grass.png').convert(), (tile_size, tile_size))

        tile_images = {1: lava_img, 2: dirt_img, 3: grass_img}

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile in tile_images:
                    # FIX: copy() so each tile gets its own rect without re-loading the surface
                    img = tile_images[tile].copy()
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    self.tile_list.append((img, img_rect))
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


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

world = World(world_data)
player = Player(100, screen_height - 130)

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