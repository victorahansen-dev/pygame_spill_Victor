import pygame  # Importerer pygame-biblioteket for spillutvikling
import sys  # Importerer sys for å avslutte programmet
import math  # Importerer math for matematiske funksjoner som sin og hypot
import random  # Importerer random for tilfeldige tall (stjernefelt)

pygame.init()  # Starter opp alle pygame-moduler

# ── Konstanter ──────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1800, 1000  # Bredde og høyde på spillvinduet i piksler
FPS = 60  # Antall bilder per sekund spillet kjører på
GRAVITY = 0.55  # Tyngdekraftens styrke – legges til vertikal hastighet hver frame
TILE = 48  # Størrelsen på én flis i piksler, brukes som måleenhet

# Farger definert som RGB-tupler
SKY        = (40,  67,  100)  # Bakgrunnsfarge – mørk himmelblå
PLATFORM_C = (60,  90, 140)  # Farge på plattformene
PLAYER_C   = (80, 200, 120)  # Farge på spilleren – grønn
ENEMY_C    = (200,  60,  60)  # Farge på fiender – rød
ITEM_C     = (255, 220,  50)  # Farge på edelstenen – gul
KEY_C      = (255, 180,   0)  # Farge på nøkkelen – oransje-gul
EXIT_C     = (100, 255, 200)  # Farge på utgangsdøren når den er ulåst
HIT_C      = (255, 255, 255)  # Hvit farge brukt ved treff/skade
ATTACK_C   = (255, 120,  40)  # Farge på angrepshitboksen
UI_BG      = (10,  10,  25, 180)  # Bakgrunnsfarge for brukergrensesnittet (med gjennomsiktighet)

screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Oppretter spillvinduet med angitt størrelse
pygame.display.set_caption("Ascent")  # Setter tittelen på vindusrammen
clock = pygame.time.Clock()  # Oppretter en klokke for å styre FPS
font_big   = pygame.font.SysFont("monospace", 32, bold=True)  # Stor font for titler
font_small = pygame.font.SysFont("monospace", 18)  # Liten font for HUD og tekst


# ── Kamera ──────────────────────────────────────────────────────────────────
class Camera:
    def __init__(self):
        self.offset_x = 0  # Horisontal forskyvning av kameraet
        self.offset_y = 0  # Vertikal forskyvning av kameraet

    def apply(self, rect):
        return rect.move(-self.offset_x, -self.offset_y)  # Flytter et rektangel relativt til kameraet for tegning

    def update(self, target):
        self.offset_x = target.centerx - WIDTH  // 2  # Sentrerer kameraet horisontalt på målet
        self.offset_y = target.centery - HEIGHT // 2  # Sentrerer kameraet vertikalt på målet


