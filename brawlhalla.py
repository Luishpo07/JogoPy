import pygame
import sys
import math
import random
import os


def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


def cc(*args):
    return tuple(clamp(v) for v in args)


WIDTH, HEIGHT = 1280, 720
FPS = 60

PLATFORMS = [
    (290, 350, 700, 20)
]

GRAVITY = 0.65
MAX_FALL = 18
DEATH_ZONE_X = (-300, WIDTH + 300)
DEATH_ZONE_Y = HEIGHT + 200

C_WHITE  = (255, 255, 255)
C_YELLOW = (255, 220, 50)
C_ORANGE = (255, 140, 20)
C_RED    = (220, 40, 40)
C_DARK   = (20, 15, 50)
C_HP_BG  = (50, 40, 80)

C_P1      = (60, 140, 255)
C_P1_DARK = (30, 80, 180)
C_P2      = (255, 60, 60)
C_P2_DARK = (180, 30, 30)

CHARACTERS = [
    {
        "name": "TITAN",
        "color": (60, 140, 255),
        "dark_color": (30, 80, 180),
        "icon": "🛡",
        "desc": "Tanque Inabalável",
        "stats": {"força": 6, "velocidade": 3, "pulo": 4, "defesa": 9},
        "ability": "Super Armadura",
        "special_color": (100, 180, 255),
        "speed": 5.0,
        "jump_power": -13.0,
        "weight": 1.4,
        "light_dmg": 6, "heavy_dmg": 18, "light_kb": 6, "heavy_kb": 20,
        "accent": (150, 210, 255),
    },
    {
        "name": "PHANTOM",
        "color": (180, 60, 255),
        "dark_color": (100, 20, 160),
        "icon": "👻",
        "desc": "Assassino das Sombras",
        "stats": {"força": 7, "velocidade": 9, "pulo": 8, "defesa": 3},
        "ability": "Teletransporte",
        "special_color": (220, 100, 255),
        "speed": 8.5,
        "jump_power": -16.5,
        "weight": 0.75,
        "light_dmg": 8, "heavy_dmg": 12, "light_kb": 9, "heavy_kb": 14,
        "accent": (200, 140, 255),
    },
    {
        "name": "INFERNO",
        "color": (255, 80, 20),
        "dark_color": (160, 40, 0),
        "icon": "🔥",
        "desc": "Devastador de Chamas",
        "stats": {"força": 9, "velocidade": 6, "pulo": 5, "defesa": 5},
        "ability": "Rastro de Fogo",
        "special_color": (255, 180, 40),
        "speed": 6.5,
        "jump_power": -14.5,
        "weight": 1.0,
        "light_dmg": 9, "heavy_dmg": 20, "light_kb": 10, "heavy_kb": 22,
        "accent": (255, 160, 60),
    },
    {
        "name": "VORTEX",
        "color": (0, 210, 180),
        "dark_color": (0, 120, 100),
        "icon": "🌀",
        "desc": "Mestre do Vento",
        "stats": {"força": 5, "velocidade": 8, "pulo": 10, "defesa": 4},
        "ability": "Rajada Aérea",
        "special_color": (100, 255, 220),
        "speed": 7.5,
        "jump_power": -17.5,
        "weight": 0.8,
        "light_dmg": 7, "heavy_dmg": 11, "light_kb": 12, "heavy_kb": 16,
        "accent": (80, 240, 200),
    },
    {
        "name": "GOLEM",
        "color": (160, 120, 60),
        "dark_color": (80, 60, 20),
        "icon": "🪨",
        "desc": "Força da Terra",
        "stats": {"força": 10, "velocidade": 2, "pulo": 2, "defesa": 8},
        "ability": "Terremoto",
        "special_color": (200, 170, 90),
        "speed": 3.5,
        "jump_power": -11.0,
        "weight": 1.8,
        "light_dmg": 10, "heavy_dmg": 24, "light_kb": 7, "heavy_kb": 26,
        "accent": (210, 180, 100),
    },
]

