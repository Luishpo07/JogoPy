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
            print(f"[SPRITE] Não encontrado: {path}")
            return False
        img = pygame.image.load(path).convert_alpha()
        run_frames.append(img)

    idle_path = os.path.join(folder, "idle_01.png")
    if not os.path.exists(idle_path):
        print(f"[SPRITE] Não encontrado: {idle_path}")
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
        col = (
            clamp(r * alpha),
            clamp(g * alpha),
            clamp(b * alpha)
        )
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


def _draw_char_preview(surf, char, card_cx, card_top_y, hover_off, card_w, card_h, tick, i, is_sel):
    pcx = card_cx + card_w // 2
    pcy = card_top_y - hover_off + card_h // 2 - 20

    if char.get("use_sprite") and SPRITE_CACHE:
        idle = SPRITE_CACHE["p1_idle"]
        orig_w, orig_h = idle.get_size()
        tgt_h = 120
        tgt_w = max(1, int(orig_w * tgt_h / orig_h))
        scaled = scale_sprite(idle, tgt_w, tgt_h)

        bob = int(math.sin(tick * 0.06 + i) * (5 if is_sel else 2))

        if is_sel:
            glow = pygame.Surface((tgt_w + 20, tgt_h + 20), pygame.SRCALPHA)
            ac = char["accent"]
            pygame.draw.ellipse(glow, (*ac, 55), (0, 0, tgt_w + 20, tgt_h + 20))
            surf.blit(glow, (pcx - tgt_w // 2 - 10, pcy - tgt_h // 2 - 10 + bob))

        surf.blit(scaled, (pcx - tgt_w // 2, pcy - tgt_h // 2 + bob))
    else:
        bounce = int(math.sin(tick * 0.06 + i) * (5 if is_sel else 3))
        cw2, ch2 = 38, 56
        bx2 = pcx - cw2 // 2
        by2 = pcy - ch2 // 2 + bounce

        body_r = pygame.Rect(bx2, by2, cw2, ch2)
        pygame.draw.rect(surf, char["dark_color"], body_r, border_radius=10)
        pygame.draw.rect(surf, char["color"], body_r.inflate(-6, -6), border_radius=8)
        pygame.draw.rect(surf, char["special_color"], (bx2 + 4, by2 + 4, cw2 - 8, 4), border_radius=2)

        eye_y = by2 + ch2 // 3
        pygame.draw.circle(surf, C_WHITE, (bx2 + cw2 // 2 + 8, eye_y), 5)
        pygame.draw.circle(surf, C_DARK, (bx2 + cw2 // 2 + 9, eye_y), 3)

        arm_s = int(math.sin(tick * 0.07 + i) * 6)
        pygame.draw.line(surf, char["dark_color"],
                         (bx2 + cw2, by2 + ch2 // 2),
                         (bx2 + cw2 + 10 + arm_s, by2 + ch2 // 2 - 8), 4)

        leg_s = int(math.sin(tick * 0.07 + i) * 8)
        pygame.draw.line(surf, char["dark_color"],
                         (bx2 + cw2 // 3, by2 + ch2),
                         (bx2 + cw2 // 3 - leg_s, by2 + ch2 + 12), 4)
        pygame.draw.line(surf, char["dark_color"],
                         (bx2 + 2 * cw2 // 3, by2 + ch2),
                         (bx2 + 2 * cw2 // 3 + leg_s, by2 + ch2 + 12), 4)


def draw_character_select(surf, font_title, font_small, font_big, css, tick):
    for y in range(HEIGHT):
        t = y / HEIGHT
        pygame.draw.line(surf,
                         (int(5 * (1 - t) + 15 * t), int(5 * (1 - t) + 10 * t), int(20 * (1 - t) + 40 * t)),
                         (0, y), (WIDTH, y))

    title = font_title.render("ESCOLHA SEU LUTADOR", True, C_YELLOW)
    surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 18))

    n = len(CHARACTERS)
    card_w = 185
    card_h = 310
    gap = 14
    total_w = n * card_w + (n - 1) * gap
    start_x = WIDTH // 2 - total_w // 2

    for i, char in enumerate(CHARACTERS):
        cx = start_x + i * (card_w + gap)
        cy = 90
        p1_sel = css["p1_idx"] == i
        p2_sel = css["p2_idx"] == i
        is_sel = p1_sel or p2_sel
        hover_off = 6 if is_sel else 0

        shad = pygame.Surface((card_w + 8, card_h + 8), pygame.SRCALPHA)
        shad.fill((0, 0, 0, 80))
        surf.blit(shad, (cx - 2, cy + 8 - hover_off))

        card = pygame.Surface((card_w, card_h))
        for row in range(card_h):
            t2 = row / card_h
            br = int((20 * (1 - t2) + 35 * t2) * 0.85 + char["color"][0] * 0.15)
            bg = int((15 * (1 - t2) + 25 * t2) * 0.85 + char["color"][1] * 0.15)
            bb = int((45 * (1 - t2) + 70 * t2) * 0.85 + char["color"][2] * 0.15)
            pygame.draw.line(card, (clamp(br), clamp(bg), clamp(bb)), (0, row), (card_w, row))
        surf.blit(card, (cx, cy - hover_off))

        _draw_char_preview(surf, char, cx, cy, hover_off, card_w, card_h, tick, i, is_sel)

        name_col = char["accent"] if is_sel else C_WHITE
        name_surf = font_small.render(char["name"], True, name_col)
        surf.blit(name_surf, (cx + card_w // 2 - name_surf.get_width() // 2,
                               cy - hover_off + card_h - 110))

        desc_s = font_small.render(char["desc"], True, (170, 160, 200))
        surf.blit(desc_s, (cx + card_w // 2 - desc_s.get_width() // 2,
                            cy - hover_off + card_h - 90))

        abil_s = font_small.render(char["ability"], True, char["special_color"])
        abil_bg = pygame.Surface((abil_s.get_width() + 14, abil_s.get_height() + 6), pygame.SRCALPHA)
        abil_bg.fill((*char["special_color"], 40))
        surf.blit(abil_bg, (cx + card_w // 2 - abil_s.get_width() // 2 - 7,
                             cy - hover_off + card_h - 68))
        surf.blit(abil_s, (cx + card_w // 2 - abil_s.get_width() // 2,
                             cy - hover_off + card_h - 65))

        stat_labels = ["FOR", "VEL", "PUL", "DEF"]
        stat_keys = ["força", "velocidade", "pulo", "defesa"]
        bar_y = cy - hover_off + card_h - 50
        for si, (sl, sk) in enumerate(zip(stat_labels, stat_keys)):
            val = char["stats"][sk]
            lbl = font_small.render(sl, True, (180, 170, 210))
            surf.blit(lbl, (cx + 8, bar_y + si * 13 - 2))
            bx2 = cx + 42
            bw2 = card_w - 52
            pygame.draw.rect(surf, C_HP_BG, (bx2, bar_y + si * 13, bw2, 7), border_radius=4)
            fw = int(bw2 * val / 10)
            bc = char["accent"] if is_sel else (100, 90, 130)
            pygame.draw.rect(surf, bc, (bx2, bar_y + si * 13, fw, 7), border_radius=4)

        if p1_sel and p2_sel:
            pygame.draw.rect(surf, C_P1, (cx, cy - hover_off, card_w // 2, card_h), 3, border_radius=8)
            pygame.draw.rect(surf, C_P2, (cx + card_w // 2, cy - hover_off, card_w // 2, card_h), 3, border_radius=8)
        elif p1_sel:
            pulse = 0.7 + 0.3 * math.sin(tick * 0.1)
            pygame.draw.rect(surf, tuple(int(c * pulse) for c in C_P1),
                             (cx, cy - hover_off, card_w, card_h), 3, border_radius=8)
        elif p2_sel:
            pulse = 0.7 + 0.3 * math.sin(tick * 0.1)
            pygame.draw.rect(surf, tuple(int(c * pulse) for c in C_P2),
                             (cx, cy - hover_off, card_w, card_h), 3, border_radius=8)
        else:
            pygame.draw.rect(surf, (60, 55, 90), (cx, cy - hover_off, card_w, card_h), 1, border_radius=8)

        for psel, pready, pcol, yoff in [
            (p1_sel, css["p1_ready"], C_P1, -38),
            (p2_sel, css["p2_ready"], C_P2, -20),
        ]:
            if psel and pready:
                lbl_p = font_small.render("P1 PRONTO!" if pcol == C_P1 else "P2 PRONTO!", True, pcol)
                bg_p = pygame.Surface((lbl_p.get_width() + 10, lbl_p.get_height() + 4), pygame.SRCALPHA)
                bg_p.fill((*pcol, 80))
                surf.blit(bg_p, (cx + card_w // 2 - lbl_p.get_width() // 2 - 5,
                                  cy - hover_off + card_h + yoff))
                surf.blit(lbl_p, (cx + card_w // 2 - lbl_p.get_width() // 2,
                                   cy - hover_off + card_h + yoff + 2))

        if p1_sel:
            off = -16 if p2_sel else 0
            surf.blit(font_small.render("P1", True, C_P1),
                      (cx + card_w // 2 - font_small.size("P1")[0] // 2 + off, cy - hover_off - 26))
            surf.blit(font_big.render("▼", True, C_P1),
                      (cx + card_w // 2 - font_big.size("▼")[0] // 2 + off, cy - hover_off - 46))
        if p2_sel:
            off = 16 if p1_sel else 0
            surf.blit(font_small.render("P2", True, C_P2),
                      (cx + card_w // 2 - font_small.size("P2")[0] // 2 + off, cy - hover_off - 26))
            surf.blit(font_big.render("▼", True, C_P2),
                      (cx + card_w // 2 - font_big.size("▼")[0] // 2 + off, cy - hover_off - 46))

    p1c = CHARACTERS[css["p1_idx"]]
    p2c = CHARACTERS[css["p2_idx"]]

    for panel_x, color, char, ctrl_txt, confirm_txt, is_ready in [
        (20, C_P1, p1c, "A/D: mover  W: pular  F/G: ataque", "ENTER: confirmar", css["p1_ready"]),
        (WIDTH - 330, C_P2, p2c, "←/→: mover  ↑: pular  L/K: ataque", "SPACE: confirmar", css["p2_ready"]),
    ]:
        panel = pygame.Surface((310, 90), pygame.SRCALPHA)
        panel.fill((*color, 60))
        surf.blit(panel, (panel_x, HEIGHT - 110))
        p_num = "P1" if color == C_P1 else "P2"
        surf.blit(font_small.render(f"{p_num}: {char['name']}", True, color), (panel_x + 10, HEIGHT - 105))
        surf.blit(font_small.render(ctrl_txt, True, (200, 200, 230)), (panel_x + 10, HEIGHT - 82))
        if is_ready:
            surf.blit(font_small.render("PRONTO! ✓", True, (100, 255, 100)), (panel_x + 10, HEIGHT - 60))
        else:
            surf.blit(font_small.render(confirm_txt, True, (180, 180, 210)), (panel_x + 10, HEIGHT - 60))

    if css["p1_ready"] and css["p2_ready"]:
        if int(tick * 0.1) % 2 == 0:
            go = font_big.render("AMBOS PRONTOS - INICIANDO!", True, C_YELLOW)
            surf.blit(go, (WIDTH // 2 - go.get_width() // 2, HEIGHT - 55))
    else:
        hint = font_small.render(
            "Navegar: A/D (P1)  ←/→ (P2)   Confirmar: ENTER (P1)  SPACE (P2)",
            True, (140, 130, 180))
        surf.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 40))


# ─── NOVA TELA: TELA INICIAL COM capa.png ────────────────────────────────────
def get_jogar_button_rect():
    """
    Retorna o pygame.Rect do botão JOGAR mapeado para a resolução 1280x720.
    Na imagem original (2560x1440) o botão fica em ~(230,490)-(590,565).
    Escala: 1280/2560 = 0.5 e 720/1440 = 0.5
    """
    # Coordenadas na imagem original 2560x1440, escaladas para 1280x720
    x = int(230 * 1280 / 2560)
    y = int(482 * 720 / 1440)
    w = int(360 * 1280 / 2560)
    h = int(88  * 720 / 1440)
    return pygame.Rect(x, y, w, h)


def draw_intro(surf, font_small, capa_img, tick, jogar_btn_rect):
    """
    Nova tela inicial: exibe capa.png em tela cheia.
    Desenha um leve efeito de hover/pulse sobre a área do botão JOGAR.
    """
    surf.blit(capa_img, (0, 0))

    # Efeito de brilho pulsante sobre o botão para indicar que é clicável
    mouse_pos = pygame.mouse.get_pos()
    hovering = jogar_btn_rect.collidepoint(mouse_pos)

    pulse = 0.4 + 0.35 * math.sin(tick * 0.08)
    alpha = int(pulse * 80) if not hovering else 120
    glow_surf = pygame.Surface((jogar_btn_rect.w + 20, jogar_btn_rect.h + 20), pygame.SRCALPHA)
    glow_col = (255, 220, 50, alpha)
    pygame.draw.rect(glow_surf, glow_col,
                     (0, 0, jogar_btn_rect.w + 20, jogar_btn_rect.h + 20),
                     border_radius=30)
    surf.blit(glow_surf, (jogar_btn_rect.x - 10, jogar_btn_rect.y - 10))

    if hovering:
        # Contorno branco quando hover
        pygame.draw.rect(surf, (255, 255, 255),
                         jogar_btn_rect.inflate(6, 6), 3, border_radius=28)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    # Dica discreta no rodapé
    hint = font_small.render("Clique em JOGAR ou pressione ENTER", True, (220, 220, 220))
    shadow = font_small.render("Clique em JOGAR ou pressione ENTER", True, (0, 0, 0))
    surf.blit(shadow, (WIDTH // 2 - hint.get_width() // 2 + 1, HEIGHT - 28))
    surf.blit(hint,   (WIDTH // 2 - hint.get_width() // 2,     HEIGHT - 29))


# ─── NOVA TELA: INSTRUÇÕES ────────────────────────────────────────────────────
def draw_instructions(surf, font_title, font_small, font_big, tick):
    """
    Tela de instruções/controles que aparece após o JOGAR e antes da seleção
    de personagens.
    """
    # Fundo com gradiente escuro
    for y in range(HEIGHT):
        t = y / HEIGHT
        pygame.draw.line(surf,
                         (int(8 * (1 - t) + 20 * t),
                          int(5 * (1 - t) + 12 * t),
                          int(25 * (1 - t) + 55 * t)),
                         (0, y), (WIDTH, y))

    # Título
    title = font_title.render("COMO JOGAR", True, C_YELLOW)
    surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

    # Linha decorativa
    pygame.draw.line(surf, C_YELLOW,
                     (WIDTH // 2 - 300, 110), (WIDTH // 2 + 300, 110), 2)

    # Painéis lado a lado
    panels = [
        {
            "title": "JOGADOR 1",
            "color": C_P1,
            "x": 80,
            "controls": [
                ("Mover",        "A  /  D"),
                ("Pular",        "W   (2x = double jump)"),
                ("Ataque Leve",  "F"),
                ("Ataque Forte", "G"),
                ("Dodge / Air Dash", "S"),
            ],
        },
        {
            "title": "JOGADOR 2",
            "color": C_P2,
            "x": WIDTH // 2 + 80,
            "controls": [
                ("Mover",        "← / →"),
                ("Pular",        "↑   (2x = double jump)"),
                ("Ataque Leve",  "L"),
                ("Ataque Forte", "K"),
                ("Dodge / Air Dash", "↓"),
            ],
        },
    ]

    panel_w = 510
    panel_h = 340

    for panel in panels:
        px, py = panel["x"], 140
        col = panel["color"]

        # Fundo do painel
        bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        bg.fill((*col, 25))
        surf.blit(bg, (px, py))
        pygame.draw.rect(surf, col, (px, py, panel_w, panel_h), 2, border_radius=12)

        # Título do painel
        t = font_big.render(panel["title"], True, col)
        surf.blit(t, (px + panel_w // 2 - t.get_width() // 2, py + 14))
        pygame.draw.line(surf, col, (px + 20, py + 58), (px + panel_w - 20, py + 58), 1)

        # Controles
        for idx, (action, key) in enumerate(panel["controls"]):
            row_y = py + 75 + idx * 50
            # Ação
            act_s = font_small.render(action, True, (200, 200, 230))
            surf.blit(act_s, (px + 24, row_y))
            # Fundo da tecla
            key_s = font_small.render(key, True, C_YELLOW)
            key_bg = pygame.Surface((key_s.get_width() + 16, key_s.get_height() + 6), pygame.SRCALPHA)
            key_bg.fill((255, 220, 50, 40))
            surf.blit(key_bg, (px + panel_w - key_s.get_width() - 28, row_y - 2))
            surf.blit(key_s, (px + panel_w - key_s.get_width() - 20, row_y))

    # Dica geral
    tip_y = 510
    tips = [
        "• Empurre o adversário para fora da arena para marcar pontos",
        "• Cada jogador começa com 3 vidas — quem ficar sem primeiro perde",
        "• Quanto maior o % de dano, mais longe você voa ao ser atingido",
    ]
    for i, tip in enumerate(tips):
        tip_s = font_small.render(tip, True, (180, 175, 220))
        surf.blit(tip_s, (WIDTH // 2 - tip_s.get_width() // 2, tip_y + i * 30))

    # Botão "CONTINUAR"
    btn_w, btn_h = 340, 54
    btn_x = WIDTH // 2 - btn_w // 2
    btn_y = HEIGHT - 80

    pulse = 0.75 + 0.25 * math.sin(tick * 0.09)
    btn_col = tuple(int(c * pulse) for c in C_YELLOW)
    pygame.draw.rect(surf, (30, 25, 60), (btn_x, btn_y, btn_w, btn_h), border_radius=28)
    pygame.draw.rect(surf, btn_col, (btn_x, btn_y, btn_w, btn_h), 3, border_radius=28)

    mouse_pos = pygame.mouse.get_pos()
    btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    hovering = btn_rect.collidepoint(mouse_pos)
    if hovering:
        fill = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        fill.fill((255, 220, 50, 30))
        surf.blit(fill, (btn_x, btn_y))
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    btn_text = font_small.render("▶  ESCOLHER PERSONAGEM", True, C_YELLOW)
    surf.blit(btn_text, (btn_x + btn_w // 2 - btn_text.get_width() // 2,
                          btn_y + btn_h // 2 - btn_text.get_height() // 2))

    return btn_rect  # retorna o rect para detecção de clique


def draw_landscape_select(surf, font_title, font_small, font_big,
                           selected_idx, tick, bg_images, bg_cards):
    surf.blit(bg_images[LANDSCAPE_NAMES[selected_idx]], (0, 0))
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

    for i, lname in enumerate(LANDSCAPE_NAMES):
        data = LANDSCAPES[lname]
        cx = start_x + i * (card_w + gap)
        cy = 120
        is_sel = i == selected_idx
        hover_off = int(math.sin(tick * 0.05) * 5) if is_sel else 0

        shadow = pygame.Surface((card_w + 10, card_h + 10), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 100))
        surf.blit(shadow, (cx - 3, cy + 8 - hover_off))
        surf.blit(bg_cards[lname], (cx, cy - hover_off))

        border_col = data["accent"] if is_sel else (80, 70, 100)
        pygame.draw.rect(surf, border_col, (cx, cy - hover_off, card_w, card_h),
                         3 if is_sel else 1, border_radius=8)

        name_col = data["accent"] if is_sel else C_WHITE
        name_surf = font_small.render(lname, True, name_col)
        surf.blit(name_surf, (cx + card_w // 2 - name_surf.get_width() // 2,
                               cy - hover_off + card_h - 48))

        desc_surf = font_small.render(data["desc"], True, (220, 220, 220))
        surf.blit(desc_surf, (cx + card_w // 2 - desc_surf.get_width() // 2,
                               cy - hover_off + card_h - 26))

    instr = font_small.render(
        "← → para navegar   |   ENTER para confirmar   |   M para voltar ao personagem",
        True, (240, 240, 240))
    surf.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT - 50))


def draw_winner(surf, winner, font_title, font_small, win_particles):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surf.blit(overlay, (0, 0))

    win_particles[:] = [p for p in win_particles if p.life > 0]

    for p in win_particles:
        p.update()
        p.draw(surf)

    txt = font_title.render(f"{winner} VENCEU!", True, C_YELLOW)
    surf.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 60))

    sub = font_small.render(
        "R = reiniciar | M = menu | ESC = sair",
        True, C_WHITE
    )
    surf.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 20))


def main():
    pygame.init()
    surf = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Insper Brawl")
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

    sprites_ok = load_sprites(base_dir)
    if not sprites_ok:
        print("[AVISO] Sprites de Personagem1 não encontrados — SOMBRA usará visual geométrico como fallback.")
        for c in CHARACTERS:
            if c.get("use_sprite"):
                c["use_sprite"] = False

    def load_bg(filename):
        path = os.path.join(base_dir, "imagens", filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Imagem não encontrada: {path}")
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, (WIDTH, HEIGHT))

    # ── Carrega a capa ─────────────────────────────────────────────────────
    capa_path = os.path.join(base_dir, "imagens", "capa.png")
    if os.path.exists(capa_path):
        capa_img = pygame.image.load(capa_path).convert_alpha()
        capa_img = pygame.transform.smoothscale(capa_img, (WIDTH, HEIGHT))
    else:
        # Fallback: fundo escuro com texto caso o arquivo não seja encontrado
        capa_img = pygame.Surface((WIDTH, HEIGHT))
        capa_img.fill(C_DARK)
        fb = pygame.font.SysFont("Arial Black", 72, bold=True)
        t = fb.render("INSPER BRAWL", True, C_YELLOW)
        capa_img.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 60))
        print(f"[AVISO] capa.png não encontrado em: {capa_path}")

    jogar_btn_rect = get_jogar_button_rect()

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
    state = "intro"          # estados: intro | instructions | char_select | landscape_select | game | win
    winner = None
    win_particles = []
    tick = 0
    instructions_btn_rect = pygame.Rect(0, 0, 0, 0)  # atualizado no draw

    def spawn_win_particles(color):
        return [Particle(
            random.randint(0, WIDTH), random.randint(-50, HEIGHT // 2),
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

                # ── Tela inicial ──────────────────────────────────────────
                if state == "intro" and event.key == pygame.K_RETURN:
                    state = "instructions"

                # ── Tela de instruções ────────────────────────────────────
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

            # ── Cliques do mouse ──────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mpos = event.pos
                if state == "intro" and jogar_btn_rect.collidepoint(mpos):
                    state = "instructions"
                elif state == "instructions" and instructions_btn_rect.collidepoint(mpos):
                    state = "char_select"
                    css["p1_ready"] = False
                    css["p2_ready"] = False
                    css_ready_timer = 0

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
                        player.respawn(WIDTH // 2, 200)

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
            instructions_btn_rect = draw_instructions(surf, font_title, font_small, font_big, tick)

        elif state == "char_select":
            draw_character_select(surf, font_title, font_small, font_big, css, tick)

        elif state == "landscape_select":
            draw_landscape_select(surf, font_title, font_small, font_big,
                                  selected_landscape_idx, tick, bg_images, bg_cards)

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
            for pg in global_particles:
                pg.draw(surf)
            draw_hud(surf, p1, p2, font_big, font_small)
            if state == "win":
                draw_winner(surf, winner, font_title, font_small, win_particles)

        pygame.display.flip()

    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()