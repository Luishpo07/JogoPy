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

C_BG_TOP   = (15,  10,  40)
C_BG_BOT   = (40,  20,  80)
C_PLAT     = (80,  60, 140)
C_PLAT_TOP = (120, 90, 200)
C_P1       = (60, 140, 255)
C_P1_DARK  = (30,  80, 180)
C_P2       = (255,  60,  60)
C_P2_DARK  = (180,  30,  30)
C_WHITE    = (255, 255, 255)
C_YELLOW   = (255, 220,  50)
C_ORANGE   = (255, 140,  20)
C_RED      = (220,  40,  40)
C_DARK     = (20,  15,  50)
C_HP_BG    = (50,  40,  80)


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


def draw_hud(surf, p1, p2, font_big, font_small):
    pygame.draw.rect(surf, C_DARK, (0, HEIGHT - 90, WIDTH, 90))
    pygame.draw.line(surf, C_PLAT_TOP, (0, HEIGHT - 90), (WIDTH, HEIGHT - 90), 2)

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


def draw_background(surf, stars):
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(C_BG_TOP[0] * (1-t) + C_BG_BOT[0] * t)
        g = int(C_BG_TOP[1] * (1-t) + C_BG_BOT[1] * t)
        b = int(C_BG_TOP[2] * (1-t) + C_BG_BOT[2] * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
    for sx, sy, sz, _ in stars:
        alpha = sz / 3
        col = (int(200*alpha), int(180*alpha), int(255*alpha))
        pygame.draw.circle(surf, col, (int(sx), int(sy)), sz)


def draw_platforms(surf, platforms):
    for px, py, pw, ph in platforms:
        pygame.draw.rect(surf, (30, 20, 60), (px+4, py+4, pw, ph), border_radius=8)
        pygame.draw.rect(surf, C_PLAT, (px, py, pw, ph), border_radius=8)
        pygame.draw.rect(surf, C_PLAT_TOP, (px+4, py, pw-8, 5), border_radius=4)
        pygame.draw.rect(surf, (160, 130, 255), (px, py, pw, ph), 2, border_radius=8)


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

    start = font_small.render("Pressione ENTER para comecar!", True, C_YELLOW)
    surf.blit(start, (WIDTH//2 - start.get_width()//2, y + 20))


def draw_winner(surf, winner, font_title, font_small, win_particles):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surf.blit(overlay, (0, 0))
    for p in win_particles:
        p.update()
        p.draw(surf)
    txt = font_title.render(f"{winner} VENCEU!", True, C_YELLOW)
    surf.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 60))
    sub = font_small.render("Pressione R para reiniciar ou ESC para sair", True, C_WHITE)
    surf.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))


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

    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT-100),
              random.randint(1, 3), random.uniform(0.1, 0.5)) for _ in range(120)]

    ctrl1 = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w,
              'light': pygame.K_f, 'heavy': pygame.K_g, 'dodge': pygame.K_s}
    ctrl2 = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP,
              'light': pygame.K_l, 'heavy': pygame.K_k, 'dodge': pygame.K_DOWN}

    def make_players():
        return (Player(300, 300, C_P1, C_P1_DARK, ctrl1, "JOGADOR 1"),
                Player(900, 300, C_P2, C_P2_DARK, ctrl2, "JOGADOR 2"))

    p1, p2 = make_players()
    effects = []
    global_particles = []
    state = "intro"
    winner = None
    win_particles = []

    def spawn_win_particles(color):
        return [Particle(random.randint(0, WIDTH), random.randint(-50, HEIGHT//2),
                         color, random.uniform(-3, 3), random.uniform(-1, 4),
                         random.randint(60, 120), random.randint(4, 10))
                for _ in range(120)]

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if state == "intro" and event.key == pygame.K_RETURN:
                    state = "game"
                    p1, p2 = make_players()
                if state == "game":
                    p1.process_event(event)
                    p2.process_event(event)
                if state == "win" and event.key == pygame.K_r:
                    state = "game"
                    p1, p2 = make_players()
                    effects.clear()
                    global_particles.clear()
                    win_particles.clear()
                    winner = None

        if state == "intro":
            draw_intro(surf, font_title, font_small)
            pygame.display.flip()
            continue

        if state == "game":
            keys = pygame.key.get_pressed()
            p1.handle_input(keys)
            p2.handle_input(keys)
            p1.update(PLATFORMS)
            p2.update(PLATFORMS)

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

        draw_background(surf, stars)
        draw_platforms(surf, PLATFORMS)
        pygame.draw.rect(surf, (180, 30, 30), (0, 0, 6, HEIGHT))
        pygame.draw.rect(surf, (180, 30, 30), (WIDTH-6, 0, 6, HEIGHT))

        if state in ("game", "win"):
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