# ── Plattform ────────────────────────────────────────────────────────────────
class Platform:
    def __init__(self, x, y, w, h=TILE//2):
        self.rect = pygame.Rect(x, y, w, h)  # Oppretter plattformens kollisjonsboks

    def draw(self, surface, cam):
        r = cam.apply(self.rect)  # Beregner plattformens posisjon på skjermen
        pygame.draw.rect(surface, PLATFORM_C, r, border_radius=4)  # Tegner fylt rektangel for plattformen
        pygame.draw.rect(surface, (90, 130, 190), r, 2, border_radius=4)  # Tegner kantlinje rundt plattformen


# ── Samleobjekt (edelstein) ────────────────────────────────────────────────────────
class Gem:
    def __init__(self, x, y):
        self.rect  = pygame.Rect(x, y, 24, 24)  # Kollisjonsboks for edelstenen
        self.alive = True  # Styrer om edelstenen fortsatt er synlig/aktiv
        self.t     = 0  # Tidseller for animasjonen (svingebevegelse)

    def update(self):
        self.t += 0.05  # Øker tidstelleren for å drive svingeanimasjonen fremover

    def draw(self, surface, cam):
        if not self.alive:
            return  # Hopper over tegning hvis edelstenen er samlet inn
        r   = cam.apply(self.rect)  # Beregner skjermposisjon
        bob = int(math.sin(self.t) * 4)  # Beregner vertikal svingeforskyvning med sinusbølge
        cx, cy = r.centerx, r.centery + bob  # Senterpunkt med svingebevegelse
        points = [(cx, cy-12),(cx+10, cy-2),(cx+6, cy+10),(cx-6, cy+10),(cx-10, cy-2)]  # Punkter for femkantet form
        pygame.draw.polygon(surface, ITEM_C, points)  # Tegner fylt femkant
        pygame.draw.polygon(surface, (255,255,180), points, 2)  # Tegner lysere kantlinje


# ── Nøkkel ──────────────────────────────────────────────────────────────────────
class Key:
    def __init__(self, x, y):
        self.rect  = pygame.Rect(x, y, 28, 28)  # Kollisjonsboks for nøkkelen
        self.alive = False  # Nøkkelen er usynlig til edelstenen er samlet inn
        self.t     = 0  # Tidseller for svingeanimasjon

    def update(self):
        if self.alive:
            self.t += 0.04  # Øker animasjonstid kun når nøkkelen er aktiv

    def draw(self, surface, cam):
        if not self.alive:
            return  # Hopper over tegning hvis nøkkelen ikke er aktiv ennå
        r   = cam.apply(self.rect)  # Beregner skjermposisjon
        bob = int(math.sin(self.t) * 5)  # Svingeforskyvning basert på sinusbølge
        cx, cy = r.centerx, r.centery + bob  # Senterpunkt med svingebevegelse
        pygame.draw.circle(surface, KEY_C, (cx, cy-6), 9, 3)  # Tegner nøkkelringen øverst
        pygame.draw.line(surface, KEY_C, (cx, cy+3), (cx, cy+12), 3)  # Tegner nøkkelskaftet
        pygame.draw.line(surface, KEY_C, (cx+3, cy+7), (cx+7, cy+7), 3)  # Tegner første tann på nøkkelen
        pygame.draw.line(surface, KEY_C, (cx+3, cy+10), (cx+6, cy+10), 3)  # Tegner andre tann på nøkkelen


# ── Utgangsdør ────────────────────────────────────────────────────────────────
class Exit:
    def __init__(self, x, y):
        self.rect   = pygame.Rect(x, y, TILE, TILE*2)  # Kollisjonsboks – én flis bred, to fliser høy
        self.locked = True  # Døren er låst til spilleren har nøkkelen

    def draw(self, surface, cam):
        r = cam.apply(self.rect)  # Beregner skjermposisjon
        col = (40, 80, 80) if self.locked else EXIT_C  # Mørk farge hvis låst, lys hvis ulåst
        pygame.draw.rect(surface, col, r, border_radius=6)  # Tegner dørens kropp
        pygame.draw.rect(surface, (200,255,240) if not self.locked else (60,120,120), r, 3, border_radius=6)  # Tegner kantlinje
        label = font_small.render("EXIT" if not self.locked else "LOCKED", True, (200,255,240))  # Lager tekstetikett
        surface.blit(label, (r.centerx - label.get_width()//2, r.centery - label.get_height()//2))  # Tegner etiketten sentrert på døren


# ── Angrepshitboks ────────────────────────────────────────────────────────────
class AttackHitbox:
    def __init__(self):
        self.rect    = pygame.Rect(0,0,50,40)  # Størrelsen på angrepshitboksen
        self.active  = False  # Angrepet er ikke aktivt som standard
        self.timer   = 0  # Teller ned hvor lenge angrepet varer
        self.duration = 14  # Angrepet varer i 14 frames

    def trigger(self, player_rect, facing):
        self.active = True  # Aktiverer angrepet
        self.timer  = self.duration  # Nullstiller varighetstimer
        if facing == 1:
            self.rect.midleft = player_rect.midright  # Plasserer hitboks til høyre for spilleren
        else:
            self.rect.midright = player_rect.midleft  # Plasserer hitboks til venstre for spilleren

    def update(self):
        if self.active:
            self.timer -= 1  # Teller ned angrepstimeren
            if self.timer <= 0:
                self.active = False  # Deaktiverer angrepet når timeren går ut

    def draw(self, surface, cam):
        if not self.active:
            return  # Tegner ingenting hvis angrepet ikke er aktivt
        r = cam.apply(self.rect)  # Beregner skjermposisjon
        s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)  # Lager en gjennomsiktig overflate
        s.fill((255, 120, 40, 120))  # Fyller med semi-transparent oransje farge
        surface.blit(s, r.topleft)  # Tegner den gjennomsiktige overflaten
        pygame.draw.rect(surface, ATTACK_C, r, 2, border_radius=4)  # Tegner kantlinjen rundt hitboksen


# ── Spiller ───────────────────────────────────────────────────────────────────
class Player:
    W, H = 32, 44  # Spillerens bredde og høyde i piksler

    def __init__(self, x, y):
        self.rect       = pygame.Rect(x, y, self.W, self.H)  # Spillerens kollisjonsboks
        self.vel_x      = 0.0  # Horisontal hastighet
        self.vel_y      = 0.0  # Vertikal hastighet (positiv = ned)
        self.on_ground  = False  # Holder styr på om spilleren står på bakken
        self.facing     = 1  # Retning spilleren ser: 1 = høyre, -1 = venstre
        self.hp         = 5  # Spillerens nåværende helsepoeng
        self.max_hp     = 5  # Spillerens maksimale helsepoeng
        self.inv_timer  = 0  # Uovervinnelighetframes etter å ha blitt truffet
        self.attack     = AttackHitbox()  # Angrepshitboks-objektet til spilleren
        self.atk_cd     = 0  # Nedkjølingstimer mellom angrep
        self.dead       = False  # Flagg for om spilleren er død
        self.anim_t     = 0  # Animasjonsteller for bevegelseanimasjon

    def handle_input(self):
        keys = pygame.key.get_pressed()  # Henter alle tastaturknapper som er trykket ned
        speed = 4.5  # Horisontal bevegelseshastighet
        self.vel_x = 0  # Nullstiller horisontal hastighet hvert frame
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.vel_x = -speed  # Beveger spilleren til venstre
            self.facing = -1  # Setter retningen til venstre
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x =  speed  # Beveger spilleren til høyre
            self.facing =  1  # Setter retningen til høyre
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = -13  # Gir spilleren oppoverhastighet for hopp
            self.on_ground = False  # Markerer at spilleren ikke lenger er på bakken

        # Angrep
        if keys[pygame.K_z] or keys[pygame.K_j]:
            if self.atk_cd == 0:
                self.attack.trigger(self.rect, self.facing)  # Utløser angrep i spillerens retning
                self.atk_cd = 22  # Setter nedkjølingstimer for neste angrep

    def update(self, platforms):
        if self.dead:
            return  # Stopper oppdatering hvis spilleren er død

        self.handle_input()  # Behandler tastetrykk
        self.vel_y += GRAVITY  # Legger til tyngdekraft på vertikal hastighet
        self.anim_t += 1  # Øker animasjonsteller

        # Beveg horisontalt
        self.rect.x += int(self.vel_x)  # Oppdaterer horisontal posisjon
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_x > 0:
                    self.rect.right = p.rect.left  # Stopper bevegelse til høyre ved kollisjon
                elif self.vel_x < 0:
                    self.rect.left  = p.rect.right  # Stopper bevegelse til venstre ved kollisjon

        # Beveg vertikalt
        self.on_ground = False  # Antar at spilleren ikke er på bakken
        self.rect.y += int(self.vel_y)  # Oppdaterer vertikal posisjon
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:
                    self.rect.bottom = p.rect.top  # Lander på toppen av plattformen
                    self.on_ground   = True  # Bekrefter at spilleren er på bakken
                    self.vel_y       = 0  # Nullstiller vertikal hastighet ved landing
                elif self.vel_y < 0:
                    self.rect.top    = p.rect.bottom  # Stopper spilleren ved hodekolisjonen med undersiden
                    self.vel_y       = 0  # Nullstiller vertikal hastighet

        # Timere
        if self.inv_timer  > 0: self.inv_timer  -= 1  # Teller ned uovervinnelighetframes
        if self.atk_cd     > 0: self.atk_cd     -= 1  # Teller ned angrepsnedkjøling
        self.attack.update()  # Oppdaterer angrepshitboksens tilstand

        # Oppdaterer hitboksens posisjon hvis angrepet fortsatt er aktivt
        if self.attack.active:
            if self.facing == 1:
                self.attack.rect.midleft  = self.rect.midright  # Holder hitboksen til høyre for spilleren
            else:
                self.attack.rect.midright = self.rect.midleft  # Holder hitboksen til venstre for spilleren

    def take_damage(self, amount=1):
        if self.inv_timer > 0:
            return  # Ignorerer skade mens spilleren er uovervinnelig
        self.hp -= amount  # Trekker fra helsepoeng
        self.inv_timer = 50  # Starter uovervinnelighetstimer (50 frames)
        if self.hp <= 0:
            self.dead = True  # Markerer spilleren som død

    def draw(self, surface, cam):
        r = cam.apply(self.rect)  # Beregner skjermposisjon

        # Blink hvit når uovervinnelig
        if self.inv_timer > 0 and (self.inv_timer // 4) % 2 == 0:
            col = HIT_C  # Hvit farge under blinkeffekt
        else:
            col = PLAYER_C  # Normal spillerfarge

        # Kropp
        pygame.draw.rect(surface, col, r, border_radius=6)  # Tegner spillerens kropp

        # Øye
        eye_x = r.right - 8 if self.facing == 1 else r.left + 8  # Plasserer øyet basert på retning
        pygame.draw.circle(surface, (20,20,40), (eye_x, r.top+14), 5)  # Tegner det mørke pupillen
        pygame.draw.circle(surface, (255,255,255), (eye_x, r.top+14), 2)  # Tegner hvitt øyeglans

        # Ben (enkel ganganimasjon)
        leg_off = int(math.sin(self.anim_t * 0.25) * 6) if abs(self.vel_x) > 0.1 else 0  # Beregner benforskyvning ved bevegelse
        pygame.draw.line(surface, (50,160,90), (r.centerx-6, r.bottom), (r.centerx-6+leg_off, r.bottom+8), 3)  # Tegner venstre ben
        pygame.draw.line(surface, (50,160,90), (r.centerx+6, r.bottom), (r.centerx+6-leg_off, r.bottom+8), 3)  # Tegner høyre ben

        self.attack.draw(surface, cam)  # Tegner angrepshitboksen hvis aktiv


# ── Fiende ────────────────────────────────────────────────────────────────────
class Enemy:
    W, H = 34, 44  # Fiendens bredde og høyde i piksler
    PATROL_SPEED  = 1.8  # Hastighet under patruljering
    CHASE_SPEED   = 3.2  # Hastighet under forfølgelse av spilleren
    DETECT_RANGE  = 220  # Avstand der fienden begynner å forfølge spilleren
    ATTACK_RANGE  = 55   # Avstand der fienden angriper spilleren
    ATTACK_CD     = 70   # Frames mellom hvert angrep

    def __init__(self, x, y, patrol_left, patrol_right):
        self.rect          = pygame.Rect(x, y, self.W, self.H)  # Fiendens kollisjonsboks
        self.vel_y         = 0.0  # Vertikal hastighet
        self.facing        = 1  # Retning: 1 = høyre, -1 = venstre
        self.patrol_left   = patrol_left  # Venstre grense for patruljering
        self.patrol_right  = patrol_right  # Høyre grense for patruljering
        self.state         = "patrol"  # Nåværende tilstand: patrol, chase eller attack
        self.atk_cd        = 0  # Nedkjølingstimer for angrep
        self.hp            = 3  # Fiendens helsepoeng
        self.alive         = True  # Flagg for om fienden lever
        self.hit_flash     = 0  # Timer for hvit blinkeffekt når fienden tar skade
        self.anim_t        = 0  # Animasjonsteller

    def update(self, platforms, player):
        if not self.alive:
            return  # Stopper oppdatering hvis fienden er død

        self.vel_y += GRAVITY  # Legger til tyngdekraft
        dx = player.rect.centerx - self.rect.centerx  # Horisontal avstand til spilleren
        dy = player.rect.centery - self.rect.centery  # Vertikal avstand til spilleren
        dist = math.hypot(dx, dy)  # Beregner total avstand til spilleren

        # Tilstandsmaskin – bestemmer fiendens oppførsel
        if dist < self.ATTACK_RANGE:
            self.state = "attack"  # Nær nok til å angripe
        elif dist < self.DETECT_RANGE:
            self.state = "chase"  # Innenfor deteksjonsrekkevidde – forfølger
        else:
            self.state = "patrol"  # Utenfor rekkevidde – patruljer

        # Bevegelse basert på tilstand
        if self.state == "patrol":
            self.rect.x += self.PATROL_SPEED * self.facing  # Beveger seg i patruljens retning
            if self.rect.right >= self.patrol_right or self.rect.left <= self.patrol_left:
                self.facing *= -1  # Snur retning ved patruljegrensene
        elif self.state == "chase":
            move = self.CHASE_SPEED if dx > 0 else -self.CHASE_SPEED  # Beveger seg mot spilleren
            self.rect.x += move  # Oppdaterer horisontal posisjon
            self.facing = 1 if dx > 0 else -1  # Snur mot spillerens retning
        elif self.state == "attack":
            self.facing = 1 if dx > 0 else -1  # Ser mot spilleren
            if self.atk_cd == 0:
                player.take_damage(1)  # Påfører spilleren skade
                self.atk_cd = self.ATTACK_CD  # Nullstiller angrepsnedkjølingen

        if self.atk_cd     > 0: self.atk_cd  -= 1  # Teller ned angrepsnedkjøling
        if self.hit_flash  > 0: self.hit_flash -= 1  # Teller ned blinkeffekttimer
        self.anim_t += 1  # Øker animasjonsteller

        # Tyngdekraft og plattformkollisjon
        self.rect.y += int(self.vel_y)  # Oppdaterer vertikal posisjon
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:
                    self.rect.bottom = p.rect.top  # Lander på plattformens topp
                    self.vel_y = 0  # Nullstiller vertikal hastighet
                elif self.vel_y < 0:
                    self.rect.top = p.rect.bottom  # Stopper ved kollisjon med undersiden
                    self.vel_y = 0  # Nullstiller vertikal hastighet

    def take_damage(self, amount=1):
        self.hp -= amount  # Trekker fra helsepoeng
        self.hit_flash = 10  # Starter blinkeffekt i 10 frames
        if self.hp <= 0:
            self.alive = False  # Markerer fienden som død

    def draw(self, surface, cam):
        if not self.alive:
            return  # Tegner ikke døde fiender
        r   = cam.apply(self.rect)  # Beregner skjermposisjon
        col = HIT_C if self.hit_flash > 0 else ENEMY_C  # Hvit ved treff, ellers rød

        pygame.draw.rect(surface, col, r, border_radius=5)  # Tegner fiendens kropp

        # Sinte øyne
        eye_x = r.right-8 if self.facing==1 else r.left+8  # Øyets posisjon basert på retning
        pygame.draw.circle(surface, (20,0,0),   (eye_x, r.top+14), 5)  # Tegner mørk pupill
        pygame.draw.circle(surface, (255,80,80),(eye_x, r.top+14), 2)  # Tegner rødt øyeglans

        # Ben
        leg_off = int(math.sin(self.anim_t*0.2)*5) if self.state != "attack" else 0  # Benforskyvning under bevegelse
        pygame.draw.line(surface, (160,40,40),(r.centerx-6,r.bottom),(r.centerx-6+leg_off,r.bottom+8),3)  # Venstre ben
        pygame.draw.line(surface, (160,40,40),(r.centerx+6,r.bottom),(r.centerx+6-leg_off,r.bottom+8),3)  # Høyre ben

        # Tilstandsindikator over hodet
        if self.state == "chase":
            pygame.draw.circle(surface, (255,200,0),(r.centerx, r.top-10),5)  # Gul sirkel ved forfølgelse
        elif self.state == "attack":
            pygame.draw.circle(surface, (255,50,50),(r.centerx, r.top-10),6)  # Rød sirkel ved angrep

        # Helsemåler
        bar_w = self.rect.w  # Målerens bredde er lik fiendens bredde
        filled = int(bar_w * self.hp / 3)  # Beregner fylt del basert på gjenværende HP
        pygame.draw.rect(surface, (80,0,0),   (r.left, r.top-8, bar_w, 5))  # Tegner mørk bakgrunn
        pygame.draw.rect(surface, (220,60,60),(r.left, r.top-8, filled, 5))  # Tegner fylt del av helsemåleren


# ── Nivåbygger ─────────────────────────────────────────────────────────────────
def build_level():
    """Returnerer (plattformer, fiender, edelstein, nøkkel, utgangsdør)"""
    platforms = []  # Tom liste som fylles med plattformobjekter
    ground_y  = 1400  # Y-posisjon for bakkenivået

    # Bakkefliser
    for gx in range(-200, 2000, TILE*3):
        platforms.append(Platform(gx, ground_y, TILE*3))  # Legger til bakkefliser langs hele bunnen

    # Stigende plattformer (tårnet)
    layout = [
        # (x,   y,    bredde)
        (100,  1280,  200),
        (320,  1160,  160),
        (520,  1040,  180),
        (260,   920,  200),
        (480,   800,  160),
        (180,   680,  200),
        (420,   560,  180),
        (120,   440,  200),
        (380,   320,  160),
        (200,   200,  220),   # Plattform nær toppen med edelstein
        (400,    80,  160),   # Toppplattform med utgang
    ]
    for x, y, w in layout:
        platforms.append(Platform(x, y, w))  # Legger til hver plattform fra layoutlisten

    # Fiender (x, y, patrulje_venstre, patrulje_høyre)
    enemies = [
        Enemy(200,  ground_y - Enemy.H, 100, 400),  # Fiende på bakkenivå
        Enemy(350,  1240 - Enemy.H,     320, 520),  # Fiende på andre plattform
        Enemy(550,  1000 - Enemy.H,     520, 700),  # Fiende på tredje plattform
        Enemy(300,   840 - Enemy.H,     260, 480),  # Fiende på fjerde plattform
        Enemy(220,   620 - Enemy.H,     180, 380),  # Fiende på femte plattform
        Enemy(440,   500 - Enemy.H,     380, 620),  # Fiende på sjette plattform
        Enemy(250,   160 - Enemy.H,     200, 420),  # Fiende nær toppen
    ]

    gem       = Gem(270, 165)          # Edelstenen plasseres på nest øverste plattform
    key       = Key(440,  45)          # Nøkkelen plasseres på toppplattformen
    exit_door = Exit(490,  80 - TILE*2)  # Utgangsdøren plasseres på toppplattformen

    return platforms, enemies, gem, key, exit_door  # Returnerer alle spillobjekter


# ── HUD ──────────────────────────────────────────────────────────────────────
def draw_hud(surface, player, has_gem, has_key):
    # Helsemåler
    for i in range(player.max_hp):
        col = (80,200,120) if i < player.hp else (40,40,60)  # Grønn for aktiv HP, mørk for tapt HP
        pygame.draw.rect(surface, col, (14 + i*28, 14, 22, 22), border_radius=4)  # Tegner helsefirkant
        pygame.draw.rect(surface, (255,255,255), (14+i*28, 14, 22, 22), 1, border_radius=4)  # Hvit kantlinje

    # Inventarrad
    label = font_small.render("GEM", True, ITEM_C if has_gem else (60,60,80))  # Lys tekst hvis samlet, mørk ellers
    surface.blit(label, (14, 44))  # Tegner edelstein-indikatoren
    label2 = font_small.render("KEY", True, KEY_C if has_key else (60,60,80))  # Lys tekst hvis samlet, mørk ellers
    surface.blit(label2, (70, 44))  # Tegner nøkkel-indikatoren

    # Kontrolltips
    hint = font_small.render("WASD/Arrows: move   SPACE/W: jump   Z/J: attack", True, (80,100,130))  # Lager kontrolltekst
    surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT-26))  # Tegner tips sentrert nederst på skjermen


# ── Spilltilstander ───────────────────────────────────────────────────────────
def show_screen(surface, title, subtitle, color=(180,230,180)):
    surface.fill(SKY)  # Fyller bakgrunnen med himmelfargen
    t  = font_big.render(title,    True, color)  # Lager titteloverflate med stor skrift
    s  = font_small.render(subtitle, True, (120,160,180))  # Lager undertitteloverflate med liten skrift
    surface.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 40))  # Tegner tittel sentrert på skjermen
    surface.blit(s, (WIDTH//2 - s.get_width()//2, HEIGHT//2 + 10))  # Tegner undertittel under tittelen
    pygame.display.flip()  # Oppdaterer skjermen med det som er tegnet
    waiting = True  # Flagg for å vente på tastetrykk
    while waiting:
        clock.tick(FPS)  # Begrenser løkken til FPS
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()  # Avslutter programmet ved lukking av vindu
            if e.type == pygame.KEYDOWN:
                waiting = False  # Avslutter venteløkken ved tastetrykk


# ── Hovedløkke ─────────────────────────────────────────────────────────────────
def main():
    show_screen(screen, "ASCENT",
                "Collect the Gem  →  Grab the Key  →  Reach the Exit",
                color=(100,220,160))  # Viser startskjermen

    while True:   # Ytre løkke for å starte spillet på nytt
        platforms, enemies, gem, key, exit_door = build_level()  # Bygger nivået og henter alle objekter
        player    = Player(140, 1350)  # Oppretter spilleren nær bunnen av nivået
        camera    = Camera()  # Oppretter kameraobjektet
        has_gem   = False  # Spilleren har ikke edelstenen ennå
        has_key   = False  # Spilleren har ikke nøkkelen ennå
        won       = False  # Spilleren har ikke vunnet ennå

        # Genererer stjernefelt i bakgrunnen
        stars = [(random.randint(0, WIDTH*3), random.randint(0, 1500)) for _ in range(200)]  # 200 tilfeldige stjernepunkter

        running = True  # Flagg for å holde spilløkken aktiv
        while running:
            clock.tick(FPS)  # Begrenser oppdateringsfrekvensen til FPS

            # ── Hendelser ──
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()  # Avslutter programmet
                if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                    running = False  # Restarter spillet ved trykk på R

            # ── Oppdatering ──
            player.update(platforms)  # Oppdaterer spillerens posisjon og logikk
            gem.update()  # Oppdaterer edelsteinens animasjon
            key.update()  # Oppdaterer nøkkelens animasjon

            for enemy in enemies:
                enemy.update(platforms, player)  # Oppdaterer hver fiendes AI og fysikk

            # Sjekker om spillerens angrep treffer fiender
            if player.attack.active:
                for enemy in enemies:
                    if enemy.alive and player.attack.rect.colliderect(enemy.rect):
                        enemy.take_damage(1)  # Påfører fienden skade ved treff

            # Innsamling av edelstein
            if not has_gem and gem.alive and player.rect.colliderect(gem.rect):
                gem.alive = False  # Fjerner edelstenen fra banen
                has_gem   = True  # Markerer at spilleren har samlet edelstenen
                key.alive = True  # Aktiverer nøkkelen på toppplattformen

            # Innsamling av nøkkel
            if has_gem and key.alive and player.rect.colliderect(key.rect):
                key.alive     = False  # Fjerner nøkkelen fra banen
                has_key       = True  # Markerer at spilleren har nøkkelen
                exit_door.locked = False  # Låser opp utgangsdøren

            # Sjekker om spilleren når utgangen
            if has_key and player.rect.colliderect(exit_door.rect):
                won     = True  # Markerer at spilleren har vunnet
                running = False  # Avslutter spilløkken

            # Sjekker om spilleren er død
            if player.dead:
                running = False  # Avslutter spilløkken

            # Sjekker om spilleren falt utenfor verden
            if player.rect.top > 1500:
                player.dead = True  # Markerer spilleren som død
                running = False  # Avslutter spilløkken

            # ── Kamera ──
            camera.update(player.rect)  # Sentrerer kameraet på spilleren

            # ── Tegning ──
            screen.fill(SKY)  # Fyller bakgrunnen med himmelfargen

            # Tegner stjerner
            for sx, sy in stars:
                sr = pygame.Rect(sx, sy, 2, 2)  # Lager et lite rektangel for hver stjerne
                pr = camera.apply(sr)  # Beregner stjernens skjermposisjon
                if 0 <= pr.x <= WIDTH and 0 <= pr.y <= HEIGHT:
                    pygame.draw.rect(screen, (80,90,120), pr)  # Tegner stjernen hvis den er synlig

            exit_door.draw(screen, camera)  # Tegner utgangsdøren
            for p in platforms:
                p.draw(screen, camera)  # Tegner hver plattform
            gem.draw(screen, camera)  # Tegner edelstenen
            key.draw(screen, camera)  # Tegner nøkkelen
            for enemy in enemies:
                enemy.draw(screen, camera)  # Tegner hver fiende
            player.draw(screen, camera)  # Tegner spilleren

            draw_hud(screen, player, has_gem, has_key)  # Tegner HUD øverst på skjermen
            pygame.display.flip()  # Oppdaterer skjermen med alt som er tegnet

        # ── Skjerm etter spillslutt ──
        if won:
            show_screen(screen, "YOU ESCAPED!", "Press any key to play again", color=(100,255,180))  # Viser vinnskjerm
        else:
            show_screen(screen, "YOU DIED", "Press R or any key to restart", color=(220,80,80))  # Viser dødsskjerm


if __name__ == "__main__":
    main()  # Starter spillet når filen kjøres direkte