LANDSCAPES = {
    "Cosmos": {
        "plat": (70, 50, 130),
        "plat_top": (110, 80, 200),
        "plat_edge": (150, 110, 255),
        "plat_shadow": (20, 10, 50),
        "death_bars": (120, 20, 60),
        "icon": "✦",
        "desc": "O vazio estelar",
        "accent": (180, 120, 255),
    },
    "Vulcão": {
        "plat": (100, 40, 10),
        "plat_top": (200, 80, 20),
        "plat_edge": (255, 120, 30),
        "plat_shadow": (40, 10, 5),
        "death_bars": (200, 50, 0),
        "icon": "🌋",
        "desc": "Magma e cinzas",
        "accent": (255, 100, 20),
    },
    "Oceano": {
        "plat": (10, 80, 100),
        "plat_top": (30, 160, 180),
        "plat_edge": (80, 220, 230),
        "plat_shadow": (0, 30, 60),
        "death_bars": (0, 140, 180),
        "icon": "🌊",
        "desc": "Abissal e sereno",
        "accent": (0, 200, 220),
    },
    "Floresta": {
        "plat": (30, 70, 30),
        "plat_top": (60, 140, 50),
        "plat_edge": (100, 200, 80),
        "plat_shadow": (10, 30, 10),
        "death_bars": (30, 120, 30),
        "icon": "🌿",
        "desc": "Anciã e selvagem",
        "accent": (80, 200, 60),
    },
    "Tundra": {
        "plat": (160, 190, 220),
        "plat_top": (220, 240, 255),
        "plat_edge": (255, 255, 255),
        "plat_shadow": (120, 150, 190),
        "death_bars": (100, 160, 220),
        "icon": "❄",
        "desc": "Gélida e silenciosa",
        "accent": (160, 210, 255),
    },
}

LANDSCAPE_NAMES = list(LANDSCAPES.keys())


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


