import pygame
import sys
import math
import random

WIDTH, HEIGHT = 1280, 720
FPS = 60

PLATFORMS = [
    (340, 500, 600, 20),
    (100, 380, 220, 16),
    (960, 380, 220, 16),
    (540, 320, 200, 16),
    (200, 580, 160, 14),
    (920, 580, 160, 14),
]

GRAVITY = 0.65
MAX_FALL = 18
DEATH_ZONE_X = (-300, WIDTH + 300)
DEATH_ZONE_Y = HEIGHT + 200

# ── Paleta base ──────────────────────────────────────────────────────────────
C_WHITE  = (255, 255, 255)
C_YELLOW = (255, 220,  50)
C_ORANGE = (255, 140,  20)
C_RED    = (220,  40,  40)
C_DARK   = (20,   15,  50)
C_HP_BG  = (50,   40,  80)

C_P1      = (60,  140, 255)
C_P1_DARK = (30,   80, 180)
C_P2      = (255,  60,  60)
C_P2_DARK = (180,  30,  30)

# ── Paisagens ─────────────────────────────────────────────────────────────────
LANDSCAPES = {
    "Cosmos": {
        "bg_top":    (8,   5,  30),
        "bg_bot":    (30, 10,  70),
        "plat":      (70, 50, 130),
        "plat_top":  (110, 80, 200),
        "plat_edge": (150, 110, 255),
        "plat_shadow":(20, 10, 50),
        "death_bars":(120, 20,  60),
        "star_color": (200, 180, 255),
        "icon": "✦",
        "desc": "O vazio estelar",
        "accent": (180, 120, 255),
    },
    "Vulcão": {
        "bg_top":    (30,  5,   5),
        "bg_bot":    (80, 20,   0),
        "plat":      (100, 40,  10),
        "plat_top":  (200, 80,  20),
        "plat_edge": (255, 120,  30),
        "plat_shadow":(40, 10,   5),
        "death_bars":(200, 50,   0),
        "star_color": (255, 160,  60),
        "icon": "🌋",
        "desc": "Magma e cinzas",
        "accent": (255, 100, 20),
    },
    "Oceano": {
        "bg_top":    (0,  20,  60),
        "bg_bot":    (0,  60, 110),
        "plat":      (10,  80, 100),
        "plat_top":  (30, 160, 180),
        "plat_edge": (80, 220, 230),
        "plat_shadow":(0,  30,  60),
        "death_bars":(0,  140, 180),
        "star_color": (140, 230, 255),
        "icon": "🌊",
        "desc": "Abissal e sereno",
        "accent": (0, 200, 220),
    },
    "Floresta": {
        "bg_top":    (5,  20,   5),
        "bg_bot":    (10,  45,  15),
        "plat":      (30,  70,  30),
        "plat_top":  (60, 140,  50),
        "plat_edge": (100, 200,  80),
        "plat_shadow":(10,  30,  10),
        "death_bars":(30, 120,  30),
        "star_color": (150, 255, 120),
        "icon": "🌿",
        "desc": "Anciã e selvagem",
        "accent": (80, 200, 60),
    },
    "Tundra": {
        "bg_top":    (180, 210, 240),
        "bg_bot":    (220, 235, 255),
        "plat":      (160, 190, 220),
        "plat_top":  (220, 240, 255),
        "plat_edge": (255, 255, 255),
        "plat_shadow":(120, 150, 190),
        "death_bars":(100, 160, 220),
        "star_color": (200, 220, 255),
        "icon": "❄",
        "desc": "Gélida e silenciosa",
        "accent": (160, 210, 255),
    },
}

LANDSCAPE_NAMES = list(LANDSCAPES.keys())

