import pygame
import sys

pygame.init()

# --- Setup ---
WORLD_WIDTH, WORLD_HEIGHT = 7500, 800
WIDTH, HEIGHT = 800, 800
CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("jumping")

# Physics / movement
Y_GRAVITY = 1
JUMP_HEIGHT = 18
Y_VELOCITY = 0
VELOCITY = 8
on_ground = True
FACING_LEFT = False

# Camera
cam_x = 0.0

# Animation
anim_frame = 0
anim_timer = 0
ANIM_SPEED = 6

BLOCK_SIZE = 48
GROUND_Y = 660

# --- Load assets ---
def load(path, size):
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)

STANDING  = load("assets/img/mario_standing 1.png", (48, 64))
JUMPING   = load("assets/img/mario_jumping 1.png",  (48, 64))
WALK      = [load(f"assets/img/mario_walk.gif", (48, 64)) for i in range(1, 5)]
BLOCK_IMG = load("assets/img/grass.png", (48, 48))

BACKGROUND = pygame.transform.scale(
    pygame.image.load("assets/img/sky.png").convert(), (WORLD_WIDTH, WORLD_HEIGHT)
)

# Pre-flip surfaces for facing left
STANDING_L = pygame.transform.flip(STANDING, True, False)
JUMPING_L  = pygame.transform.flip(JUMPING,  True, False)
WALK_L     = [pygame.transform.flip(f, True, False) for f in WALK]

# --- Load level ---
blocks = []
with open("level.txt", "r", encoding="utf-8-sig") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            parts = line.split()
            if len(parts) == 2:
                blocks.append(pygame.Rect(int(parts[0]), int(parts[1]), BLOCK_SIZE, BLOCK_SIZE))

mario = STANDING.get_rect(center=(400, GROUND_Y))

# --- Game loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()

    # Horizontal input
    dx = 0
    if keys[pygame.K_a]: dx, FACING_LEFT = -VELOCITY, True
    if keys[pygame.K_d]: dx, FACING_LEFT = VELOCITY, False
    MOVING = dx != 0

    # Jump
    if keys[pygame.K_SPACE] and on_ground:
        Y_VELOCITY = JUMP_HEIGHT
        on_ground = False

    # Gravity
    Y_VELOCITY -= Y_GRAVITY

    # --- X movement + collision ---
    mario.x += dx
    for block in blocks:
        if mario.colliderect(block):
            if dx > 0: mario.right = block.left
            else:      mario.left  = block.right

    # --- Y movement + collision ---
    mario.y -= Y_VELOCITY
    on_ground = False
    for block in blocks:
        if mario.colliderect(block):
            if Y_VELOCITY < 0:  # falling
                mario.bottom = block.top
                on_ground = True
            else:               # hitting ceiling
                mario.top = block.bottom
            Y_VELOCITY = 0

    # Ground floor
    if mario.centery >= GROUND_Y:
        mario.centery = GROUND_Y
        Y_VELOCITY = 0
        on_ground = True

    # --- Animation ---
    if MOVING and on_ground:
        anim_timer += 1
        if anim_timer >= ANIM_SPEED:
            anim_timer = 0
            anim_frame = (anim_frame + 1) % len(WALK)
    else:
        anim_frame = anim_timer = 0

    # --- Camera ---
    cam_x += (mario.centerx - WIDTH // 2 - cam_x) * 0.1
    cam_x = max(0, min(cam_x, WORLD_WIDTH - WIDTH))

    # --- Draw ---
    SCREEN.blit(BACKGROUND, (0, 0), (cam_x, 0, WIDTH, HEIGHT))

    for block in blocks:
        bx = block.x - cam_x
        if -BLOCK_SIZE < bx < WIDTH:
            SCREEN.blit(BLOCK_IMG, (bx, block.y))

    if not on_ground:
        surf = JUMPING_L if FACING_LEFT else JUMPING
    elif MOVING:
        surf = WALK_L[anim_frame] if FACING_LEFT else WALK[anim_frame]
    else:
        surf = STANDING_L if FACING_LEFT else STANDING

    SCREEN.blit(surf, (mario.x - cam_x, mario.y))

    pygame.display.update()
    CLOCK.tick(60)