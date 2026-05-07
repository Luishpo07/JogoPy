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

SPRITE_CACHE = {}


def load_sprites(base_dir):
    folder = os.path.join(base_dir, "Personagem1")

    if not os.path.isdir(folder):
        print(f"[SPRITE] Pasta não encontrada: {folder}")
        return False

    run_files = [
        f for f in os.listdir(folder)
        if f.lower().startswith("run_") and f.lower().endswith(".png")
    ]

    def run_sort_key(name):
        digits = "".join(ch for ch in os.path.splitext(name)[0] if ch.isdigit())
        return int(digits) if digits else 10**9

    run_files.sort(key=run_sort_key)

    if not run_files:
        print(f"[SPRITE] Nenhum frame run_*.png encontrado em: {folder}")
        return False

    run_frames = []
    for filename in run_files:
        path = os.path.join(folder, filename)
        if not os.path.exists(path):
            return False
        img = pygame.image.load(path).convert_alpha()
        run_frames.append(img)

    idle_path = os.path.join(folder, "idle_01.png")
    if not os.path.exists(idle_path):
        return False
    idle_img = pygame.image.load(idle_path).convert_alpha()

    SPRITE_CACHE["p1_walk"] = run_frames
    SPRITE_CACHE["p1_idle"] = idle_img
    print(f"[SPRITE] Carregados {len(run_frames)} frames de caminhada e idle_01.png com sucesso.")
    return True


