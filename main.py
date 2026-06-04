import pygame

import sys

pygame.init()

clock = pygame.time.Clock()

fps = 60

screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption('platformer game')

# game variables
tile_size = 50

game_over = 0

menu = True

game_paused = False

game_beaten = False

# load images
bg_img = pygame.image.load('assets/img/sky.png').convert()

restart_img = pygame.image.load('assets/img/restart_btn.png').convert_alpha()

start_img = pygame.image.load('assets/img/start_btn.png').convert_alpha()

exit_img = pygame.image.load('assets/img/exit_btn.png').convert_alpha()

door_img = pygame.image.load('assets/img/door.png').convert_alpha()



# clickable button class
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()

        # check if mouse is hovering and clicked
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        # reset click when mouse button is released
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        screen.blit(self.image, self.rect)
        return action


# player class handles movement, animation, and collision
class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:
            # handle keyboard input
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.in_air == False:
                self.vel_y = -15
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

            # reset to idle frame when no movement key is pressed
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False and key[pygame.K_a] == False and key[pygame.K_d] == False:
                self.counter = 0
                self.index = 0
                self.image = self.images_right[self.index]
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # cycle through walk animation frames
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                # wrap back to first frame at end of animation
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # apply gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # tile collision detection
            self.in_air = True
            for tile in world.tile_list:
                # horizontal collision — stop horizontal movement
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                # vertical collision
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # hitting a ceiling while jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # landing on the ground while falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False
            # touching an enemy kills the player
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
            # touching lava kills the player
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
            # touching the exit door triggers the win state
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1
            # apply movement
            self.rect.x += dx
            self.rect.y += dy
        
        # only draw player if alive
        if game_over == 0:
            screen.blit(self.image, self.rect)
        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        
        # load all walk animation frames and create mirrored left-facing versions
        for num in range(1, 5):
            img_right = pygame.image.load(f'assets/img/sprite_guy{num}.png').convert_alpha()
            img_right = pygame.transform.scale(img_right, (60, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        # start with first frame
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.direction = 0
        self.in_air = True

# world class builds the level from the grid data
class World():
    def __init__(self, data):
        self.tile_list = []
        lava_img = pygame.image.load('assets/img/lava.png').convert_alpha()
        dirt_img = pygame.image.load('assets/img/tile_dirt.png').convert_alpha()
        grass_img = pygame.image.load('assets/img/tile_grass.png').convert_alpha()
        sand_img = pygame.image.load('assets/img/tile_sand.png').convert_alpha()
        stone_img = pygame.image.load('assets/img/tile_stone.png').convert_alpha()
        metal_img = pygame.image.load('assets/img/tile_metal.png').convert_alpha()

        # loop through grid and place tiles/objects based on their number
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    lava_img = Lava(col_count * tile_size, row_count * tile_size)
                    lava_group.add(lava_img)
                if tile == 2:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 4:
                    # enemy spawn
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                if tile == 5:
                    img = pygame.transform.scale(door_img, (tile_size, tile_size * 2))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size - tile_size
                    door = ExitDoor(img_rect.x, img_rect.y)
                    exit_group.add(door)
                if tile == 6:
                    img = pygame.transform.scale(sand_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 7:
                    img = pygame.transform.scale(stone_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 8:
                    img = pygame.transform.scale(metal_img, (tile_size, tile_size))
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

# exit door, triggers win state when collided with
class ExitDoor(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(door_img, (tile_size, tile_size * 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
# enemy that patrols back and forth
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
        # move horizontally and reverse direction after 50 pixels
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1
# lava tile — kills the player on contact
class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('assets/img/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
# level layout — 0: empty, 1: lava, 2: dirt, 3: grass, 4: enemy, 5: exit door, 6: sand, 7: stone, 8: metal
level = 3
level_data = [
    # level 1
    [
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 5, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 2],
    [2, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    ],
    # level 2
    [
    [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 6, 6, 0, 0, 0, 5, 0, 0, 6],
    [6, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 6, 0, 6],
    [6, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0, 4, 0, 0, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 6, 0, 6],
    [6, 0, 0, 0, 0, 0, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 0, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 0, 0, 0, 0, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 0, 0, 0, 0, 0, 0, 6, 6, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 6, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1, 6, 6, 6, 6, 6, 6, 6],
    [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
    ],
    # level 3
    [
    [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 7, 7, 7, 7, 7, 0, 0, 0, 5, 0, 0, 0, 7],
    [7, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 7, 0, 0, 7],
    [7, 0, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 7, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 7],
    [7, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 7],
    [7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 7, 7, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 0, 0, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]
    ],
    # level 4
    [
    [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 8, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 8, 8, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 8, 8, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8],
    [8, 0, 0, 0, 0, 0, 8, 8, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 8],
    [8, 0, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 8, 8, 8, 8],
    [8, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8],
    ],

]

#resets level
def reset_level(level_num):
    global level
    player.reset(100, screen_height - 300)
    lava_group.empty()
    blob_group.empty()
    exit_group.empty()
    return World(level_data[level_num])

# create player, sprite groups, and the world
player = Player(100, screen_height - 300)

lava_group = pygame.sprite.Group()
blob_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

world = reset_level(level)

# create buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

# goes to the next level when the player reaches the exit door
def next_level():
    global level, world, game_over, game_beaten
    level += 1
    if level >= len(level_data):
        game_beaten = True
        game_over = 1
    else:
        world = reset_level(level)
        game_over = 0

# resets current level, used when the player dies
def restart_current():
    global world, game_over
    world = reset_level(level)
    game_over = 0

# main game loop
run = True
while run:
    clock.tick(fps)
    screen.blit(bg_img, (0, 0))
    # show main menu until start is pressed
    if menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            menu = False
        startMenu_font = pygame.font.SysFont('Arial', 80, bold=True)
        startMenu_text = startMenu_font.render('super epic platformer', True, (0, 175, 0))
        screen.blit(startMenu_text, (screen_width // 2 - startMenu_text.get_width() // 2,
                                screen_height // 3  - startMenu_text.get_height() // 2))

    else:
        # draw the level
        world.draw()
        # update and draw enemies, lava, and door
        if game_over == 0:
            blob_group.update()
            lava_group.update()
            exit_group.update()
        blob_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)

        # update player
        game_over = player.update(game_over)

        # death screen
        if game_over == -1:
            death_font = pygame.font.SysFont('Arial', 60, bold=True)
            death_text = death_font.render('You died! D: Try again?', True, (0, 175, 100))
            screen.blit(death_text, (screen_width // 2 - death_text.get_width() // 2,
                                     screen_height // 2 - death_text.get_height() // 2))
            if restart_button.draw():
                restart_current()
        # win screen if all levels have been beaten
        if game_over == 1:
            if game_beaten:
                gameBeaten_font = pygame.font.SysFont('Arial', 40, bold=True)
                gameBeaten_text = gameBeaten_font.render('You beat the game, Good job! Press R to restart', True, (0, 175, 100))
                screen.blit(gameBeaten_text, (screen_width // 2 - gameBeaten_text.get_width() // 2,
                                            screen_height // 2 - gameBeaten_text.get_height() // 2))
                if restart_button.draw():
                    game_beaten = False
                    level = 0
                    world = reset_level(level)
                    game_over = 0
            else:
                win_font = pygame.font.SysFont('Arial', 60, bold=True)
                win_text = win_font.render('You did it! :D press R to proceed', True, (0, 175, 100))
                screen.blit(win_text, (screen_width // 2 - win_text.get_width() // 2,
                                    screen_height // 2 - win_text.get_height() // 2))
                if restart_button.draw():
                    next_level()
            
    # FPS counter (AI coded, only for troubleshooting)
        fps_font = pygame.font.SysFont('Arial', 20)
        fps_text = fps_font.render(f'FPS: {int(clock.get_fps())}', True, (255, 255, 255))
        screen.blit(fps_text, (10, 10))

    #pause menu (partially AI coded)
        if game_paused:
                pause_font = pygame.font.SysFont('Arial', 60, bold=True)
                pause_text = pause_font.render('GAME PAUSED; press esc to continue', True, (0, 175, 100))
                screen.blit(pause_text, (screen_width // 2 - pause_text.get_width() // 2,
                                        screen_height // 2 - pause_text.get_height() // 2))    
        pygame.display.update()
        while game_paused:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_paused = False
                        
    # handle events            
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
         run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over == -1:
                restart_current()
            if event.key == pygame.K_r and game_over == 1:
                if not game_beaten:
                    next_level()
            if event.key == pygame.K_ESCAPE:
                game_paused = not game_paused  # toggle pause
    pygame.display.update()
pygame.quit()