class Player:
    W, H = 36, 54

    def __init__(self, x, y, char_data, controls, player_num):
        self.x = float(x)
        self.y = float(y)
        self.color = char_data["color"]
        self.dark_color = char_data["dark_color"]
        self.special_color = char_data["special_color"]
        self.controls = controls
        self.name = char_data["name"]
        self.player_num = player_num
        self.top_speed = char_data["speed"]
        self.jump_power = char_data["jump_power"]
        self.weight = char_data["weight"]
        self.light_dmg = char_data["light_dmg"]
        self.heavy_dmg = char_data["heavy_dmg"]
        self.light_kb = char_data["light_kb"]
        self.heavy_kb = char_data["heavy_kb"]
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

        left = self.controls["left"]
        right = self.controls["right"]
        jump = self.controls["jump"]
        heavy = self.controls["heavy"]
        light = self.controls["light"]
        dodge = self.controls["dodge"]

        acc = 1.2

        if keys[left]:
            self.vx = max(self.vx - acc, -self.top_speed)
            self.facing = -1
        elif keys[right]:
            self.vx = min(self.vx + acc, self.top_speed)
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
                dx = 1 if keys[right] else -1 if keys[left] else self.facing
                dy = -1 if keys[jump] else 0
                mag = math.hypot(dx, dy) or 1
                self.vx = dx / mag * 13
                self.vy = dy / mag * 13
                self.jumps_left -= 1
                self.dodge_timer = 22
                self.invincible = 22
                self.dodge_cd = 35
                for _ in range(12):
                    self.particles.append(
                        Particle(
                            self.x + self.W // 2,
                            self.y + self.H // 2,
                            C_WHITE,
                            random.uniform(-3, 3),
                            random.uniform(-3, 3),
                            14,
                            4,
                        )
                    )

        if self.attack_timer <= 0:
            if keys[heavy]:
                self._start_attack("heavy")
            elif keys[light]:
                self._start_attack("light")

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls["jump"]:
                self._do_jump()

    def _do_jump(self):
        if self.stun_timer > 0:
            return
        if self.jumps_left > 0:
            self.vy = self.jump_power
            self.jumps_left -= 1
            self.squash_y = 0.7
            self.squash_x = 1.3
            for _ in range(8):
                self.particles.append(
                    Particle(
                        self.x + self.W // 2,
                        self.y + self.H,
                        self.color,
                        life=12,
                        vy=random.uniform(0, 2),
                    )
                )

    def _start_attack(self, atype):
        self.attack_type = atype
        self.attack_timer = 18 if atype == "light" else 28
        w, h = (55, 40) if atype == "light" else (75, 55)
        kb = self.light_kb if atype == "light" else self.heavy_kb
        dmg = self.light_dmg if atype == "light" else self.heavy_dmg
        hx = self.x + self.W + 2 if self.facing == 1 else self.x - w - 2
        hy = self.y + 5
        self.attack_hitbox = {
            "rect": pygame.Rect(int(hx), int(hy), w, h),
            "type": atype,
            "knockback": kb,
            "active": True,
            "damage": dmg,
        }

    def apply_knockback(self, kb_x, kb_y, damage):
        if self.invincible > 0:
            return False
        mult = 1 + self.damage / (80 * self.weight)
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

        gravity = GRAVITY * self.weight
        self.vy = min(self.vy + gravity, MAX_FALL)

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

        sc = self.special_color
        pygame.draw.rect(surf, sc, (bx + 4, by + 4, w - 8, 4), border_radius=2)

        eye_y = by + h // 3
        e_off = 7 if self.facing == 1 else -7
        pygame.draw.circle(surf, C_WHITE, (bx + w // 2 + e_off, eye_y), 5)
        pygame.draw.circle(surf, C_DARK, (bx + w // 2 + e_off + self.facing, eye_y), 3)

        arm_swing = math.sin(self.anim_frame * 0.15) * 8 if abs(self.vx) > 0.5 else 0
        arm_color = sc if self.attack_timer > 0 else self.dark_color
        if self.attack_timer > 0:
            arm_swing = 18 * self.facing

        ax = bx + (w if self.facing == 1 else 0)
        ay = by + h // 2
        pygame.draw.line(
            surf,
            arm_color,
            (ax, ay),
            (ax + int(arm_swing * self.facing), ay - 10),
            5,
        )

        leg_swing = int(math.sin(self.anim_frame * 0.2) * 10) if abs(self.vx) > 0.5 else 0
        pygame.draw.line(
            surf,
            self.dark_color,
            (bx + w // 3, by + h),
            (bx + w // 3 - leg_swing, by + h + 12),
            5,
        )
        pygame.draw.line(
            surf,
            self.dark_color,
            (bx + 2 * w // 3, by + h),
            (bx + 2 * w // 3 + leg_swing, by + h + 12),
            5,
        )

        if self.attack_hitbox and self.attack_timer > 5:
            color = C_YELLOW if self.attack_type == "light" else C_ORANGE
            s = pygame.Surface((self.attack_hitbox["rect"].w, self.attack_hitbox["rect"].h), pygame.SRCALPHA)
            s.fill((*color, 80))
            surf.blit(s, self.attack_hitbox["rect"].topleft)
            pygame.draw.rect(surf, color, self.attack_hitbox["rect"], 2, border_radius=6)

    def is_dead(self):
        return self.x < DEATH_ZONE_X[0] or self.x > DEATH_ZONE_X[1] or self.y > DEATH_ZONE_Y

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


def draw_hud(surf, p1, p2, font_big, font_small):
    pygame.draw.rect(surf, C_DARK, (0, HEIGHT - 90, WIDTH, 90))
    pygame.draw.line(surf, (120, 90, 200), (0, HEIGHT - 90), (WIDTH, HEIGHT - 90), 2)

    for i in range(3):
        col = p1.color if i < p1.stocks else C_HP_BG
        pygame.draw.circle(surf, col, (120 + i * 28, HEIGHT - 30), 10)
        pygame.draw.circle(surf, C_WHITE, (120 + i * 28, HEIGHT - 30), 10, 2)

    for i in range(3):
        col = p2.color if i < p2.stocks else C_HP_BG
        pygame.draw.circle(surf, col, (WIDTH - 120 - i * 28, HEIGHT - 30), 10)
        pygame.draw.circle(surf, C_WHITE, (WIDTH - 120 - i * 28, HEIGHT - 30), 10, 2)

    def dmg_color(d):
        if d < 50:
            return C_WHITE
        if d < 100:
            return C_YELLOW
        if d < 150:
            return C_ORANGE
        return C_RED

    t1 = font_big.render(f"{p1.damage}%", True, dmg_color(p1.damage))
    t2 = font_big.render(f"{p2.damage}%", True, dmg_color(p2.damage))
    surf.blit(t1, (60, HEIGHT - 80))
    surf.blit(t2, (WIDTH - 60 - t2.get_width(), HEIGHT - 80))

    n1 = font_small.render(p1.name, True, p1.color)
    n2 = font_small.render(p2.name, True, p2.color)
    surf.blit(n1, (60, HEIGHT - 92))
    surf.blit(n2, (WIDTH - 60 - n2.get_width(), HEIGHT - 92))

    cw = 300
    cx = WIDTH // 2 - cw // 2
    cy = HEIGHT - 55
    pygame.draw.rect(surf, C_HP_BG, (cx, cy, cw, 14), border_radius=7)
    ratio = p1.damage / max(1, p1.damage + p2.damage + 0.001)
    pygame.draw.rect(surf, p1.color, (cx, cy, int(cw * ratio), 14), border_radius=7)
    pygame.draw.rect(surf, p2.color, (cx + int(cw * ratio), cy, cw - int(cw * ratio), 14), border_radius=7)
    pygame.draw.rect(surf, C_WHITE, (cx, cy, cw, 14), 2, border_radius=7)


def draw_background(surf, landscape_name, bg_images):
    surf.blit(bg_images[landscape_name], (0, 0))


def draw_platforms(surf, platforms, landscape_name):
    data = LANDSCAPES[landscape_name]
    c_plat = data["plat"]
    c_top = data["plat_top"]
    c_edge = data["plat_edge"]
    c_shad = data["plat_shadow"]

    for px, py, pw, ph in platforms:
        pygame.draw.rect(surf, c_shad, (px + 4, py + 4, pw, ph + 8), border_radius=8)
        pygame.draw.rect(surf, c_plat, (px, py, pw, ph + 8), border_radius=8)
        pygame.draw.rect(surf, c_top, (px + 4, py, pw - 8, 6), border_radius=4)
        pygame.draw.rect(surf, c_edge, (px, py, pw, ph + 8), 2, border_radius=8)


def draw_character_select(surf, font_title, font_small, font_big, css, tick):
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(5 * (1 - t) + 15 * t)
        g = int(5 * (1 - t) + 10 * t)
        b = int(20 * (1 - t) + 40 * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

    title = font_title.render("ESCOLHA SEU LUTADOR", True, C_YELLOW)
    surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 18))

    n = len(CHARACTERS)
    card_w = 200
    card_h = 300
    gap = 18
    total_w = n * card_w + (n - 1) * gap
    start_x = WIDTH // 2 - total_w // 2

    for i, char in enumerate(CHARACTERS):
        cx = start_x + i * (card_w + gap)
        cy = 90

        p1_sel = css["p1_idx"] == i
        p2_sel = css["p2_idx"] == i

        hover_off = max(6 if p1_sel else 0, 6 if p2_sel else 0)
        if p1_sel and css["p1_ready"]:
            hover_off += int(math.sin(tick * 0.08) * 3)
        if p2_sel and css["p2_ready"]:
            hover_off += int(math.sin(tick * 0.08 + 1) * 3)

        shad = pygame.Surface((card_w + 8, card_h + 8), pygame.SRCALPHA)
        shad.fill((0, 0, 0, 80))
        surf.blit(shad, (cx - 2, cy + 8 - hover_off))

        card = pygame.Surface((card_w, card_h))
        for row in range(card_h):
            t2 = row / card_h
            base_r = int(20 * (1 - t2) + 35 * t2)
            base_g = int(15 * (1 - t2) + 25 * t2)
            base_b = int(45 * (1 - t2) + 70 * t2)
            cr2, cg2, cb2 = char["color"]
            mix = 0.15
            base_r = int(base_r * (1 - mix) + cr2 * mix)
            base_g = int(base_g * (1 - mix) + cg2 * mix)
            base_b = int(base_b * (1 - mix) + cb2 * mix)
            pygame.draw.line(card, (base_r, base_g, base_b), (0, row), (card_w, row))

        surf.blit(card, (cx, cy - hover_off))

        pcx = cx + card_w // 2
        pcy = cy - hover_off + 135

        bounce = int(math.sin(tick * 0.06 + i) * 3)
        if p1_sel or p2_sel:
            bounce = int(math.sin(tick * 0.1 + i) * 5)

        cw2, ch2 = 38, 56
        bx2 = pcx - cw2 // 2
        by2 = pcy - ch2 + bounce

        body_r = pygame.Rect(bx2, by2, cw2, ch2)
        pygame.draw.rect(surf, char["dark_color"], body_r, border_radius=10)
        pygame.draw.rect(surf, char["color"], body_r.inflate(-6, -6), border_radius=8)
        pygame.draw.rect(surf, char["special_color"], (bx2 + 4, by2 + 4, cw2 - 8, 4), border_radius=2)

        eye_y = by2 + ch2 // 3
        pygame.draw.circle(surf, C_WHITE, (bx2 + cw2 // 2 + 8, eye_y), 5)
        pygame.draw.circle(surf, C_DARK, (bx2 + cw2 // 2 + 9, eye_y), 3)

        arm_swing = int(math.sin(tick * 0.07 + i) * 6)
        pygame.draw.line(
            surf,
            char["dark_color"],
            (bx2 + cw2, by2 + ch2 // 2),
            (bx2 + cw2 + 10 + arm_swing, by2 + ch2 // 2 - 8),
            4,
        )

        leg_s = int(math.sin(tick * 0.07 + i) * 8)
        pygame.draw.line(surf, char["dark_color"], (bx2 + cw2 // 3, by2 + ch2), (bx2 + cw2 // 3 - leg_s, by2 + ch2 + 12), 4)
        pygame.draw.line(surf, char["dark_color"], (bx2 + 2 * cw2 // 3, by2 + ch2), (bx2 + 2 * cw2 // 3 + leg_s, by2 + ch2 + 12), 4)

        name_col = char["accent"] if (p1_sel or p2_sel) else C_WHITE
        name_surf = font_small.render(char["name"], True, name_col)
        surf.blit(name_surf, (cx + card_w // 2 - name_surf.get_width() // 2, cy - hover_off + 160))

        desc_s = font_small.render(char["desc"], True, (170, 160, 200))
        surf.blit(desc_s, (cx + card_w // 2 - desc_s.get_width() // 2, cy - hover_off + 185))

        abil_s = font_small.render(char["ability"], True, char["special_color"])
        abil_bg = pygame.Surface((abil_s.get_width() + 14, abil_s.get_height() + 6), pygame.SRCALPHA)
        r3, g3, b3 = char["special_color"]
        abil_bg.fill((r3, g3, b3, 40))
        surf.blit(abil_bg, (cx + card_w // 2 - abil_s.get_width() // 2 - 7, cy - hover_off + 207))
        surf.blit(abil_s, (cx + card_w // 2 - abil_s.get_width() // 2, cy - hover_off + 210))

        stat_labels = ["FOR", "VEL", "PUL", "DEF"]
        stat_keys = ["força", "velocidade", "pulo", "defesa"]
        bar_y = cy - hover_off + 240
        for si, (sl, sk) in enumerate(zip(stat_labels, stat_keys)):
            val = char["stats"][sk]
            lbl = font_small.render(sl, True, (180, 170, 210))
            surf.blit(lbl, (cx + 10, bar_y + si * 14 - 2))
            bar_x2 = cx + 44
            bar_w2 = card_w - 54
            pygame.draw.rect(surf, C_HP_BG, (bar_x2, bar_y + si * 14, bar_w2, 8), border_radius=4)
            fill_w = int(bar_w2 * val / 10)
            bar_c = char["accent"] if (p1_sel or p2_sel) else (100, 90, 130)
            pygame.draw.rect(surf, bar_c, (bar_x2, bar_y + si * 14, fill_w, 8), border_radius=4)

        if p1_sel and p2_sel:
            pygame.draw.rect(surf, C_P1, (cx, cy - hover_off, card_w // 2, card_h), 3, border_radius=8)
            pygame.draw.rect(surf, C_P2, (cx + card_w // 2, cy - hover_off, card_w // 2, card_h), 3, border_radius=8)
        elif p1_sel:
            pulse_a = 0.7 + 0.3 * math.sin(tick * 0.1)
            col_b = tuple(int(c * pulse_a) for c in C_P1)
            pygame.draw.rect(surf, col_b, (cx, cy - hover_off, card_w, card_h), 3, border_radius=8)
        elif p2_sel:
            pulse_a = 0.7 + 0.3 * math.sin(tick * 0.1)
            col_b = tuple(int(c * pulse_a) for c in C_P2)
            pygame.draw.rect(surf, col_b, (cx, cy - hover_off, card_w, card_h), 3, border_radius=8)
        else:
            pygame.draw.rect(surf, (60, 55, 90), (cx, cy - hover_off, card_w, card_h), 1, border_radius=8)

        if p1_sel and css["p1_ready"]:
            r_surf = font_small.render("P1 PRONTO!", True, C_P1)
            r_bg = pygame.Surface((r_surf.get_width() + 10, r_surf.get_height() + 4), pygame.SRCALPHA)
            r_bg.fill((30, 80, 180, 180))
            surf.blit(r_bg, (cx + card_w // 2 - r_surf.get_width() // 2 - 5, cy - hover_off + card_h - 38))
            surf.blit(r_surf, (cx + card_w // 2 - r_surf.get_width() // 2, cy - hover_off + card_h - 36))

        if p2_sel and css["p2_ready"]:
            r_surf = font_small.render("P2 PRONTO!", True, C_P2)
            r_bg = pygame.Surface((r_surf.get_width() + 10, r_surf.get_height() + 4), pygame.SRCALPHA)
            r_bg.fill((180, 30, 30, 180))
            surf.blit(r_bg, (cx + card_w // 2 - r_surf.get_width() // 2 - 5, cy - hover_off + card_h - 20))
            surf.blit(r_surf, (cx + card_w // 2 - r_surf.get_width() // 2, cy - hover_off + card_h - 18))

        if p1_sel:
            lbl = font_small.render("P1", True, C_P1)
            surf.blit(lbl, (cx + card_w // 2 - lbl.get_width() // 2, cy - hover_off - 26))
            arrow = font_big.render("▼", True, C_P1)
            surf.blit(arrow, (cx + card_w // 2 - arrow.get_width() // 2 - 16, cy - hover_off - 46))

        if p2_sel:
            lbl = font_small.render("P2", True, C_P2)
            surf.blit(lbl, (cx + card_w // 2 - lbl.get_width() // 2 + (14 if p1_sel else 0), cy - hover_off - 26))
            arrow = font_big.render("▼", True, C_P2)
            surf.blit(arrow, (cx + card_w // 2 - arrow.get_width() // 2 + (16 if p1_sel else 0), cy - hover_off - 46))

    p1_char = CHARACTERS[css["p1_idx"]]
    p2_char = CHARACTERS[css["p2_idx"]]

    p1_panel = pygame.Surface((300, 90), pygame.SRCALPHA)
    p1_panel.fill((30, 80, 180, 100))
    surf.blit(p1_panel, (20, HEIGHT - 110))
    p1_title = font_small.render(f"P1: {p1_char['name']}", True, C_P1)
    surf.blit(p1_title, (30, HEIGHT - 105))
    p1_ctrl = font_small.render("A/D: mover  W: pular  F/G: ataque", True, (180, 200, 255))
    surf.blit(p1_ctrl, (30, HEIGHT - 82))
    if css["p1_ready"]:
        p1_ready_txt = font_small.render("PRONTO! ✓", True, (100, 255, 100))
        surf.blit(p1_ready_txt, (30, HEIGHT - 60))
    else:
        p1_ready_hint = font_small.render("ENTER: confirmar", True, (150, 180, 220))
        surf.blit(p1_ready_hint, (30, HEIGHT - 60))

    p2_panel = pygame.Surface((300, 90), pygame.SRCALPHA)
    p2_panel.fill((180, 30, 30, 100))
    surf.blit(p2_panel, (WIDTH - 320, HEIGHT - 110))
    p2_title = font_small.render(f"P2: {p2_char['name']}", True, C_P2)
    surf.blit(p2_title, (WIDTH - 310, HEIGHT - 105))
    p2_ctrl = font_small.render("←/→: mover  ↑: pular  L/K: ataque", True, (255, 180, 180))
    surf.blit(p2_ctrl, (WIDTH - 310, HEIGHT - 82))
    if css["p2_ready"]:
        p2_ready_txt = font_small.render("PRONTO! ✓", True, (100, 255, 100))
        surf.blit(p2_ready_txt, (WIDTH - 310, HEIGHT - 60))
    else:
        p2_ready_hint = font_small.render("SPACE: confirmar", True, (220, 150, 150))
        surf.blit(p2_ready_hint, (WIDTH - 310, HEIGHT - 60))

    if css["p1_ready"] and css["p2_ready"]:
        if int(tick * 0.1) % 2 == 0:
            go_txt = font_big.render("AMBOS PRONTOS - INICIANDO!", True, C_YELLOW)
            surf.blit(go_txt, (WIDTH // 2 - go_txt.get_width() // 2, HEIGHT - 55))
    else:
        hint = font_small.render("Navegar: A/D (P1)  ←/→ (P2)   Confirmar: ENTER (P1)  SPACE (P2)", True, (140, 130, 180))
        surf.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 40))


def draw_intro(surf, font_title, font_small):
    surf.fill(C_DARK)
    title = font_title.render("BRAWL CLONE", True, C_YELLOW)
    surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

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
        surf.blit(t, (WIDTH // 2 - 250, y))
        y += 32

    start = font_small.render("Pressione ENTER para escolher personagens!", True, C_YELLOW)
    surf.blit(start, (WIDTH // 2 - start.get_width() // 2, y + 20))


def draw_landscape_select(surf, font_title, font_small, font_big, selected_idx, tick, bg_images, bg_cards):
    name = LANDSCAPE_NAMES[selected_idx]

    surf.blit(bg_images[name], (0, 0))

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 90))
    surf.blit(overlay, (0, 0))

    title = font_title.render("ESCOLHA A ARENA", True, C_YELLOW)
    surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

    n = len(LANDSCAPE_NAMES)
    card_w, card_h = 210, 240
    gap = 20
    total_w = n * card_w + (n - 1) * gap
    start_x = WIDTH // 2 - total_w // 2

    for i, name in enumerate(LANDSCAPE_NAMES):
        data = LANDSCAPES[name]
        cx = start_x + i * (card_w + gap)
        cy = 120

        is_sel = i == selected_idx
        hover_off = int(math.sin(tick * 0.05) * 5) if is_sel else 0

        shadow = pygame.Surface((card_w + 10, card_h + 10), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 100))
        surf.blit(shadow, (cx - 3, cy + 8 - hover_off))

        card_img = bg_cards[name].copy()
        tint = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        tint.fill((0, 0, 0, 85 if not is_sel else 35))
        card_img.blit(tint, (0, 0))
        surf.blit(card_img, (cx, cy - hover_off))

        border_col = data["accent"] if is_sel else (80, 70, 100)
        border_w = 3 if is_sel else 1
        pygame.draw.rect(surf, border_col, (cx, cy - hover_off, card_w, card_h), border_w, border_radius=8)

        if is_sel:
            glow = pygame.Surface((card_w + 20, card_h + 20), pygame.SRCALPHA)
            ac = data["accent"]
            pygame.draw.rect(glow, (*ac, 50), (0, 0, card_w + 20, card_h + 20), border_radius=12)
            surf.blit(glow, (cx - 10, cy - hover_off - 10))

        try:
            icon_surf = font_big.render(data["icon"], True, data["accent"])
        except Exception:
            icon_surf = font_big.render("*", True, data["accent"])
        surf.blit(icon_surf, (cx + card_w // 2 - icon_surf.get_width() // 2, cy - hover_off + 12))

        name_col = data["accent"] if is_sel else C_WHITE
        name_surf = font_small.render(name, True, name_col)
        surf.blit(name_surf, (cx + card_w // 2 - name_surf.get_width() // 2, cy - hover_off + card_h - 48))

        desc_surf = font_small.render(data["desc"], True, (220, 220, 220))
        surf.blit(desc_surf, (cx + card_w // 2 - desc_surf.get_width() // 2, cy - hover_off + card_h - 26))

    instr = font_small.render("← → para navegar   |   ENTER para confirmar   |   M para voltar ao personagem", True, (240, 240, 240))
    surf.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT - 50))


def draw_winner(surf, winner, font_title, font_small, win_particles):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surf.blit(overlay, (0, 0))

    for p in win_particles:
        p.update()
        p.draw(surf)

    txt = font_title.render(f"{winner} VENCEU!", True, C_YELLOW)
    surf.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 60))
    sub = font_small.render("R = reiniciar mesmo mapa   |   M = menu de personagens   |   ESC = sair", True, C_WHITE)
    surf.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 20))


def main():
    pygame.init()
    surf = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Brawl Clone")
    clock = pygame.time.Clock()

    try:
        font_title = pygame.font.SysFont("Arial Black", 64, bold=True)
        font_big = pygame.font.SysFont("Arial Black", 44, bold=True)
        font_small = pygame.font.SysFont("Arial", 22)
    except Exception:
        font_title = pygame.font.Font(None, 72)
        font_big = pygame.font.Font(None, 52)
        font_small = pygame.font.Font(None, 28)

    base_dir = os.path.dirname(os.path.abspath(__file__))

    def load_bg(filename):
        path = os.path.join(base_dir, "imagens", filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Imagem não encontrada: {path}")
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, (WIDTH, HEIGHT))

    bg_images = {
        "Cosmos": load_bg("ilhadoceu.png"),
        "Vulcão": load_bg("inferno.png"),
        "Oceano": load_bg("oriental.png"),
        "Floresta": load_bg("floresta.png"),
        "Tundra": load_bg("reinocongelante.png"),
    }

    card_w, card_h = 210, 240
    bg_cards = {
        name: pygame.transform.smoothscale(bg_images[name], (card_w, card_h))
        for name in LANDSCAPE_NAMES
    }

    ctrl1 = {"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "light": pygame.K_f, "heavy": pygame.K_g, "dodge": pygame.K_s}
    ctrl2 = {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP, "light": pygame.K_l, "heavy": pygame.K_k, "dodge": pygame.K_DOWN}

    css = {
        "p1_idx": 0,
        "p2_idx": 1,
        "p1_ready": False,
        "p2_ready": False,
    }
    css_ready_timer = 0

    def make_players():
        c1 = CHARACTERS[css["p1_idx"]]
        c2 = CHARACTERS[css["p2_idx"]]
        return Player(300, 200, c1, ctrl1, 1), Player(900, 200, c2, ctrl2, 2)

    selected_landscape_idx = 0
    current_landscape = LANDSCAPE_NAMES[0]

    p1, p2 = make_players()
    effects = []
    global_particles = []
    state = "intro"
    winner = None
    win_particles = []
    tick = 0

    def spawn_win_particles(color):
        return [
            Particle(
                random.randint(0, WIDTH),
                random.randint(-50, HEIGHT // 2),
                color,
                random.uniform(-3, 3),
                random.uniform(-1, 4),
                random.randint(60, 120),
                random.randint(4, 10),
            )
            for _ in range(120)
        ]

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

                if state == "intro" and event.key == pygame.K_RETURN:
                    state = "char_select"
                    css["p1_ready"] = False
                    css["p2_ready"] = False

                elif state == "char_select":
                    if not css["p1_ready"]:
                        if event.key == pygame.K_a:
                            css["p1_idx"] = (css["p1_idx"] - 1) % len(CHARACTERS)
                        elif event.key == pygame.K_d:
                            css["p1_idx"] = (css["p1_idx"] + 1) % len(CHARACTERS)
                        elif event.key == pygame.K_RETURN:
                            css["p1_ready"] = True
                    else:
                        if event.key == pygame.K_RETURN:
                            css["p1_ready"] = False

                    if not css["p2_ready"]:
                        if event.key == pygame.K_LEFT:
                            css["p2_idx"] = (css["p2_idx"] - 1) % len(CHARACTERS)
                        elif event.key == pygame.K_RIGHT:
                            css["p2_idx"] = (css["p2_idx"] + 1) % len(CHARACTERS)
                        elif event.key == pygame.K_SPACE:
                            css["p2_ready"] = True
                    else:
                        if event.key == pygame.K_SPACE:
                            css["p2_ready"] = False

                elif state == "landscape_select":
                    if event.key == pygame.K_LEFT:
                        selected_landscape_idx = (selected_landscape_idx - 1) % len(LANDSCAPE_NAMES)
                    elif event.key == pygame.K_RIGHT:
                        selected_landscape_idx = (selected_landscape_idx + 1) % len(LANDSCAPE_NAMES)
                    elif event.key == pygame.K_RETURN:
                        current_landscape = LANDSCAPE_NAMES[selected_landscape_idx]
                        p1, p2 = make_players()
                        effects.clear()
                        global_particles.clear()
                        state = "game"
                    elif event.key == pygame.K_m:
                        state = "char_select"
                        css["p1_ready"] = False
                        css["p2_ready"] = False

                elif state == "game":
                    p1.process_event(event)
                    p2.process_event(event)

                elif state == "win":
                    if event.key == pygame.K_r:
                        p1, p2 = make_players()
                        effects.clear()
                        global_particles.clear()
                        win_particles.clear()
                        winner = None
                        state = "game"
                    elif event.key == pygame.K_m:
                        state = "char_select"
                        css["p1_ready"] = False
                        css["p2_ready"] = False
                        win_particles.clear()
                        effects.clear()
                        global_particles.clear()
                        winner = None

        if state == "char_select":
            if css["p1_ready"] and css["p2_ready"]:
                css_ready_timer += 1
                if css_ready_timer >= 90:
                    css_ready_timer = 0
                    state = "landscape_select"
                    selected_landscape_idx = 0
            else:
                css_ready_timer = 0

        if state == "game":
            keys = pygame.key.get_pressed()
            p1.handle_input(keys)
            p2.handle_input(keys)
            p1.update(PLATFORMS)
            p2.update(PLATFORMS)

            for attacker, defender in [(p1, p2), (p2, p1)]:
                hb = attacker.attack_hitbox
                if hb and hb["active"]:
                    if hb["rect"].colliderect(defender.rect):
                        dx = defender.x - attacker.x
                        dir_x = 1 if dx > 0 else -1
                        hit = defender.apply_knockback(
                            dir_x * hb["knockback"] * 0.7,
                            -hb["knockback"] * 0.5,
                            hb["damage"],
                        )
                        if hit:
                            hb["active"] = False
                            ex = int((defender.x + attacker.x + attacker.W) // 2)
                            ey = int((defender.y + attacker.y + attacker.H) // 2)
                            col = C_YELLOW if hb["type"] == "light" else C_ORANGE
                            effects.append(HitEffect(ex, ey, col))
                            for _ in range(16):
                                global_particles.append(Particle(ex, ey, col))

            for player, other in [(p1, p2), (p2, p1)]:
                if player.is_dead():
                    player.stocks -= 1
                    if player.stocks <= 0:
                        winner = other.name
                        state = "win"
                        win_col = other.color
                        win_particles = spawn_win_particles(win_col)
                    else:
                        player.respawn(WIDTH // 2, 200)

            for e in effects:
                e.update()
            effects = [e for e in effects if e.life > 0]

            for p_g in global_particles:
                p_g.update()
            global_particles = [p_g for p_g in global_particles if p_g.life > 0]

        if state == "intro":
            draw_intro(surf, font_title, font_small)

        elif state == "char_select":
            draw_character_select(surf, font_title, font_small, font_big, css, tick)

        elif state == "landscape_select":
            draw_landscape_select(surf, font_title, font_small, font_big, selected_landscape_idx, tick, bg_images, bg_cards)

        elif state in ("game", "win"):
            draw_background(surf, current_landscape, bg_images)
            draw_platforms(surf, PLATFORMS, current_landscape)
            bar_col = LANDSCAPES[current_landscape]["death_bars"]
            pygame.draw.rect(surf, bar_col, (0, 0, 6, HEIGHT))
            pygame.draw.rect(surf, bar_col, (WIDTH - 6, 0, 6, HEIGHT))
            p1.draw(surf)
            p2.draw(surf)
            for e in effects:
                e.draw(surf)
            for p_g in global_particles:
                p_g.draw(surf)
            draw_hud(surf, p1, p2, font_big, font_small)
            if state == "win":
                draw_winner(surf, winner, font_title, font_small, win_particles)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()