# ── Geração de partículas de fundo por paisagem ───────────────────────────────
def make_bg_particles(landscape_name):
    data = LANDSCAPES[landscape_name]
    particles = []
    sc = data["star_color"]
    if landscape_name == "Cosmos":
        for _ in range(140):
            particles.append({
                "type": "star",
                "x": random.randint(0, WIDTH),
                "y": random.randint(0, HEIGHT - 100),
                "size": random.randint(1, 3),
                "alpha_base": random.uniform(0.3, 1.0),
                "phase": random.uniform(0, math.pi * 2),
            })
    elif landscape_name == "Vulcão":
        for _ in range(60):
            particles.append({
                "type": "ember",
                "x": random.randint(0, WIDTH),
                "y": float(random.randint(100, HEIGHT)),
                "vy": random.uniform(-0.8, -0.3),
                "vx": random.uniform(-0.5, 0.5),
                "size": random.randint(1, 3),
                "color": sc,
                "life": random.randint(0, 200),
                "max_life": 200,
            })
    elif landscape_name == "Oceano":
        for _ in range(30):
            particles.append({
                "type": "bubble",
                "x": float(random.randint(0, WIDTH)),
                "y": float(random.randint(100, HEIGHT)),
                "vy": random.uniform(-0.4, -0.15),
                "vx": random.uniform(-0.2, 0.2),
                "size": random.randint(2, 6),
                "color": sc,
                "life": random.randint(0, 300),
                "max_life": 300,
            })
    elif landscape_name == "Floresta":
        for _ in range(50):
            particles.append({
                "type": "firefly",
                "x": float(random.randint(0, WIDTH)),
                "y": float(random.randint(50, HEIGHT - 120)),
                "vx": random.uniform(-0.4, 0.4),
                "vy": random.uniform(-0.2, 0.2),
                "phase": random.uniform(0, math.pi * 2),
                "size": random.randint(2, 4),
                "color": sc,
            })
    elif landscape_name == "Tundra":
        for _ in range(80):
            particles.append({
                "type": "snowflake",
                "x": float(random.randint(0, WIDTH)),
                "y": float(random.randint(-50, HEIGHT)),
                "vy": random.uniform(0.3, 1.0),
                "vx": random.uniform(-0.3, 0.3),
                "size": random.randint(1, 3),
                "color": (200, 220, 255),
                "life": random.randint(0, 400),
                "max_life": 400,
            })
    return particles


def update_bg_particles(particles, landscape_name, tick):
    data = LANDSCAPES[landscape_name]
    sc = data["star_color"]
    for p in particles:
        t = p["type"]
        if t == "star":
            pass  # só animação visual
        elif t in ("ember", "bubble", "snowflake"):
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] += 1
            if p["life"] >= p["max_life"]:
                p["life"] = 0
                p["x"] = float(random.randint(0, WIDTH))
                p["y"] = HEIGHT if t in ("ember", "bubble") else -10
                if t == "snowflake":
                    p["y"] = float(random.randint(-50, -5))
        elif t == "firefly":
            p["phase"] += 0.03
            p["x"] += p["vx"] + math.sin(p["phase"] * 1.3) * 0.4
            p["y"] += p["vy"] + math.cos(p["phase"]) * 0.3
            if p["x"] < 0: p["x"] = WIDTH
            if p["x"] > WIDTH: p["x"] = 0
            if p["y"] < 0: p["y"] = HEIGHT - 150
            if p["y"] > HEIGHT - 80: p["y"] = 50


def draw_bg_particles(surf, particles, landscape_name, tick):
    for p in particles:
        t = p["type"]
        if t == "star":
            alpha = 0.5 + 0.5 * math.sin(tick * 0.03 + p["phase"])
            alpha *= p["alpha_base"]
            sc = LANDSCAPES[landscape_name]["star_color"]
            col = tuple(int(c * alpha) for c in sc)
            pygame.draw.circle(surf, col, (int(p["x"]), int(p["y"])), p["size"])
        elif t == "ember":
            a = 1.0 - p["life"] / p["max_life"]
            sc = p["color"]
            col = (int(sc[0]*a), int(sc[1]*a*0.5), 0)
            pygame.draw.circle(surf, col, (int(p["x"]), int(p["y"])), p["size"])
        elif t == "bubble":
            a = math.sin(math.pi * p["life"] / p["max_life"])
            sc = p["color"]
            col = (int(sc[0]*a*0.6), int(sc[1]*a*0.8), int(sc[2]*a))
            pygame.draw.circle(surf, col, (int(p["x"]), int(p["y"])), p["size"], 1)
        elif t == "firefly":
            a = 0.4 + 0.6 * abs(math.sin(p["phase"] * 2))
            sc = p["color"]
            col = (int(sc[0]*a), int(sc[1]*a), int(sc[2]*a*0.5))
            pygame.draw.circle(surf, col, (int(p["x"]), int(p["y"])), p["size"])
        elif t == "snowflake":
            a = math.sin(math.pi * p["life"] / p["max_life"])
            col = tuple(int(c * a) for c in (200, 220, 255))
            pygame.draw.circle(surf, col, (int(p["x"]), int(p["y"])), p["size"])


# ── Partículas de jogo ────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color, vx=None, vy=None, life=None, size=None):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx if vx is not None else random.uniform(-4, 4)
        self.vy = vy if vy is not None else random.uniform(-6, -1)
        self.life = life if life is not None else random.randint(15, 35)
        self.max_life = self.life
        self.size = size if size is not None else random.uniform(3, 7)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 1

    def draw(self, surf):
        alpha = self.life / self.max_life
        r, g, b = self.color
        col = (int(r * alpha), int(g * alpha), int(b * alpha))
        s = max(1, int(self.size * alpha))
        pygame.draw.circle(surf, col, (int(self.x), int(self.y)), s)


