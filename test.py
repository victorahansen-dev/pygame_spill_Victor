import pygame
from mario_sprites import SpriteSheet

pygame.init()
screen = pygame.display.set_mode((600, 300))
clock = pygame.time.Clock()

sheet = SpriteSheet("mario_sprites/spritesheet.png",
                    "mario_sprites/spritesheet_meta.json")

anims = {
    'idle':   sheet.get_animation('idle'),
    'walk':   sheet.get_animation('walk'),
    'run':    sheet.get_animation('run'),
    'jump':   sheet.get_animation('jump'),
    'crouch': sheet.get_animation('crouch'),
}

# Player state
x, y = 275, 180
vel_y = 0
on_ground = True
facing_right = True

current_anim = 'idle'
frame = 0
frame_timer = 0

GROUND_Y = 180
GRAVITY = 0.5
JUMP_FORCE = -12
WALK_SPEED = 3
RUN_SPEED = 6

ANIM_FPS = {
    'idle': 3, 'walk': 8, 'run': 14, 'jump': 6, 'crouch': 6
}

running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # ── Determine animation & movement ──
    moving_right = keys[pygame.K_a]   # a = right
    moving_left  = keys[pygame.K_d]   # d = left
    crouching    = keys[pygame.K_s]   # s = crouch
    jumping      = keys[pygame.K_w]   # w = jump
    running_key  = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]  # shift = run

    speed = RUN_SPEED if running_key else WALK_SPEED

    # Horizontal movement
    if moving_right and not crouching:
        x += speed
        facing_right = True
    if moving_left and not crouching:
        x -= speed
        facing_right = False

    # Jump (only when on ground)
    if jumping and on_ground:
        vel_y = JUMP_FORCE
        on_ground = False

    # Gravity
    vel_y += GRAVITY
    y += vel_y
    if y >= GROUND_Y:
        y = GROUND_Y
        vel_y = 0
        on_ground = True

    # ── Pick animation ──
    new_anim = 'idle'
    if not on_ground:
        new_anim = 'jump'
    elif crouching:
        new_anim = 'crouch'
    elif moving_right or moving_left:
        new_anim = 'run' if running_key else 'walk'

    # Reset frame when animation changes
    if new_anim != current_anim:
        current_anim = new_anim
        frame = 0
        frame_timer = 0

    # Advance frame
    frame_timer += dt
    ms_per_frame = 1000 / ANIM_FPS[current_anim]
    if frame_timer >= ms_per_frame:
        frame = (frame + 1) % len(anims[current_anim])
        frame_timer = 0

    # ── Draw ──
    screen.fill((92, 148, 252))

    sprite = anims[current_anim][frame]
    # Flip horizontally when facing left
    if not facing_right:
        sprite = pygame.transform.flip(sprite, True, False)

    screen.blit(sprite, (x, y))
    pygame.display.flip()

pygame.quit()