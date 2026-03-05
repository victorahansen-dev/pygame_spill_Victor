"""
mario_sprites.py  —  pygame sprite loader
Generated automatically. Drop this file next to mario_sprites/

Usage example
-------------
import pygame
from mario_sprites import SpriteSheet

pygame.init()
screen = pygame.display.set_mode((400, 300))
clock  = pygame.time.Clock()

sheet = SpriteSheet("mario_sprites/spritesheet.png",
                    "mario_sprites/spritesheet_meta.json")

# Animations: idle, walk, run, jump, skid, crouch, swim, die
# FPS suggestions: idle=3, walk=8, run=14, swim=8, others=6
anim   = sheet.get_animation("walk")
frame  = 0
timer  = 0
FPS_ANIM = 8   # animation frames per second

running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    timer += dt
    if timer >= 1000 / FPS_ANIM:
        frame = (frame + 1) % len(anim)
        timer = 0

    screen.fill((92, 148, 252))   # sky blue
    screen.blit(anim[frame], (176, 120))
    pygame.display.flip()

pygame.quit()
"""

import pygame
import json
import os

class SpriteSheet:
    """Load all animations from the generated spritesheet."""

    def __init__(self, sheet_path: str, meta_path: str):
        self.sheet = pygame.image.load(sheet_path).convert_alpha()
        with open(meta_path) as f:
            self.meta = json.load(f)

    def get_frame(self, anim: str, index: int) -> pygame.Surface:
        """Return a single pygame.Surface for one frame."""
        info = self.meta[anim][index]
        rect = pygame.Rect(info["x"], info["y"], info["w"], info["h"])
        surf = pygame.Surface((info["w"], info["h"]), pygame.SRCALPHA)
        surf.blit(self.sheet, (0, 0), rect)
        return surf

    def get_animation(self, anim: str) -> list:
        """Return a list of pygame.Surface objects for every frame."""
        return [self.get_frame(anim, i) for i in range(len(self.meta[anim]))]

    @property
    def animations(self) -> list:
        """Names of all available animations."""
        return list(self.meta.keys())


# ── Convenience: load individual PNG files instead of spritesheet ──
def load_frames(folder: str, anim: str) -> list:
    """
    Load individual PNGs from a folder.
    E.g. load_frames("mario_sprites", "walk")
    returns [Surface(walk_0.png), Surface(walk_1.png), ...]
    """
    frames = []
    i = 0
    while True:
        path = os.path.join(folder, f"{anim}_{i}.png")
        if not os.path.exists(path):
            break
        frames.append(pygame.image.load(path).convert_alpha())
        i += 1
    return frames