class HitEffect:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.life = 18
        self.max_life = 18

    def update(self):
        self.life -= 1

    def draw(self, surf):
        t = self.life / self.max_life
        r = int(50 * t)
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), r, 3)
        pygame.draw.circle(surf, C_WHITE, (int(self.x), int(self.y)), int(r * 0.5))


# ── Player ────────────────────────────────────────────────────────────────────
class Player:
    W, H = 36, 54

    def __init__(self, x, y, color, dark_color, controls, name):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.dark_color = dark_color
        self.controls = controls
        self.name = name
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.jumps_left = 2
        self.facing = 1
        self.damage = 0
        self.stocks = 3
        self.attack_timer = 0
        self.attack_type = None
        self.attack_hitbox = None
        self.stun_timer = 0
        self.invincible = 0
        self.dodge_timer = 0
        self.dodge_cd = 0
        self.anim_frame = 0
        self.squash_y = 1.0
        self.squash_x = 1.0
        self.particles = []
        self.trail = []

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def handle_input(self, keys):
        if self.stun_timer > 0 or self.dodge_timer > 0:
            return
        left  = self.controls['left']
        right = self.controls['right']
        jump  = self.controls['jump']
        heavy = self.controls['heavy']
        light = self.controls['light']
        dodge = self.controls['dodge']
        acc = 1.2
        top_speed = 6.5
        if keys[left]:
            self.vx = max(self.vx - acc, -top_speed)
            self.facing = -1
        elif keys[right]:
            self.vx = min(self.vx + acc, top_speed)
            self.facing = 1
        else:
            self.vx *= 0.78
        if keys[dodge] and self.dodge_cd <= 0:
            if self.on_ground:
                self.vx = self.facing * 12
                self.dodge_timer = 18
                self.invincible = 18
                self.dodge_cd = 35
            elif self.jumps_left > 0:
                dx = (1 if keys[right] else -1 if keys[left] else self.facing)
                dy = (-1 if keys[jump] else 0)
                mag = math.hypot(dx, dy) or 1
                self.vx = dx / mag * 13
                self.vy = dy / mag * 13
                self.jumps_left -= 1
                self.dodge_timer = 22
                self.invincible = 22
                self.dodge_cd = 35
                for _ in range(12):
                    self.particles.append(Particle(
                        self.x + self.W // 2, self.y + self.H // 2,
                        C_WHITE, random.uniform(-3, 3), random.uniform(-3, 3), 14, 4))
        if self.attack_timer <= 0:
            if keys[heavy]:
                self._start_attack('heavy')
            elif keys[light]:
                self._start_attack('light')

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls['jump']:
                self._do_jump()

    def _do_jump(self):
        if self.stun_timer > 0:
            return
        if self.jumps_left > 0:
            self.vy = -15.5
            self.jumps_left -= 1
            self.squash_y = 0.7
            self.squash_x = 1.3
            for _ in range(8):
                self.particles.append(Particle(
                    self.x + self.W // 2, self.y + self.H,
                    self.color, life=12, vy=random.uniform(0, 2)))

    def _start_attack(self, atype):
        self.attack_type = atype
        self.attack_timer = 18 if atype == 'light' else 28
        w, h = (55, 40) if atype == 'light' else (75, 55)
        kb   = 8 if atype == 'light' else 16
        dmg  = 7 if atype == 'light' else 14
        hx = self.x + self.W + 2 if self.facing == 1 else self.x - w - 2
        hy = self.y + 5
        self.attack_hitbox = {
            'rect': pygame.Rect(int(hx), int(hy), w, h),
            'type': atype, 'knockback': kb, 'active': True, 'damage': dmg,
        }

    def apply_knockback(self, kb_x, kb_y, damage):
        if self.invincible > 0:
            return False
        mult = 1 + self.damage / 80
        self.vx += kb_x * mult
        self.vy += kb_y * mult
        self.damage += damage
        self.stun_timer = int(12 + self.damage / 6)
        self.invincible = 25
        return True

    def update(self, platforms):
        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer == 0:
                self.attack_hitbox = None
                self.attack_type = None
        if self.stun_timer > 0:
            self.stun_timer -= 1
        if self.invincible > 0:
            self.invincible -= 1
        if self.dodge_timer > 0:
            self.dodge_timer -= 1
        if self.dodge_cd > 0:
            self.dodge_cd -= 1
        self.vy = min(self.vy + GRAVITY, MAX_FALL)
        self.x += self.vx
        self.y += self.vy
        prev_on = self.on_ground
        self.on_ground = False
        if self.vy >= 0:
            for px, py, pw, ph in platforms:
                pr = pygame.Rect(px, py, pw, ph)
                if self.rect.colliderect(pr) and self.y + self.H - self.vy <= py + 4:
                    self.y = py - self.H
                    self.vy = 0
                    self.on_ground = True
                    self.jumps_left = 2
                    if not prev_on:
                        self.squash_y = 0.6
                        self.squash_x = 1.4
                    break
        self.squash_y += (1.0 - self.squash_y) * 0.22
        self.squash_x += (1.0 - self.squash_x) * 0.22
        self.trail.append((self.x + self.W // 2, self.y + self.H // 2))
        if len(self.trail) > 8:
            self.trail.pop(0)
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        self.anim_frame = (self.anim_frame + 1) % 60

    def draw(self, surf):
        if self.dodge_timer > 0:
            for i, (tx, ty) in enumerate(self.trail):
                alpha = i / max(len(self.trail), 1)
                r, g, b = self.color
                col = (int(r * alpha * 0.5), int(g * alpha * 0.5), int(b * alpha * 0.5))
                s = int(self.W * 0.4 * alpha)
                if s > 0:
                    pygame.draw.circle(surf, col, (int(tx), int(ty)), s)
        for p in self.particles:
            p.draw(surf)
        if self.invincible > 0 and self.invincible % 4 < 2:
            return
        sx, sy = self.squash_x, self.squash_y
        w = int(self.W * sx)
        h = int(self.H * sy)
        bx = int(self.x + self.W // 2 - w // 2)
        by = int(self.y + self.H - h)
        body_rect = pygame.Rect(bx, by, w, h)
        pygame.draw.rect(surf, self.dark_color, body_rect, border_radius=10)
        inner = body_rect.inflate(-6, -6)
        pygame.draw.rect(surf, self.color, inner, border_radius=8)
        eye_y = by + h // 3
        e_off = 7 if self.facing == 1 else -7
        pygame.draw.circle(surf, C_WHITE, (bx + w // 2 + e_off, eye_y), 5)
        pygame.draw.circle(surf, C_DARK, (bx + w // 2 + e_off + self.facing, eye_y), 3)
        arm_swing = math.sin(self.anim_frame * 0.15) * 8 if abs(self.vx) > 0.5 else 0
        arm_color = C_YELLOW if self.attack_timer > 0 else self.dark_color
        if self.attack_timer > 0:
            arm_swing = 18 * self.facing
        ax = bx + (w if self.facing == 1 else 0)
        ay = by + h // 2
        pygame.draw.line(surf, arm_color, (ax, ay),
                         (ax + int(arm_swing * self.facing), ay - 10), 5)
        leg_swing = int(math.sin(self.anim_frame * 0.2) * 10) if abs(self.vx) > 0.5 else 0
        pygame.draw.line(surf, self.dark_color,
                         (bx + w // 3, by + h),
                         (bx + w // 3 - leg_swing, by + h + 12), 5)
        pygame.draw.line(surf, self.dark_color,
                         (bx + 2 * w // 3, by + h),
                         (bx + 2 * w // 3 + leg_swing, by + h + 12), 5)
        if self.attack_hitbox and self.attack_timer > 5:
            color = C_YELLOW if self.attack_type == 'light' else C_ORANGE
            s = pygame.Surface((self.attack_hitbox['rect'].w, self.attack_hitbox['rect'].h), pygame.SRCALPHA)
            s.fill((*color, 80))
            surf.blit(s, self.attack_hitbox['rect'].topleft)
            pygame.draw.rect(surf, color, self.attack_hitbox['rect'], 2, border_radius=6)

    def is_dead(self):
        return (self.x < DEATH_ZONE_X[0] or self.x > DEATH_ZONE_X[1] or self.y > DEATH_ZONE_Y)

    def respawn(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx = self.vy = 0
        self.attack_timer = 0
        self.attack_hitbox = None
        self.stun_timer = 0
        self.invincible = 90
        self.dodge_timer = 0
        self.damage = 0
        self.particles.clear()
        self.trail.clear()


# ── HUD ───────────────────────────────────────────────────────────────────────
def draw_hud(surf, p1, p2, font_big, font_small):
    pygame.draw.rect(surf, C_DARK, (0, HEIGHT - 90, WIDTH, 90))
    pygame.draw.line(surf, (120, 90, 200), (0, HEIGHT - 90), (WIDTH, HEIGHT - 90), 2)
    for i in range(3):
        col = C_P1 if i < p1.stocks else C_HP_BG
        pygame.draw.circle(surf, col, (120 + i * 28, HEIGHT - 30), 10)
        pygame.draw.circle(surf, C_WHITE, (120 + i * 28, HEIGHT - 30), 10, 2)
    for i in range(3):
        col = C_P2 if i < p2.stocks else C_HP_BG
        pygame.draw.circle(surf, col, (WIDTH - 120 - i * 28, HEIGHT - 30), 10)
        pygame.draw.circle(surf, C_WHITE, (WIDTH - 120 - i * 28, HEIGHT - 30), 10, 2)

    def dmg_color(d):
        if d < 50:  return C_WHITE
        if d < 100: return C_YELLOW
        if d < 150: return C_ORANGE
        return C_RED

    t1 = font_big.render(f"{p1.damage}%", True, dmg_color(p1.damage))
    t2 = font_big.render(f"{p2.damage}%", True, dmg_color(p2.damage))
    surf.blit(t1, (60, HEIGHT - 80))
    surf.blit(t2, (WIDTH - 60 - t2.get_width(), HEIGHT - 80))
    n1 = font_small.render(p1.name, True, C_P1)
    n2 = font_small.render(p2.name, True, C_P2)
    surf.blit(n1, (60, HEIGHT - 92))
    surf.blit(n2, (WIDTH - 60 - n2.get_width(), HEIGHT - 92))
    cw = 300
    cx = WIDTH // 2 - cw // 2
    cy = HEIGHT - 55
    pygame.draw.rect(surf, C_HP_BG, (cx, cy, cw, 14), border_radius=7)
    ratio = p1.damage / max(1, p1.damage + p2.damage + 0.001)
    pygame.draw.rect(surf, C_P1, (cx, cy, int(cw * ratio), 14), border_radius=7)
    pygame.draw.rect(surf, C_P2, (cx + int(cw * ratio), cy, cw - int(cw * ratio), 14), border_radius=7)
    pygame.draw.rect(surf, C_WHITE, (cx, cy, cw, 14), 2, border_radius=7)


# ── Fundo e plataformas dinâmicos ──────────────────────────────────────────────
def draw_background(surf, landscape_name, bg_particles, tick):
    data = LANDSCAPES[landscape_name]
    top = data["bg_top"]
    bot = data["bg_bot"]

    # Gradiente
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(top[0] * (1-t) + bot[0] * t)
        g = int(top[1] * (1-t) + bot[1] * t)
        b = int(top[2] * (1-t) + bot[2] * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

    # Detalhes extras por paisagem
    if landscape_name == "Vulcão":
        # Lava no fundo
        for i in range(0, WIDTH, 60):
            wave = int(math.sin((i * 0.04) + tick * 0.05) * 8)
            pygame.draw.rect(surf, (180, 50, 0), (i, HEIGHT - 100 + wave, 60, 100))
            pygame.draw.ellipse(surf, (220, 80, 10),
                                (i - 5, HEIGHT - 105 + wave, 70, 20))
    elif landscape_name == "Oceano":
        # Ondas suaves
        for i in range(0, WIDTH, 4):
            wave = int(math.sin(i * 0.025 + tick * 0.04) * 10)
            pygame.draw.line(surf, (0, 100, 160),
                             (i, HEIGHT - 95 + wave), (i, HEIGHT - 90 + wave), 3)
    elif landscape_name == "Floresta":
        # Silhueta de árvores
        for i, bx in enumerate(range(-60, WIDTH + 60, 110)):
            h_tree = 80 + (i * 37 % 50)
            ty = HEIGHT - 90 - h_tree
            pygame.draw.rect(surf, (15, 50, 10), (bx + 45, ty + h_tree - 30, 20, 30))
            pygame.draw.polygon(surf, (20, 70, 20),
                                [(bx + 55, ty), (bx + 10, ty + h_tree - 20), (bx + 100, ty + h_tree - 20)])
            pygame.draw.polygon(surf, (30, 90, 25),
                                [(bx + 55, ty + 20), (bx + 5, ty + h_tree), (bx + 105, ty + h_tree)])
    elif landscape_name == "Tundra":
        # Montanhas nevadas
        for i, bx in enumerate(range(-100, WIDTH + 100, 200)):
            h_m = 100 + (i * 53 % 80)
            my = HEIGHT - 90 - h_m
            pygame.draw.polygon(surf, (180, 200, 230),
                                [(bx, HEIGHT - 90), (bx + 100, my), (bx + 200, HEIGHT - 90)])
            pygame.draw.polygon(surf, (230, 240, 255),
                                [(bx + 70, my + 20), (bx + 100, my), (bx + 130, my + 20)])
    elif landscape_name == "Cosmos":
        # Nebulosa suave
        for i in range(3):
            cx = 200 + i * 400
            cy = 150 + i * 80
            r_neb = 80 + i * 30
            neb_surf = pygame.Surface((r_neb * 2, r_neb * 2), pygame.SRCALPHA)
            base_col = [(60, 20, 100), (20, 60, 100), (100, 20, 60)][i]
            pygame.draw.circle(neb_surf, (*base_col, 30), (r_neb, r_neb), r_neb)
            surf.blit(neb_surf, (cx - r_neb, cy - r_neb))

    draw_bg_particles(surf, bg_particles, landscape_name, tick)


def draw_platforms(surf, platforms, landscape_name):
    data = LANDSCAPES[landscape_name]
    C_PLAT       = data["plat"]
    C_PLAT_TOP   = data["plat_top"]
    C_PLAT_EDGE  = data["plat_edge"]
    C_PLAT_SHAD  = data["plat_shadow"]
    for px, py, pw, ph in platforms:
        pygame.draw.rect(surf, C_PLAT_SHAD, (px+4, py+4, pw, ph), border_radius=8)
        pygame.draw.rect(surf, C_PLAT,      (px, py, pw, ph), border_radius=8)
        pygame.draw.rect(surf, C_PLAT_TOP,  (px+4, py, pw-8, 5), border_radius=4)
        pygame.draw.rect(surf, C_PLAT_EDGE, (px, py, pw, ph), 2, border_radius=8)


# ── Telas ─────────────────────────────────────────────────────────────────────
def draw_intro(surf, font_title, font_small):
    surf.fill(C_DARK)
    title = font_title.render("BRAWL CLONE", True, C_YELLOW)
    surf.blit(title, (WIDTH//2 - title.get_width()//2, 60))
    lines = [
        ("JOGADOR 1 (AZUL)", C_P1),
        ("  Mover: A / D", C_WHITE),
        ("  Pular: W  (2x = double jump)", C_WHITE),
        ("  Ataque Leve: F", C_WHITE),
        ("  Ataque Forte: G", C_WHITE),
        ("  Dodge / Air Dash: S", C_WHITE),
        ("", C_WHITE),
        ("JOGADOR 2 (VERMELHO)", C_P2),
        ("  Mover: Seta Esq / Dir", C_WHITE),
        ("  Pular: Seta Cima  (2x = double jump)", C_WHITE),
        ("  Ataque Leve: L", C_WHITE),
        ("  Ataque Forte: K", C_WHITE),
        ("  Dodge / Air Dash: Seta Baixo", C_WHITE),
    ]
    y = 180
    for text, color in lines:
        t = font_small.render(text, True, color)
        surf.blit(t, (WIDTH//2 - 250, y))
        y += 32
    start = font_small.render("Pressione ENTER para escolher a paisagem!", True, C_YELLOW)
    surf.blit(start, (WIDTH//2 - start.get_width()//2, y + 20))


def draw_landscape_select(surf, font_title, font_small, font_big, selected_idx, tick):
    """Tela de seleção de paisagem com preview animado."""
    # Fundo escuro com leve gradiente
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(10 * (1-t) + 30 * t)
        g = int(8  * (1-t) + 15 * t)
        b = int(30 * (1-t) + 60 * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

    title = font_title.render("ESCOLHA A PAISAGEM", True, C_YELLOW)
    surf.blit(title, (WIDTH//2 - title.get_width()//2, 30))

    n = len(LANDSCAPE_NAMES)
    card_w, card_h = 200, 220
    gap = 24
    total_w = n * card_w + (n - 1) * gap
    start_x = WIDTH // 2 - total_w // 2

    for i, name in enumerate(LANDSCAPE_NAMES):
        data = LANDSCAPES[name]
        cx = start_x + i * (card_w + gap)
        cy = 130

        is_sel = (i == selected_idx)
        hover_off = int(math.sin(tick * 0.05) * 4) if is_sel else 0

        # Sombra
        shadow = pygame.Surface((card_w + 10, card_h + 10), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 100))
        surf.blit(shadow, (cx - 3, cy + 6 - hover_off))

        # Card background com gradiente da paisagem
        card = pygame.Surface((card_w, card_h))
        top_c = data["bg_top"]
        bot_c = data["bg_bot"]
        for row in range(card_h):
            t2 = row / card_h
            cr = int(top_c[0]*(1-t2) + bot_c[0]*t2)
            cg = int(top_c[1]*(1-t2) + bot_c[1]*t2)
            cb = int(top_c[2]*(1-t2) + bot_c[2]*t2)
            pygame.draw.line(card, (cr, cg, cb), (0, row), (card_w, row))

        # Mini plataforma decorativa
        plat_col = data["plat"]
        plat_top = data["plat_top"]
        pygame.draw.rect(card, plat_col, (20, card_h - 60, card_w - 40, 10), border_radius=4)
        pygame.draw.rect(card, plat_top, (24, card_h - 60, card_w - 48, 3), border_radius=2)

        # Accent dots (estrelas/partículas decorativas)
        accent = data["accent"]
        for j in range(6):
            dx = 20 + (j * 29 + i * 17) % (card_w - 40)
            dy = 15 + (j * 43 + i * 23) % (card_h - 80)
            pulse = 0.5 + 0.5 * math.sin(tick * 0.04 + j * 1.1)
            col_a = tuple(int(c * pulse) for c in accent)
            pygame.draw.circle(card, col_a, (dx, dy), 2 + (j % 2))

        surf.blit(card, (cx, cy - hover_off))

        # Borda selecionado/normal
        border_col = data["accent"] if is_sel else (80, 70, 100)
        border_w = 3 if is_sel else 1
        pygame.draw.rect(surf, border_col,
                         (cx, cy - hover_off, card_w, card_h),
                         border_w, border_radius=8)

        # Glow quando selecionado
        if is_sel:
            glow = pygame.Surface((card_w + 20, card_h + 20), pygame.SRCALPHA)
            ac = data["accent"]
            pygame.draw.rect(glow, (*ac, 40), (0, 0, card_w + 20, card_h + 20), border_radius=12)
            surf.blit(glow, (cx - 10, cy - hover_off - 10))

        # Ícone
        try:
            icon_surf = font_big.render(data["icon"], True, data["accent"])
        except Exception:
            icon_surf = font_big.render("*", True, data["accent"])
        surf.blit(icon_surf, (cx + card_w//2 - icon_surf.get_width()//2,
                               cy - hover_off + card_h // 2 - 50))

        # Nome
        name_col = data["accent"] if is_sel else C_WHITE
        name_surf = font_small.render(name, True, name_col)
        surf.blit(name_surf, (cx + card_w//2 - name_surf.get_width()//2,
                               cy - hover_off + card_h - 55))

        # Descrição
        desc_surf = font_small.render(data["desc"], True, (180, 170, 200))
        surf.blit(desc_surf, (cx + card_w//2 - desc_surf.get_width()//2,
                               cy - hover_off + card_h - 30))

    # Instruções
    instr = font_small.render("← → para navegar   |   ENTER para confirmar", True, (180, 170, 220))
    surf.blit(instr, (WIDTH//2 - instr.get_width()//2, HEIGHT - 70))

    sel_name = LANDSCAPE_NAMES[selected_idx]
    sel_surf = font_small.render(f"Selecionado: {sel_name}", True, C_YELLOW)
    surf.blit(sel_surf, (WIDTH//2 - sel_surf.get_width()//2, HEIGHT - 40))


def draw_winner(surf, winner, font_title, font_small, win_particles):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surf.blit(overlay, (0, 0))
    for p in win_particles:
        p.update()
        p.draw(surf)
    txt = font_title.render(f"{winner} VENCEU!", True, C_YELLOW)
    surf.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 60))
    sub = font_small.render("R = reiniciar mesmo mapa   |   M = escolher mapa   |   ESC = sair", True, C_WHITE)
    surf.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    surf = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Brawl Clone")
    clock = pygame.time.Clock()

    try:
        font_title = pygame.font.SysFont("Arial Black", 64, bold=True)
        font_big   = pygame.font.SysFont("Arial Black", 44, bold=True)
        font_small = pygame.font.SysFont("Arial", 24)
    except Exception:
        font_title = pygame.font.Font(None, 72)
        font_big   = pygame.font.Font(None, 52)
        font_small = pygame.font.Font(None, 28)

    ctrl1 = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w,
              'light': pygame.K_f, 'heavy': pygame.K_g, 'dodge': pygame.K_s}
    ctrl2 = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP,
              'light': pygame.K_l, 'heavy': pygame.K_k, 'dodge': pygame.K_DOWN}

    def make_players():
        return (Player(300, 300, C_P1, C_P1_DARK, ctrl1, "JOGADOR 1"),
                Player(900, 300, C_P2, C_P2_DARK, ctrl2, "JOGADOR 2"))

    # Estado
    selected_landscape_idx = 0
    current_landscape = LANDSCAPE_NAMES[0]
    bg_particles = make_bg_particles(current_landscape)

    p1, p2 = make_players()
    effects = []
    global_particles = []
    state = "intro"
    winner = None
    win_particles = []
    tick = 0

    def spawn_win_particles(color):
        return [Particle(random.randint(0, WIDTH), random.randint(-50, HEIGHT//2),
                         color, random.uniform(-3, 3), random.uniform(-1, 4),
                         random.randint(60, 120), random.randint(4, 10))
                for _ in range(120)]

    running = True
    while running:
        clock.tick(FPS)
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Intro → seleção
                if state == "intro" and event.key == pygame.K_RETURN:
                    state = "landscape_select"

                # Seleção de paisagem
                elif state == "landscape_select":
                    if event.key == pygame.K_LEFT:
                        selected_landscape_idx = (selected_landscape_idx - 1) % len(LANDSCAPE_NAMES)
                    elif event.key == pygame.K_RIGHT:
                        selected_landscape_idx = (selected_landscape_idx + 1) % len(LANDSCAPE_NAMES)
                    elif event.key == pygame.K_RETURN:
                        current_landscape = LANDSCAPE_NAMES[selected_landscape_idx]
                        bg_particles = make_bg_particles(current_landscape)
                        p1, p2 = make_players()
                        effects.clear()
                        global_particles.clear()
                        state = "game"

                # Jogo
                elif state == "game":
                    p1.process_event(event)
                    p2.process_event(event)

                # Vitória
                elif state == "win":
                    if event.key == pygame.K_r:
                        # Reinicia no mesmo mapa
                        p1, p2 = make_players()
                        effects.clear()
                        global_particles.clear()
                        win_particles.clear()
                        winner = None
                        state = "game"
                    elif event.key == pygame.K_m:
                        # Volta pra seleção de mapa
                        state = "landscape_select"
                        win_particles.clear()
                        effects.clear()
                        global_particles.clear()
                        winner = None

        # Update
        if state == "game":
            keys = pygame.key.get_pressed()
            p1.handle_input(keys)
            p2.handle_input(keys)
            p1.update(PLATFORMS)
            p2.update(PLATFORMS)
            update_bg_particles(bg_particles, current_landscape, tick)

            for attacker, defender in [(p1, p2), (p2, p1)]:
                hb = attacker.attack_hitbox
                if hb and hb['active']:
                    if hb['rect'].colliderect(defender.rect):
                        dx = defender.x - attacker.x
                        dir_x = 1 if dx > 0 else -1
                        hit = defender.apply_knockback(
                            dir_x * hb['knockback'] * 0.7,
                            -hb['knockback'] * 0.5,
                            hb['damage'])
                        if hit:
                            hb['active'] = False
                            ex = int((defender.x + attacker.x + attacker.W) // 2)
                            ey = int((defender.y + attacker.y + attacker.H) // 2)
                            col = C_YELLOW if hb['type'] == 'light' else C_ORANGE
                            effects.append(HitEffect(ex, ey, col))
                            for _ in range(16):
                                global_particles.append(Particle(ex, ey, col))

            for player, other in [(p1, p2), (p2, p1)]:
                if player.is_dead():
                    player.stocks -= 1
                    if player.stocks <= 0:
                        winner = other.name
                        state = "win"
                        win_col = C_P1 if other is p1 else C_P2
                        win_particles = spawn_win_particles(win_col)
                    else:
                        player.respawn(WIDTH // 2, 200)

            for e in effects: e.update()
            effects = [e for e in effects if e.life > 0]
            for p in global_particles: p.update()
            global_particles = [p for p in global_particles if p.life > 0]

        elif state == "landscape_select":
            update_bg_particles(bg_particles, LANDSCAPE_NAMES[selected_landscape_idx], tick)

        # Draw
        if state == "intro":
            draw_intro(surf, font_title, font_small)

        elif state == "landscape_select":
            draw_landscape_select(surf, font_title, font_small, font_big, selected_landscape_idx, tick)

        elif state in ("game", "win"):
            draw_background(surf, current_landscape, bg_particles, tick)
            draw_platforms(surf, PLATFORMS, current_landscape)

            # Barras de morte com cor da paisagem
            bar_col = LANDSCAPES[current_landscape]["death_bars"]
            pygame.draw.rect(surf, bar_col, (0, 0, 6, HEIGHT))
            pygame.draw.rect(surf, bar_col, (WIDTH-6, 0, 6, HEIGHT))

            p1.draw(surf)
            p2.draw(surf)
            for e in effects: e.draw(surf)
            for p in global_particles: p.draw(surf)
            draw_hud(surf, p1, p2, font_big, font_small)

            if state == "win":
                draw_winner(surf, winner, font_title, font_small, win_particles)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()