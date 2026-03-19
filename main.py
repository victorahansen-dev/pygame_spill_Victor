import pygame
import sys
import math
import random

pygame.init()

# ── Constants ──────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1800, 1000
FPS = 60
GRAVITY = 0.55
TILE = 48

# Colours
SKY        = (40,  67,  100)
PLATFORM_C = (60,  90, 140)
PLAYER_C   = (80, 200, 120)
ENEMY_C    = (200,  60,  60)
ITEM_C     = (255, 220,  50)
KEY_C      = (255, 180,   0)
EXIT_C     = (100, 255, 200)
HIT_C      = (255, 255, 255)
ATTACK_C   = (255, 120,  40)
UI_BG      = (10,  10,  25, 180)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ascent")
clock = pygame.time.Clock()
font_big   = pygame.font.SysFont("monospace", 32, bold=True)
font_small = pygame.font.SysFont("monospace", 18)


# ── Camera ──────────────────────────────────────────────────────────────────
class Camera:
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0

    def apply(self, rect):
        return rect.move(-self.offset_x, -self.offset_y)

    def update(self, target):
        self.offset_x = target.centerx - WIDTH  // 2
        self.offset_y = target.centery - HEIGHT // 2


# ── Platform ────────────────────────────────────────────────────────────────
class Platform:
    def __init__(self, x, y, w, h=TILE//2):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface, cam):
        r = cam.apply(self.rect)
        pygame.draw.rect(surface, PLATFORM_C, r, border_radius=4)
        pygame.draw.rect(surface, (90, 130, 190), r, 2, border_radius=4)


# ── Collectible (gem) ────────────────────────────────────────────────────────
class Gem:
    def __init__(self, x, y):
        self.rect  = pygame.Rect(x, y, 24, 24)
        self.alive = True
        self.t     = 0

    def update(self):
        self.t += 0.05

    def draw(self, surface, cam):
        if not self.alive:
            return
        r   = cam.apply(self.rect)
        bob = int(math.sin(self.t) * 4)
        cx, cy = r.centerx, r.centery + bob
        points = [(cx, cy-12),(cx+10, cy-2),(cx+6, cy+10),(cx-6, cy+10),(cx-10, cy-2)]
        pygame.draw.polygon(surface, ITEM_C, points)
        pygame.draw.polygon(surface, (255,255,180), points, 2)


# ── Key ──────────────────────────────────────────────────────────────────────
class Key:
    def __init__(self, x, y):
        self.rect  = pygame.Rect(x, y, 28, 28)
        self.alive = False   # spawns only after gem collected
        self.t     = 0

    def update(self):
        if self.alive:
            self.t += 0.04

    def draw(self, surface, cam):
        if not self.alive:
            return
        r   = cam.apply(self.rect)
        bob = int(math.sin(self.t) * 5)
        cx, cy = r.centerx, r.centery + bob
        pygame.draw.circle(surface, KEY_C, (cx, cy-6), 9, 3)
        pygame.draw.line(surface, KEY_C, (cx, cy+3), (cx, cy+12), 3)
        pygame.draw.line(surface, KEY_C, (cx+3, cy+7), (cx+7, cy+7), 3)
        pygame.draw.line(surface, KEY_C, (cx+3, cy+10), (cx+6, cy+10), 3)


# ── Exit door ────────────────────────────────────────────────────────────────
class Exit:
    def __init__(self, x, y):
        self.rect   = pygame.Rect(x, y, TILE, TILE*2)
        self.locked = True

    def draw(self, surface, cam):
        r = cam.apply(self.rect)
        col = (40, 80, 80) if self.locked else EXIT_C
        pygame.draw.rect(surface, col, r, border_radius=6)
        pygame.draw.rect(surface, (200,255,240) if not self.locked else (60,120,120), r, 3, border_radius=6)
        label = font_small.render("EXIT" if not self.locked else "LOCKED", True, (200,255,240))
        surface.blit(label, (r.centerx - label.get_width()//2, r.centery - label.get_height()//2))


# ── Attack hitbox ────────────────────────────────────────────────────────────
class AttackHitbox:
    def __init__(self):
        self.rect    = pygame.Rect(0,0,50,40)
        self.active  = False
        self.timer   = 0
        self.duration = 14   # frames

    def trigger(self, player_rect, facing):
        self.active = True
        self.timer  = self.duration
        if facing == 1:
            self.rect.midleft = player_rect.midright
        else:
            self.rect.midright = player_rect.midleft

    def update(self):
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = False

    def draw(self, surface, cam):
        if not self.active:
            return
        r = cam.apply(self.rect)
        s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        s.fill((255, 120, 40, 120))
        surface.blit(s, r.topleft)
        pygame.draw.rect(surface, ATTACK_C, r, 2, border_radius=4)


# ── Player ───────────────────────────────────────────────────────────────────
class Player:
    W, H = 32, 44

    def __init__(self, x, y):
        self.rect       = pygame.Rect(x, y, self.W, self.H)
        self.vel_x      = 0.0
        self.vel_y      = 0.0
        self.on_ground  = False
        self.facing     = 1          # 1 = right, -1 = left
        self.hp         = 5
        self.max_hp     = 5
        self.inv_timer  = 0          # invincibility frames after hit
        self.attack     = AttackHitbox()
        self.atk_cd     = 0
        self.dead       = False
        self.anim_t     = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        speed = 4.5
        self.vel_x = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.vel_x = -speed
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x =  speed
            self.facing =  1
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = -13
            self.on_ground = False

        # Attack
        if keys[pygame.K_z] or keys[pygame.K_j]:
            if self.atk_cd == 0:
                self.attack.trigger(self.rect, self.facing)
                self.atk_cd = 22

    def update(self, platforms):
        if self.dead:
            return

        self.handle_input()
        self.vel_y += GRAVITY
        self.anim_t += 1

        # Move X
        self.rect.x += int(self.vel_x)
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_x > 0:
                    self.rect.right = p.rect.left
                elif self.vel_x < 0:
                    self.rect.left  = p.rect.right

        # Move Y
        self.on_ground = False
        self.rect.y += int(self.vel_y)
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:
                    self.rect.bottom = p.rect.top
                    self.on_ground   = True
                    self.vel_y       = 0
                elif self.vel_y < 0:
                    self.rect.top    = p.rect.bottom
                    self.vel_y       = 0

        # Timers
        if self.inv_timer  > 0: self.inv_timer  -= 1
        if self.atk_cd     > 0: self.atk_cd     -= 1
        self.attack.update()

        # Update hitbox position if attack still active
        if self.attack.active:
            if self.facing == 1:
                self.attack.rect.midleft  = self.rect.midright
            else:
                self.attack.rect.midright = self.rect.midleft

    def take_damage(self, amount=1):
        if self.inv_timer > 0:
            return
        self.hp -= amount
        self.inv_timer = 50
        if self.hp <= 0:
            self.dead = True

    def draw(self, surface, cam):
        r = cam.apply(self.rect)

        # Flash when invincible
        if self.inv_timer > 0 and (self.inv_timer // 4) % 2 == 0:
            col = HIT_C
        else:
            col = PLAYER_C

        # Body
        pygame.draw.rect(surface, col, r, border_radius=6)

        # Eye
        eye_x = r.right - 8 if self.facing == 1 else r.left + 8
        pygame.draw.circle(surface, (20,20,40), (eye_x, r.top+14), 5)
        pygame.draw.circle(surface, (255,255,255), (eye_x, r.top+14), 2)

        # Legs (simple walk anim)
        leg_off = int(math.sin(self.anim_t * 0.25) * 6) if abs(self.vel_x) > 0.1 else 0
        pygame.draw.line(surface, (50,160,90), (r.centerx-6, r.bottom), (r.centerx-6+leg_off, r.bottom+8), 3)
        pygame.draw.line(surface, (50,160,90), (r.centerx+6, r.bottom), (r.centerx+6-leg_off, r.bottom+8), 3)

        self.attack.draw(surface, cam)


# ── Enemy ────────────────────────────────────────────────────────────────────
class Enemy:
    W, H = 34, 44
    PATROL_SPEED  = 1.8
    CHASE_SPEED   = 3.2
    DETECT_RANGE  = 220
    ATTACK_RANGE  = 55
    ATTACK_CD     = 70

    def __init__(self, x, y, patrol_left, patrol_right):
        self.rect          = pygame.Rect(x, y, self.W, self.H)
        self.vel_y         = 0.0
        self.facing        = 1
        self.patrol_left   = patrol_left
        self.patrol_right  = patrol_right
        self.state         = "patrol"  # patrol | chase | attack
        self.atk_cd        = 0
        self.hp            = 3
        self.alive         = True
        self.hit_flash     = 0
        self.anim_t        = 0

    def update(self, platforms, player):
        if not self.alive:
            return

        self.vel_y += GRAVITY
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        # State machine
        if dist < self.ATTACK_RANGE:
            self.state = "attack"
        elif dist < self.DETECT_RANGE:
            self.state = "chase"
        else:
            self.state = "patrol"

        # Movement
        if self.state == "patrol":
            self.rect.x += self.PATROL_SPEED * self.facing
            if self.rect.right >= self.patrol_right or self.rect.left <= self.patrol_left:
                self.facing *= -1
        elif self.state == "chase":
            move = self.CHASE_SPEED if dx > 0 else -self.CHASE_SPEED
            self.rect.x += move
            self.facing = 1 if dx > 0 else -1
        elif self.state == "attack":
            self.facing = 1 if dx > 0 else -1
            if self.atk_cd == 0:
                player.take_damage(1)
                self.atk_cd = self.ATTACK_CD

        if self.atk_cd     > 0: self.atk_cd  -= 1
        if self.hit_flash  > 0: self.hit_flash -= 1
        self.anim_t += 1

        # Gravity + platform collision
        self.rect.y += int(self.vel_y)
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0

    def take_damage(self, amount=1):
        self.hp -= amount
        self.hit_flash = 10
        if self.hp <= 0:
            self.alive = False

    def draw(self, surface, cam):
        if not self.alive:
            return
        r   = cam.apply(self.rect)
        col = HIT_C if self.hit_flash > 0 else ENEMY_C

        pygame.draw.rect(surface, col, r, border_radius=5)

        # Angry eyes
        eye_x = r.right-8 if self.facing==1 else r.left+8
        pygame.draw.circle(surface, (20,0,0),   (eye_x, r.top+14), 5)
        pygame.draw.circle(surface, (255,80,80),(eye_x, r.top+14), 2)

        # Legs
        leg_off = int(math.sin(self.anim_t*0.2)*5) if self.state != "attack" else 0
        pygame.draw.line(surface, (160,40,40),(r.centerx-6,r.bottom),(r.centerx-6+leg_off,r.bottom+8),3)
        pygame.draw.line(surface, (160,40,40),(r.centerx+6,r.bottom),(r.centerx+6-leg_off,r.bottom+8),3)

        # State indicator above head
        if self.state == "chase":
            pygame.draw.circle(surface, (255,200,0),(r.centerx, r.top-10),5)
        elif self.state == "attack":
            pygame.draw.circle(surface, (255,50,50),(r.centerx, r.top-10),6)

        # HP bar
        bar_w = self.rect.w
        filled = int(bar_w * self.hp / 3)
        pygame.draw.rect(surface, (80,0,0),   (r.left, r.top-8, bar_w, 5))
        pygame.draw.rect(surface, (220,60,60),(r.left, r.top-8, filled, 5))


# ── Level builder ─────────────────────────────────────────────────────────────
def build_level():
    """Returns (platforms, enemies, gem, key, exit_door)"""
    platforms = []
    ground_y  = 1400

    # Ground slabs
    for gx in range(-200, 2000, TILE*3):
        platforms.append(Platform(gx, ground_y, TILE*3))

    # Ascending platforms (the 'tower')
    layout = [
        # (x,   y,    width)
        (100,  1280,  200),
        (320,  1160,  160),
        (520,  1040,  180),
        (260,   920,  200),
        (480,   800,  160),
        (180,   680,  200),
        (420,   560,  180),
        (120,   440,  200),
        (380,   320,  160),
        (200,   200,  220),   # near-top platform with gem
        (400,    80,  160),   # top platform with exit
    ]
    for x, y, w in layout:
        platforms.append(Platform(x, y, w))

    # Enemies  (x, y, patrol_left, patrol_right)
    enemies = [
        Enemy(200,  ground_y - Enemy.H, 100, 400),
        Enemy(350,  1240 - Enemy.H,     320, 520),
        Enemy(550,  1000 - Enemy.H,     520, 700),
        Enemy(300,   840 - Enemy.H,     260, 480),
        Enemy(220,   620 - Enemy.H,     180, 380),
        Enemy(440,   500 - Enemy.H,     380, 620),
        Enemy(250,   160 - Enemy.H,     200, 420),
    ]

    gem       = Gem(270, 165)          # on second-to-top platform
    key       = Key(440,  45)          # on top platform
    exit_door = Exit(490,  80 - TILE*2)

    return platforms, enemies, gem, key, exit_door


# ── HUD ──────────────────────────────────────────────────────────────────────
def draw_hud(surface, player, has_gem, has_key):
    # HP bar
    for i in range(player.max_hp):
        col = (80,200,120) if i < player.hp else (40,40,60)
        pygame.draw.rect(surface, col, (14 + i*28, 14, 22, 22), border_radius=4)
        pygame.draw.rect(surface, (255,255,255), (14+i*28, 14, 22, 22), 1, border_radius=4)

    # Inventory row
    label = font_small.render("GEM", True, ITEM_C if has_gem else (60,60,80))
    surface.blit(label, (14, 44))
    label2 = font_small.render("KEY", True, KEY_C if has_key else (60,60,80))
    surface.blit(label2, (70, 44))

    # Controls hint (fades out)
    hint = font_small.render("WASD/Arrows: move   SPACE/W: jump   Z/J: attack", True, (80,100,130))
    surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT-26))


# ── Game states ───────────────────────────────────────────────────────────────
def show_screen(surface, title, subtitle, color=(180,230,180)):
    surface.fill(SKY)
    t  = font_big.render(title,    True, color)
    s  = font_small.render(subtitle, True, (120,160,180))
    surface.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 40))
    surface.blit(s, (WIDTH//2 - s.get_width()//2, HEIGHT//2 + 10))
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                waiting = False


# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    show_screen(screen, "ASCENT",
                "Collect the Gem  →  Grab the Key  →  Reach the Exit",
                color=(100,220,160))

    while True:   # restart loop
        platforms, enemies, gem, key, exit_door = build_level()
        player    = Player(140, 1350)
        camera    = Camera()
        has_gem   = False
        has_key   = False
        won       = False

        # Spawn a star-field background
        stars = [(random.randint(0, WIDTH*3), random.randint(0, 1500)) for _ in range(200)]

        running = True
        while running:
            clock.tick(FPS)

            # ── Events ──
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                    running = False   # restart

            # ── Update ──
            player.update(platforms)
            gem.update()
            key.update()

            for enemy in enemies:
                enemy.update(platforms, player)

            # Player attack hits enemies
            if player.attack.active:
                for enemy in enemies:
                    if enemy.alive and player.attack.rect.colliderect(enemy.rect):
                        enemy.take_damage(1)

            # Gem collection
            if not has_gem and gem.alive and player.rect.colliderect(gem.rect):
                gem.alive = False
                has_gem   = True
                key.alive = True   # key spawns!

            # Key collection
            if has_gem and key.alive and player.rect.colliderect(key.rect):
                key.alive     = False
                has_key       = True
                exit_door.locked = False

            # Exit
            if has_key and player.rect.colliderect(exit_door.rect):
                won     = True
                running = False

            # Death
            if player.dead:
                running = False

            # Fell off world
            if player.rect.top > 1500:
                player.dead = True
                running = False

            # ── Camera ──
            camera.update(player.rect)

            # ── Draw ──
            screen.fill(SKY)

            # Stars
            for sx, sy in stars:
                sr = pygame.Rect(sx, sy, 2, 2)
                pr = camera.apply(sr)
                if 0 <= pr.x <= WIDTH and 0 <= pr.y <= HEIGHT:
                    pygame.draw.rect(screen, (80,90,120), pr)

            exit_door.draw(screen, camera)
            for p in platforms:
                p.draw(screen, camera)
            gem.draw(screen, camera)
            key.draw(screen, camera)
            for enemy in enemies:
                enemy.draw(screen, camera)
            player.draw(screen, camera)

            draw_hud(screen, player, has_gem, has_key)
            pygame.display.flip()

        # ── Post-run screen ──
        if won:
            show_screen(screen, "YOU ESCAPED!", "Press any key to play again", color=(100,255,180))
        else:
            show_screen(screen, "YOU DIED", "Press R or any key to restart", color=(220,80,80))


if __name__ == "__main__":
    main()