CHARACTERS = [
    {
        "name": "SOMBRA",
        "color": (180, 100, 255),
        "dark_color": (80, 30, 160),
        "icon": "⚔",
        "desc": "Guerreiro Espectral",
        "stats": {"força": 8, "velocidade": 8, "pulo": 7, "defesa": 5},
        "ability": "Lâmina das Sombras",
        "special_color": (220, 140, 255),
        "speed": 7.5,
        "jump_power": -15.5,
        "weight": 0.9,
        "light_dmg": 8, "heavy_dmg": 16, "light_kb": 9, "heavy_kb": 18,
        "accent": (210, 160, 255),
        "use_sprite": True,
    },
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
        "use_sprite": False,
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
        "use_sprite": False,
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
        "use_sprite": False,
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
        "use_sprite": False,
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
        "use_sprite": False,
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
SPRITE_DISPLAY_H = 80


def scale_sprite(img, w, h):
    return pygame.transform.smoothscale(img, (w, h))


def flip_sprite(img):
    return pygame.transform.flip(img, True, False)


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
        if self.life <= 0:
            return
        alpha = max(0, self.life / self.max_life)
        r, g, b = self.color
        col = (clamp(r * alpha), clamp(g * alpha), clamp(b * alpha))
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

        self.use_sprite = char_data.get("use_sprite", False) and bool(SPRITE_CACHE)
        self._walk_timer = 0
        self._walk_idx = 0
        self._walk_frame_speed = 6

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
                    self.particles.append(Particle(
                        self.x + self.W // 2, self.y + self.H // 2,
                        C_WHITE, random.uniform(-3, 3), random.uniform(-3, 3), 14, 4))

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
                self.particles.append(Particle(
                    self.x + self.W // 2, self.y + self.H,
                    self.color, life=12, vy=random.uniform(0, 2)))

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
            "type": atype, "knockback": kb, "active": True, "damage": dmg,
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
        prev_y = self.y - self.vy
        self.on_ground = False

        if self.vy >= 0:
            current_bottom = self.y + self.H
            prev_bottom = prev_y + self.H
            for px, py, pw, ph in platforms:
                horizontally_overlapping = (self.x + self.W > px + 2) and (self.x < px + pw - 2)
                landed_from_above = prev_bottom <= py + 2 and current_bottom >= py
                if horizontally_overlapping and landed_from_above:
                    self.y = py - self.H
                    self.vy = 0
                    self.on_ground = True
                    self.jumps_left = 2
                    if not prev_on:
                        self.squash_y = 0.6
                        self.squash_x = 1.4
                    break

        if self.on_ground:
            self.vy = 0
            self.x = round(self.x)
            self.y = round(self.y)

        self.squash_y += (1.0 - self.squash_y) * 0.22
        self.squash_x += (1.0 - self.squash_x) * 0.22

        self.trail.append((self.x + self.W // 2, self.y + self.H // 2))
        if len(self.trail) > 8:
            self.trail.pop(0)

        if self.use_sprite:
            if abs(self.vx) > 0.8:
                self._walk_timer += 1
                if self._walk_timer >= self._walk_frame_speed:
                    self._walk_timer = 0
                    self._walk_idx = (self._walk_idx + 1) % len(SPRITE_CACHE["p1_walk"])
            else:
                self._walk_timer = 0
                self._walk_idx = 0

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

        if self.use_sprite:
            self._draw_sprite(surf)
        else:
            self._draw_shape(surf)

        if self.attack_hitbox and self.attack_timer > 5:
            color = C_YELLOW if self.attack_type == "light" else C_ORANGE
            s = pygame.Surface(
                (self.attack_hitbox["rect"].w, self.attack_hitbox["rect"].h),
                pygame.SRCALPHA)
            s.fill((*color, 80))
            surf.blit(s, self.attack_hitbox["rect"].topleft)
            pygame.draw.rect(surf, color, self.attack_hitbox["rect"], 2, border_radius=6)

    def _draw_sprite(self, surf):
        is_moving = abs(self.vx) > 0.8
        raw = SPRITE_CACHE["p1_walk"][self._walk_idx] if is_moving else SPRITE_CACHE["p1_idle"]
        orig_w, orig_h = raw.get_size()
        tgt_h = SPRITE_DISPLAY_H
        tgt_w = max(1, int(orig_w * tgt_h / orig_h))
        sq_w = max(1, int(tgt_w * self.squash_x))
        sq_h = max(1, int(tgt_h * self.squash_y))
        scaled = scale_sprite(raw, sq_w, sq_h)
        if self.facing == -1:
            scaled = flip_sprite(scaled)
        draw_x = int(self.x + self.W / 2 - sq_w / 2)
        draw_y = int(self.y + self.H - sq_h)
        if self.attack_timer > 5:
            glow = pygame.Surface((sq_w, sq_h), pygame.SRCALPHA)
            sc = self.special_color
            glow.fill((*sc, 70))
            surf.blit(glow, (draw_x, draw_y))
        surf.blit(scaled, (draw_x, draw_y))

    def _draw_shape(self, surf):
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
        pygame.draw.line(surf, arm_color, (ax, ay),
                         (ax + int(arm_swing * self.facing), ay - 10), 5)
        leg_swing = int(math.sin(self.anim_frame * 0.2) * 10) if abs(self.vx) > 0.5 else 0
        pygame.draw.line(surf, self.dark_color,
                         (bx + w // 3, by + h), (bx + w // 3 - leg_swing, by + h + 12), 5)
        pygame.draw.line(surf, self.dark_color,
                         (bx + 2 * w // 3, by + h), (bx + 2 * w // 3 + leg_swing, by + h + 12), 5)

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
        self._walk_timer = 0
        self._walk_idx = 0
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
        if d < 50: return C_WHITE
        if d < 100: return C_YELLOW
        if d < 150: return C_ORANGE
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


# ══════════════════════════════════════════════════════════════════════════════
#  TELA DE SELEÇÃO DE PERSONAGEM — ESTILO BRAWLHALLA com selecaopersonagem.png
# ══════════════════════════════════════════════════════════════════════════════

# Posições dos pedestais na imagem selecaopersonagem.png
# (centro X de cada pedestal, Y do topo da plataforma azul)
PED_LEFT_CX  = 455   # centro X pedestal esquerdo (P1)
PED_RIGHT_CX = 780   # centro X pedestal direito  (P2)
PED_TOP_Y    = 588   # Y do topo da plataforma azul (onde o personagem pisa)

# Grid de thumbnails
THUMB_W, THUMB_H = 68, 68
THUMB_GAP = 5
GRID_COLS = 6
GRID_X0 = 240   # início X da grade
GRID_Y0 = 10    # início Y da grade

# Painel info embaixo
INFO_PANEL_Y = 590  # Y dos painéis de info (abaixo dos pedestais)
INFO_PANEL_H = 125


def _draw_char_big_on_pedestal(surf, char, cx, foot_y, tick, facing=1, anim_frame=0,
                                player_col=None, is_ready=False):
    """Desenha o personagem grande posicionado em cima do pedestal."""
    # Tamanho do personagem exibido no pedestal
    W2, H2 = 58, 88

    bob = int(math.sin(tick * 0.06) * 4)
    bx = cx - W2 // 2
    by = foot_y - H2 + bob

    # Glow sob o personagem (reflexo na plataforma azul)
    if player_col:
        glow_alpha = 90 + int(math.sin(tick * 0.08) * 30)
        glow_w, glow_h = 110, 28
        glow_surf = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (*player_col, glow_alpha),
                            (0, 0, glow_w, glow_h))
        surf.blit(glow_surf, (cx - glow_w // 2, foot_y - 10))

    # Sprite ou forma geométrica
    if char.get("use_sprite") and SPRITE_CACHE:
        idle = SPRITE_CACHE["p1_idle"]
        orig_w, orig_h = idle.get_size()
        tgt_h = 160
        tgt_w = max(1, int(orig_w * tgt_h / orig_h))
        scaled = scale_sprite(idle, tgt_w, tgt_h)
        if facing == -1:
            scaled = flip_sprite(scaled)
        # Glow de seleção atrás do sprite
        if is_ready and player_col:
            glow2 = pygame.Surface((tgt_w + 30, tgt_h + 30), pygame.SRCALPHA)
            a2 = 50 + int(math.sin(tick * 0.1) * 25)
            pygame.draw.ellipse(glow2, (*player_col, a2), (0, 0, tgt_w + 30, tgt_h + 30))
            surf.blit(glow2, (cx - tgt_w // 2 - 15, foot_y - tgt_h - 15 + bob))
        surf.blit(scaled, (cx - tgt_w // 2, foot_y - tgt_h + bob))
        return

    # Forma geométrica
    body_rect = pygame.Rect(bx, by, W2, H2)
    pygame.draw.rect(surf, char["dark_color"], body_rect, border_radius=12)
    pygame.draw.rect(surf, char["color"], body_rect.inflate(-8, -8), border_radius=9)
    sc = char["special_color"]
    pygame.draw.rect(surf, sc, (bx + 6, by + 6, W2 - 12, 6), border_radius=3)

    # Cabeça
    hcx = cx + (9 if facing == 1 else -9)
    hcy = by - 17
    pygame.draw.circle(surf, char["dark_color"], (hcx, hcy), 20)
    pygame.draw.circle(surf, char["color"], (hcx, hcy), 17)
    eoff = 7 if facing == 1 else -7
    pygame.draw.circle(surf, C_WHITE, (hcx + eoff, hcy - 2), 5)
    pygame.draw.circle(surf, C_DARK, (hcx + eoff + facing, hcy - 2), 3)

    # Braço animado
    arm_s = int(math.sin(anim_frame * 0.07) * 10)
    ax = bx + (W2 if facing == 1 else 0)
    pygame.draw.line(surf, sc, (ax, by + H2 // 3),
                     (ax + (14 + arm_s) * facing, by + H2 // 3 - 12), 6)

    # Pernas animadas
    ls = int(math.sin(anim_frame * 0.09) * 12)
    pygame.draw.line(surf, char["dark_color"],
                     (bx + W2 // 3, by + H2), (bx + W2 // 3 - ls, by + H2 + 16), 6)
    pygame.draw.line(surf, char["dark_color"],
                     (bx + 2 * W2 // 3, by + H2), (bx + 2 * W2 // 3 + ls, by + H2 + 16), 6)


def _draw_char_thumbnail(surf, char, tx, ty, w, h, idx, tick,
                          sel_p1=False, sel_p2=False):
    """Thumbnail do personagem na grade — estilo Brawlhalla."""
    # Gradiente de fundo
    c1 = char["color"]
    c2 = char["dark_color"]
    for row in range(h):
        t = row / h
        rc = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
        pygame.draw.line(surf, rc, (tx, ty + row), (tx + w, ty + row))

    # Mini personagem
    bw, bh = max(10, w // 3 + 2), max(14, h // 2 + 2)
    bx2 = tx + w // 2 - bw // 2
    by2 = ty + h // 2 - bh // 2 + 4
    pygame.draw.rect(surf, char["dark_color"], (bx2, by2, bw, bh), border_radius=5)
    pygame.draw.rect(surf, char["color"], (bx2 + 2, by2 + 2, bw - 4, bh - 4), border_radius=4)
    # Cabeça pequena
    hr = max(5, bw // 2)
    pygame.draw.circle(surf, char["dark_color"], (tx + w // 2, by2 - hr + 2), hr + 1)
    pygame.draw.circle(surf, char["color"], (tx + w // 2, by2 - hr + 2), hr - 1)
    pygame.draw.circle(surf, C_WHITE, (tx + w // 2 + 3, by2 - hr + 1), 2)

    # Borda de seleção
    r = pygame.Rect(tx, ty, w, h)
    if sel_p1 and sel_p2:
        pygame.draw.rect(surf, C_P1, (tx, ty, w // 2, h), 3)
        pygame.draw.rect(surf, C_P2, (tx + w // 2, ty, w // 2, h), 3)
    elif sel_p1:
        pulse = 0.55 + 0.45 * math.sin(tick * 0.14)
        pygame.draw.rect(surf, tuple(int(c * pulse) for c in C_P1), r, 3)
    elif sel_p2:
        pulse = 0.55 + 0.45 * math.sin(tick * 0.14 + 1.6)
        pygame.draw.rect(surf, tuple(int(c * pulse) for c in C_P2), r, 3)
    else:
        pygame.draw.rect(surf, (60, 55, 100), r, 1)


def _draw_stat_bar(surf, x, y, label, val, max_val, color, font):
    lbl = font.render(label, True, (200, 195, 230))
    surf.blit(lbl, (x, y))
    bx = x + 38
    bw = 110
    pygame.draw.rect(surf, (20, 16, 40), (bx, y + 3, bw, 7), border_radius=4)
    fw = int(bw * val / max_val)
    if fw > 0:
        pygame.draw.rect(surf, color, (bx, y + 3, fw, 7), border_radius=4)


def draw_character_select(surf, font_title, font_small, font_big, css, tick,
                           charsel_bg):
    """Tela de seleção de personagem com selecaopersonagem.png como fundo."""

    # ── 1. Fundo: imagem do pedestal ──────────────────────────────────────
    surf.blit(charsel_bg, (0, 0))

    # Overlay semitransparente escuro no topo para legibilidade da grade
    top_overlay = pygame.Surface((WIDTH, 310), pygame.SRCALPHA)
    top_overlay.fill((0, 0, 0, 155))
    surf.blit(top_overlay, (0, 0))

    # ── 2. Barra superior ─────────────────────────────────────────────────
    try:
        title_font = pygame.font.SysFont("Arial Black", 20, bold=True)
        ctrl_font  = pygame.font.SysFont("Arial", 13)
        name_font  = pygame.font.SysFont("Arial Black", 16, bold=True)
        info_font  = pygame.font.SysFont("Arial Black", 13, bold=True)
        stat_font  = pygame.font.SysFont("Arial", 12)
    except Exception:
        title_font = ctrl_font = name_font = info_font = stat_font = pygame.font.Font(None, 16)

    bar_h = 36
    pygame.draw.rect(surf, (5, 10, 28, 220), (0, 0, WIDTH, bar_h))
    pygame.draw.line(surf, (50, 90, 180), (0, bar_h), (WIDTH, bar_h), 1)

    title_s = title_font.render("SELECIONE SEU PERSONAGEM", True, C_YELLOW)
    surf.blit(title_s, (WIDTH // 2 - title_s.get_width() // 2, 8))

    # Botão VOLTAR
    back_rect = pygame.Rect(8, 6, 90, 26)
    pygame.draw.rect(surf, (15, 28, 65), back_rect, border_radius=5)
    pygame.draw.rect(surf, (45, 80, 160), back_rect, 1, border_radius=5)
    back_s = ctrl_font.render("◄  VOLTAR", True, (190, 205, 255))
    surf.blit(back_s, (back_rect.x + 8, back_rect.y + 7))

    # ── 3. Grade de personagens ────────────────────────────────────────────
    n = len(CHARACTERS)
    cols = GRID_COLS
    rows = math.ceil(n / cols)
    cell_w = THUMB_W + THUMB_GAP
    cell_h = THUMB_H + THUMB_GAP + 16   # +16 para nome abaixo
    total_gw = cols * cell_w - THUMB_GAP
    total_gh = rows * cell_h - THUMB_GAP

    gsx = WIDTH // 2 - total_gw // 2
    gsy = bar_h + 6

    # Fundo da grade
    pad = 7
    grid_bg = pygame.Surface((total_gw + pad * 2, total_gh + pad * 2), pygame.SRCALPHA)
    grid_bg.fill((8, 14, 40, 195))
    surf.blit(grid_bg, (gsx - pad, gsy - pad))
    pygame.draw.rect(surf, (35, 55, 115),
                     (gsx - pad, gsy - pad, total_gw + pad * 2, total_gh + pad * 2),
                     1, border_radius=5)

    for idx, char in enumerate(CHARACTERS):
        col_i = idx % cols
        row_i = idx // cols
        tx = gsx + col_i * cell_w
        ty = gsy + row_i * cell_h

        sel_p1 = css["p1_idx"] == idx
        sel_p2 = css["p2_idx"] == idx

        # Highlight de fundo
        if sel_p1 or sel_p2:
            hl = pygame.Surface((THUMB_W + 4, THUMB_H + 4), pygame.SRCALPHA)
            hl.fill((80, 150, 255, 50))
            surf.blit(hl, (tx - 2, ty - 2))

        _draw_char_thumbnail(surf, char, tx, ty, THUMB_W, THUMB_H, idx, tick,
                             sel_p1=sel_p1, sel_p2=sel_p2)

        # Nome abaixo do thumb
        nm_col = char["accent"] if (sel_p1 or sel_p2) else (130, 125, 170)
        nm = ctrl_font.render(char["name"], True, nm_col)
        surf.blit(nm, (tx + THUMB_W // 2 - nm.get_width() // 2, ty + THUMB_H + 2))

    # Bolinha P1/P2 sobre o thumb selecionado
    for pidx, pcol, plabel in [(css["p1_idx"], C_P1, "P1"), (css["p2_idx"], C_P2, "P2")]:
        col_i = pidx % cols
        row_i = pidx // cols
        tx = gsx + col_i * cell_w
        ty = gsy + row_i * cell_h
        try:
            pf = pygame.font.SysFont("Arial Black", 10, bold=True)
        except Exception:
            pf = pygame.font.Font(None, 13)
        dot_x = tx + THUMB_W - 12 if plabel == "P2" else tx + 4
        dot_y = ty + 4
        pygame.draw.circle(surf, pcol, (dot_x + 5, dot_y + 5), 7)
        pygame.draw.circle(surf, C_WHITE, (dot_x + 5, dot_y + 5), 7, 1)
        ps = pf.render(plabel, True, C_WHITE)
        surf.blit(ps, (dot_x + 5 - ps.get_width() // 2, dot_y + 5 - ps.get_height() // 2))

    # ── 4. Personagens nos pedestais ──────────────────────────────────────
    p1c = CHARACTERS[css["p1_idx"]]
    p2c = CHARACTERS[css["p2_idx"]]

    _draw_char_big_on_pedestal(surf, p1c, PED_LEFT_CX, PED_TOP_Y, tick,
                                facing=1, anim_frame=tick,
                                player_col=C_P1, is_ready=css["p1_ready"])
    _draw_char_big_on_pedestal(surf, p2c, PED_RIGHT_CX, PED_TOP_Y, tick,
                                facing=-1, anim_frame=tick,
                                player_col=C_P2, is_ready=css["p2_ready"])

    # ── 5. Painéis de info dos jogadores (abaixo dos pedestais) ───────────
    # Painel P1 (esquerdo)
    _draw_player_info_panel(surf, p1c, "JOGADOR 1", "P1", C_P1,
                             css["p1_ready"],
                             "A / D: mover   W: pular   F/G: atacar   S: dodge",
                             "ENTER: confirmar",
                             20, INFO_PANEL_Y, 380, INFO_PANEL_H,
                             name_font, stat_font, info_font, tick)

    # Painel P2 (direito)
    _draw_player_info_panel(surf, p2c, "JOGADOR 2", "P2", C_P2,
                             css["p2_ready"],
                             "← / →: mover   ↑: pular   L/K: atacar   ↓: dodge",
                             "SPACE: confirmar",
                             WIDTH - 400, INFO_PANEL_Y, 380, INFO_PANEL_H,
                             name_font, stat_font, info_font, tick)

    # ── 6. Mensagem central (prontos / dica) ──────────────────────────────
    mid_x = WIDTH // 2
    if css["p1_ready"] and css["p2_ready"]:
        pulse = 0.55 + 0.45 * abs(math.sin(tick * 0.1))
        go_col = tuple(int(c * pulse) for c in C_YELLOW)
        try:
            gf = pygame.font.SysFont("Arial Black", 20, bold=True)
        except Exception:
            gf = pygame.font.Font(None, 26)
        go_s = gf.render("✔  AMBOS PRONTOS — INICIANDO!", True, go_col)
        # shadow
        go_sh = gf.render("✔  AMBOS PRONTOS — INICIANDO!", True, (0, 0, 0))
        surf.blit(go_sh, (mid_x - go_s.get_width() // 2 + 1, HEIGHT - 26))
        surf.blit(go_s,  (mid_x - go_s.get_width() // 2,     HEIGHT - 27))
    elif css["p1_ready"]:
        ws = ctrl_font.render("P1 confirmado — aguardando P2 (SPACE)...", True, C_P2)
        surf.blit(ws, (mid_x - ws.get_width() // 2, HEIGHT - 22))
    elif css["p2_ready"]:
        ws = ctrl_font.render("P2 confirmado — aguardando P1 (ENTER)...", True, C_P1)
        surf.blit(ws, (mid_x - ws.get_width() // 2, HEIGHT - 22))
    else:
        hint = ctrl_font.render(
            "Navegar: A/D (P1)   ←/→ (P2)   |   Confirmar: ENTER (P1)   SPACE (P2)",
            True, (160, 155, 210))
        surf.blit(hint, (mid_x - hint.get_width() // 2, HEIGHT - 22))

    return back_rect


def _draw_player_info_panel(surf, char, title, p_label, p_col, is_ready,
                              ctrl_str, confirm_str,
                              px, py, pw, ph,
                              name_font, stat_font, info_font, tick):
    """Painel de informações de um jogador, posicionado abaixo do pedestal."""
    # Fundo semitransparente
    bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
    bg.fill((5, 10, 30, 200))
    surf.blit(bg, (px, py))

    # Borda na cor do jogador
    pulse = 0.65 + 0.35 * math.sin(tick * 0.08)
    bdr = tuple(int(c * pulse) for c in p_col)
    pygame.draw.rect(surf, bdr, (px, py, pw, ph), 2, border_radius=6)

    # Linha decorativa no topo
    pygame.draw.line(surf, p_col, (px + 4, py + 2), (px + pw - 4, py + 2), 1)

    row_y = py + 8

    # Título do jogador + nome do personagem
    title_s = name_font.render(title, True, p_col)
    surf.blit(title_s, (px + 8, row_y))

    char_name_s = name_font.render(char["name"], True, char["accent"])
    surf.blit(char_name_s, (px + pw - char_name_s.get_width() - 8, row_y))

    row_y += 20

    # Descrição
    desc_s = stat_font.render(char["desc"], True, (175, 165, 210))
    surf.blit(desc_s, (px + 8, row_y))

    # Habilidade especial
    abil_s = stat_font.render(f"Habilidade: {char['ability']}", True, char["special_color"])
    surf.blit(abil_s, (px + pw // 2 + 4, row_y))

    row_y += 18

    # Barras de stats — 4 stats em 2 colunas
    stat_data = [
        ("FOR", char["stats"]["força"],     10, char["accent"]),
        ("VEL", char["stats"]["velocidade"],10, char["accent"]),
        ("PUL", char["stats"]["pulo"],      10, char["accent"]),
        ("DEF", char["stats"]["defesa"],    10, char["accent"]),
    ]
    col_w = pw // 2 - 8
    for si, (label, val, mx, col) in enumerate(stat_data):
        cx2 = px + 8 + (si % 2) * (col_w + 8)
        cy2 = row_y + (si // 2) * 16
        _draw_stat_bar(surf, cx2, cy2, label, val, mx, col, stat_font)

    row_y += 38

    # Controles
    ctrl_s = stat_font.render(ctrl_str, True, (175, 175, 215))
    surf.blit(ctrl_s, (px + 8, row_y))
    row_y += 14

    # Confirmação / pronto
    if is_ready:
        rp = 0.5 + 0.5 * abs(math.sin(tick * 0.12))
        rc = tuple(int(c * rp) for c in (80, 255, 100))
        rd = info_font.render(f"✔  {p_label} PRONTO!", True, rc)
        surf.blit(rd, (px + 8, row_y))
    else:
        conf_s = stat_font.render(confirm_str, True, C_YELLOW)
        surf.blit(conf_s, (px + 8, row_y))


# ─── TELA INICIAL COM capa.png ────────────────────────────────────────────────
def get_jogar_button_rect():
    return pygame.Rect(140, 425, 475, 68)


def draw_intro(surf, font_small, capa_img, tick, jogar_btn_rect):
    surf.blit(capa_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    hovering = jogar_btn_rect.collidepoint(mouse_pos)
    pulse = 0.4 + 0.35 * math.sin(tick * 0.08)
    alpha = int(pulse * 80) if not hovering else 140
    glow_surf = pygame.Surface((jogar_btn_rect.w + 20, jogar_btn_rect.h + 20), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, (255, 220, 50, alpha),
                     (0, 0, jogar_btn_rect.w + 20, jogar_btn_rect.h + 20), border_radius=30)
    surf.blit(glow_surf, (jogar_btn_rect.x - 10, jogar_btn_rect.y - 10))
    if hovering:
        pygame.draw.rect(surf, C_WHITE, jogar_btn_rect.inflate(6, 6), 3, border_radius=28)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    hint = font_small.render("Clique em JOGAR ou pressione ENTER", True, (220, 220, 220))
    shadow = font_small.render("Clique em JOGAR ou pressione ENTER", True, (0, 0, 0))
    surf.blit(shadow, (WIDTH // 2 - hint.get_width() // 2 + 1, HEIGHT - 28))
    surf.blit(hint,   (WIDTH // 2 - hint.get_width() // 2,     HEIGHT - 29))


# ─── TELA DE INSTRUÇÕES ───────────────────────────────────────────────────────
def draw_instructions(surf, font_title, font_small, font_big, tick):
    for y in range(HEIGHT):
        t = y / HEIGHT
        pygame.draw.line(surf,
                         (int(8*(1-t)+20*t), int(5*(1-t)+12*t), int(25*(1-t)+55*t)),
                         (0, y), (WIDTH, y))

    title = font_title.render("COMO JOGAR", True, C_YELLOW)
    surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
    pygame.draw.line(surf, C_YELLOW, (WIDTH//2-300, 110), (WIDTH//2+300, 110), 2)

    panels = [
        {"title": "JOGADOR 1", "color": C_P1, "x": 80,
         "controls": [("Mover","A  /  D"),("Pular","W  (2x = double jump)"),
                      ("Ataque Leve","F"),("Ataque Forte","G"),("Dodge / Air Dash","S")]},
        {"title": "JOGADOR 2", "color": C_P2, "x": WIDTH//2+80,
         "controls": [("Mover","← / →"),("Pular","↑  (2x = double jump)"),
                      ("Ataque Leve","L"),("Ataque Forte","K"),("Dodge / Air Dash","↓")]},
    ]
    panel_w, panel_h = 510, 340
    for panel in panels:
        px, py = panel["x"], 140
        col = panel["color"]
        bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        bg.fill((*col, 25))
        surf.blit(bg, (px, py))
        pygame.draw.rect(surf, col, (px, py, panel_w, panel_h), 2, border_radius=12)
        t = font_big.render(panel["title"], True, col)
        surf.blit(t, (px + panel_w//2 - t.get_width()//2, py + 14))
        pygame.draw.line(surf, col, (px+20, py+58), (px+panel_w-20, py+58), 1)
        for idx, (action, key) in enumerate(panel["controls"]):
            row_y = py + 75 + idx * 50
            act_s = font_small.render(action, True, (200, 200, 230))
            surf.blit(act_s, (px+24, row_y))
            key_s = font_small.render(key, True, C_YELLOW)
            key_bg = pygame.Surface((key_s.get_width()+16, key_s.get_height()+6), pygame.SRCALPHA)
            key_bg.fill((255, 220, 50, 40))
            surf.blit(key_bg, (px+panel_w-key_s.get_width()-28, row_y-2))
            surf.blit(key_s,  (px+panel_w-key_s.get_width()-20, row_y))

    tips = ["• Empurre o adversário para fora da arena para marcar pontos",
            "• Cada jogador começa com 3 vidas — quem ficar sem primeiro perde",
            "• Quanto maior o % de dano, mais longe você voa ao ser atingido"]
    for i, tip in enumerate(tips):
        tip_s = font_small.render(tip, True, (180, 175, 220))
        surf.blit(tip_s, (WIDTH//2 - tip_s.get_width()//2, 510 + i*30))

    btn_w, btn_h = 340, 54
    btn_x, btn_y = WIDTH//2 - btn_w//2, HEIGHT - 80
    pulse = 0.75 + 0.25 * math.sin(tick * 0.09)
    btn_col = tuple(int(c * pulse) for c in C_YELLOW)
    pygame.draw.rect(surf, (30, 25, 60), (btn_x, btn_y, btn_w, btn_h), border_radius=28)
    pygame.draw.rect(surf, btn_col, (btn_x, btn_y, btn_w, btn_h), 3, border_radius=28)
    btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    if btn_rect.collidepoint(pygame.mouse.get_pos()):
        fill = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        fill.fill((255, 220, 50, 30))
        surf.blit(fill, (btn_x, btn_y))
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    btn_text = font_small.render("▶  ESCOLHER PERSONAGEM", True, C_YELLOW)
    surf.blit(btn_text, (btn_x + btn_w//2 - btn_text.get_width()//2,
                          btn_y + btn_h//2 - btn_text.get_height()//2))
    return btn_rect


def draw_landscape_select(surf, font_title, font_small, font_big,
                           selected_idx, tick, bg_images, bg_cards):
    surf.blit(bg_images[LANDSCAPE_NAMES[selected_idx]], (0, 0))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 90))
    surf.blit(overlay, (0, 0))
    title = font_title.render("ESCOLHA A ARENA", True, C_YELLOW)
    surf.blit(title, (WIDTH//2 - title.get_width()//2, 30))
    n = len(LANDSCAPE_NAMES)
    card_w, card_h = 210, 240
    gap = 20
    total_w = n * card_w + (n-1) * gap
    start_x = WIDTH//2 - total_w//2
    for i, lname in enumerate(LANDSCAPE_NAMES):
        data = LANDSCAPES[lname]
        cx = start_x + i * (card_w + gap)
        cy = 120
        is_sel = i == selected_idx
        hover_off = int(math.sin(tick * 0.05) * 5) if is_sel else 0
        shadow = pygame.Surface((card_w+10, card_h+10), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 100))
        surf.blit(shadow, (cx-3, cy+8-hover_off))
        surf.blit(bg_cards[lname], (cx, cy-hover_off))
        border_col = data["accent"] if is_sel else (80, 70, 100)
        pygame.draw.rect(surf, border_col, (cx, cy-hover_off, card_w, card_h),
                         3 if is_sel else 1, border_radius=8)
        name_col = data["accent"] if is_sel else C_WHITE
        name_surf = font_small.render(lname, True, name_col)
        surf.blit(name_surf, (cx+card_w//2-name_surf.get_width()//2, cy-hover_off+card_h-48))
        desc_surf = font_small.render(data["desc"], True, (220, 220, 220))
        surf.blit(desc_surf, (cx+card_w//2-desc_surf.get_width()//2, cy-hover_off+card_h-26))
    instr = font_small.render(
        "← → para navegar   |   ENTER para confirmar   |   M para voltar ao personagem",
        True, (240, 240, 240))
    surf.blit(instr, (WIDTH//2 - instr.get_width()//2, HEIGHT-50))


def draw_missao_concluida(surf, font_small, missao_img, winner, tick, win_particles):
    surf.blit(missao_img, (0, 0))
    win_particles[:] = [p for p in win_particles if p.life > 0]
    for p in win_particles:
        p.update()
        p.draw(surf)
    try:
        wfont = pygame.font.SysFont("Arial Black", 36, bold=True)
    except Exception:
        wfont = pygame.font.Font(None, 46)
    winner_text = wfont.render(f"🏆  {winner} VENCEU!", True, C_YELLOW)
    shadow_text = wfont.render(f"🏆  {winner} VENCEU!", True, (0, 0, 0))
    wx = WIDTH//2 - winner_text.get_width()//2
    surf.blit(shadow_text, (wx+2, 432))
    surf.blit(winner_text, (wx,   430))

    btn_w, btn_h = 260, 62
    gap = 40
    btn_start_x = WIDTH//2 - (btn_w*2+gap)//2
    reiniciar_rect = pygame.Rect(btn_start_x, 510, btn_w, btn_h)
    menu_rect      = pygame.Rect(btn_start_x + btn_w + gap, 510, btn_w, btn_h)
    mouse_pos = pygame.mouse.get_pos()

    for rect, base_col, hover_col, bdr_col, label, text_col in [
        (reiniciar_rect, (230,150,20), (255,200,80), (255,180,40), "↺  REINICIAR", (20,10,0)),
        (menu_rect,      (30,100,210), (80,180,255), (60,140,255), "⌂  MENU",      C_WHITE),
    ]:
        hover = rect.collidepoint(mouse_pos)
        pulse = 0.85 + 0.15 * math.sin(tick * 0.1)
        c = tuple(min(255, int(v * (1.15 if hover else pulse))) for v in base_col)
        shad = pygame.Surface((btn_w+6, btn_h+6), pygame.SRCALPHA)
        shad.fill((0, 0, 0, 100))
        surf.blit(shad, (rect.x-2, rect.y+4))
        pygame.draw.rect(surf, c, rect, border_radius=32)
        hl = pygame.Surface((btn_w, btn_h//2), pygame.SRCALPHA)
        hl.fill((255, 255, 255, 30))
        surf.blit(hl, (rect.x, rect.y))
        pygame.draw.rect(surf, hover_col if hover else bdr_col, rect, 2, border_radius=32)
        try:
            bf = pygame.font.SysFont("Arial Black", 22, bold=True)
        except Exception:
            bf = pygame.font.Font(None, 28)
        bt = bf.render(label, True, text_col)
        surf.blit(bt, (rect.centerx - bt.get_width()//2, rect.centery - bt.get_height()//2))

    if reiniciar_rect.collidepoint(mouse_pos) or menu_rect.collidepoint(mouse_pos):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    hint = font_small.render("R = reiniciar   |   M = menu   |   ESC = sair", True, (200,200,200))
    sh   = font_small.render("R = reiniciar   |   M = menu   |   ESC = sair", True, (0,0,0))
    hx = WIDTH//2 - hint.get_width()//2
    surf.blit(sh,   (hx+1, HEIGHT-27))
    surf.blit(hint, (hx,   HEIGHT-28))
    return reiniciar_rect, menu_rect


def main():
    pygame.init()
    surf = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Insper Brawl")
    clock = pygame.time.Clock()

    try:
        font_title = pygame.font.SysFont("Arial Black", 64, bold=True)
        font_big   = pygame.font.SysFont("Arial Black", 44, bold=True)
        font_small = pygame.font.SysFont("Arial", 22)
    except Exception:
        font_title = pygame.font.Font(None, 72)
        font_big   = pygame.font.Font(None, 52)
        font_small = pygame.font.Font(None, 28)

    base_dir = os.path.dirname(os.path.abspath(__file__))

    sprites_ok = load_sprites(base_dir)
    if not sprites_ok:
        print("[AVISO] Sprites não encontrados — usando visual geométrico.")
        for c in CHARACTERS:
            if c.get("use_sprite"):
                c["use_sprite"] = False

    def load_bg(filename):
        path = os.path.join(base_dir, "imagens", filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Imagem não encontrada: {path}")
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, (WIDTH, HEIGHT))

    # Capa
    capa_path = os.path.join(base_dir, "imagens", "capa.png")
    if os.path.exists(capa_path):
        capa_img = pygame.transform.smoothscale(
            pygame.image.load(capa_path).convert_alpha(), (WIDTH, HEIGHT))
    else:
        capa_img = pygame.Surface((WIDTH, HEIGHT))
        capa_img.fill(C_DARK)
        fb = pygame.font.SysFont("Arial Black", 72, bold=True)
        t = fb.render("INSPER BRAWL", True, C_YELLOW)
        capa_img.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 60))

    # Background da tela de seleção de personagem
    charsel_bg_path = os.path.join(base_dir, "imagens", "selecaopersonagem.png")
    if os.path.exists(charsel_bg_path):
        charsel_bg = pygame.transform.smoothscale(
            pygame.image.load(charsel_bg_path).convert_alpha(), (WIDTH, HEIGHT))
        print("[OK] selecaopersonagem.png carregado.")
    else:
        # Fallback: gradiente azul escuro
        charsel_bg = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(10*(1-t)+20*t)
            g = int(16*(1-t)+30*t)
            b = int(40*(1-t)+70*t)
            pygame.draw.line(charsel_bg, (r, g, b), (0, y), (WIDTH, y))
        print(f"[AVISO] selecaopersonagem.png não encontrado em: {charsel_bg_path}")

    # Missão concluída
    missao_path = os.path.join(base_dir, "imagens", "missao_concluida.png")
    if os.path.exists(missao_path):
        missao_img = pygame.transform.smoothscale(
            pygame.image.load(missao_path).convert_alpha(), (WIDTH, HEIGHT))
    else:
        missao_img = pygame.Surface((WIDTH, HEIGHT))
        missao_img.fill((10, 10, 40))
        fb2 = pygame.font.SysFont("Arial Black", 72, bold=True)
        t2 = fb2.render("MISSÃO CONCLUÍDA!", True, C_YELLOW)
        missao_img.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 - 100))

    jogar_btn_rect = get_jogar_button_rect()

    bg_images = {
        "Cosmos":   load_bg("ilhadoceu.png"),
        "Vulcão":   load_bg("inferno.png"),
        "Oceano":   load_bg("oriental.png"),
        "Floresta": load_bg("floresta.png"),
        "Tundra":   load_bg("reinocongelante.png"),
    }
    card_w, card_h = 210, 240
    bg_cards = {
        name: pygame.transform.smoothscale(bg_images[name], (card_w, card_h))
        for name in LANDSCAPE_NAMES
    }

    ctrl1 = {"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w,
             "light": pygame.K_f, "heavy": pygame.K_g, "dodge": pygame.K_s}
    ctrl2 = {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP,
             "light": pygame.K_l, "heavy": pygame.K_k, "dodge": pygame.K_DOWN}

    css = {"p1_idx": 0, "p2_idx": 1, "p1_ready": False, "p2_ready": False}
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
    instructions_btn_rect = pygame.Rect(0, 0, 0, 0)
    charsel_back_rect = pygame.Rect(0, 0, 0, 0)
    win_reiniciar_rect = pygame.Rect(0, 0, 0, 0)
    win_menu_rect = pygame.Rect(0, 0, 0, 0)

    def spawn_win_particles(color):
        return [Particle(random.randint(0, WIDTH), random.randint(-50, HEIGHT//2),
                         color, random.uniform(-3, 3), random.uniform(-1, 4),
                         random.randint(60, 120), random.randint(4, 10))
                for _ in range(120)]

    def reset_to_char_select():
        nonlocal state, css_ready_timer, winner
        state = "char_select"
        css["p1_ready"] = False
        css["p2_ready"] = False
        css_ready_timer = 0
        winner = None

    def reset_match():
        nonlocal p1, p2, effects, global_particles, win_particles, winner, state
        p1, p2 = make_players()
        effects.clear()
        global_particles.clear()
        win_particles.clear()
        winner = None
        state = "game"

    running = True
    while running:
        clock.tick(FPS)
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state in ("win", "game"):
                        reset_to_char_select()
                    elif state in ("char_select", "landscape_select", "instructions"):
                        state = "intro"
                    else:
                        running = False

                if state == "intro" and event.key == pygame.K_RETURN:
                    state = "instructions"

                elif state == "instructions" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    state = "char_select"
                    css["p1_ready"] = False
                    css["p2_ready"] = False
                    css_ready_timer = 0

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
                        reset_match()
                    elif event.key == pygame.K_m:
                        reset_to_char_select()

                elif state == "game":
                    p1.process_event(event)
                    p2.process_event(event)

                elif state == "win":
                    if event.key == pygame.K_r:
                        reset_match()
                    elif event.key == pygame.K_m:
                        reset_to_char_select()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mpos = event.pos
                if state == "intro" and jogar_btn_rect.collidepoint(mpos):
                    state = "instructions"
                elif state == "instructions" and instructions_btn_rect.collidepoint(mpos):
                    state = "char_select"
                    css["p1_ready"] = False
                    css["p2_ready"] = False
                    css_ready_timer = 0
                elif state == "char_select" and charsel_back_rect.collidepoint(mpos):
                    state = "intro"
                elif state == "win":
                    if win_reiniciar_rect.collidepoint(mpos):
                        reset_match()
                    elif win_menu_rect.collidepoint(mpos):
                        reset_to_char_select()

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
                            hb["damage"])
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
                        win_particles = spawn_win_particles(other.color)
                    else:
                        player.respawn(WIDTH//2, 200)

            for e in effects:
                e.update()
            effects = [e for e in effects if e.life > 0]
            for pg in global_particles:
                pg.update()
            global_particles = [pg for pg in global_particles if pg.life > 0]

        # ── Renderização ──────────────────────────────────────────────────
        if state == "intro":
            draw_intro(surf, font_small, capa_img, tick, jogar_btn_rect)

        elif state == "instructions":
            instructions_btn_rect = draw_instructions(
                surf, font_title, font_small, font_big, tick)

        elif state == "char_select":
            charsel_back_rect = draw_character_select(
                surf, font_title, font_small, font_big, css, tick, charsel_bg)

        elif state == "landscape_select":
            draw_landscape_select(surf, font_title, font_small, font_big,
                                  selected_landscape_idx, tick, bg_images, bg_cards)

        elif state == "game":
            draw_background(surf, current_landscape, bg_images)
            draw_platforms(surf, PLATFORMS, current_landscape)
            bar_col = LANDSCAPES[current_landscape]["death_bars"]
            pygame.draw.rect(surf, bar_col, (0, 0, 6, HEIGHT))
            pygame.draw.rect(surf, bar_col, (WIDTH-6, 0, 6, HEIGHT))
            p1.draw(surf)
            p2.draw(surf)
            for e in effects:
                e.draw(surf)
            for pg in global_particles:
                pg.draw(surf)
            draw_hud(surf, p1, p2, font_big, font_small)

        elif state == "win":
            win_reiniciar_rect, win_menu_rect = draw_missao_concluida(
                surf, font_small, missao_img, winner, tick, win_particles)

        pygame.display.flip()

    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()