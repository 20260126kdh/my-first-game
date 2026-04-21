import pygame
import random
import sys
import base64, io
import math

pygame.init()

SHEET_B64 = "iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAYAAABV7bNHAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4gYLEx862i+ojQAAA2NJREFUeNrtW9t1qzAQXHypgArcgUuAjlICcgmpyEoJ6SBpwC34ftjiGNBjH5Iwzs6nETPaXUGQJgugUEjQ/IUgDcAt8Hsy/nbvAWB4x2EAGIb5RWsBrL2ldNq9BxDjnvH2/WrMOAyTTkij3XsASW4P71JvvMfj1Wj3HkAQz9xfX2ENN8Za/CNWMgAvNyIArMbE3/dhXgd3ve9dsVf8be0AZtUlBBCrspc/xb3UcU9DbAWtkkMMIJWkiT+W9IhOqMpJhBK7fK96cAjexAgAI4gak+ve+/uRf/15Bc2qKwC5yqnHhjsn7OPoxgZ02uRkqAEEnmV2EJHJ18BBsvxI46QVfqkElQxYEixFg7LqIqv+kL1SEQ4D0JwFGmdrk1/tXI0Q92FFzH3mH1XABJGzwmKNBHeT3GJgX9LY5FA0GNxoDSR3Q96keirlljQ1gKQGkxu72cZwNxgBxETYxx4pDZPhUK/UcY1CoVAoFArFOwP1ofSXP7Q288UoX+tbFmITX4y03xMUArtVihWiui+GTb6kEKTNdqIQ1X0xVPIFhaAmP1WIbXwxTPIZhSAnH1GI9SMm9cUwB2yY5EcKEdWgJj9QCKfxb5X941H01h8AoPn5MRbg7K3u8Qjw+8sjf9zn01jxczSe7nMaMl/scoGu6+D68THnoFi9qRVH0eDwJzREvljXdfhJMPhFGgS/LqZR3xfj8lPuy+i9iXyx6+kE19MJPznGxEkazMTENJrgn0mqGMIXE/EjNMT8Ho3qvhiZn6jB4o9obOKLkbcCRA3uVsOnsakvRtlMGoFxWFJDoVAoFAqF4l3xEr7YK/Nv6ovtgZ/vDrjzXsY/WO6Jf3tf7MX5X8MXy92P5o4vcnccmsK+2GryBRrqTOaOw6r9YiZDQx3qCIPbcRhbQaZWv5i0oS6noYCYS9wXG8e7X7Q80Hag+mKUyedIaIrbXY9oRH2xyS8KQOSLuQJ8f4evXy7QfX6WSQ5y7Da+WK0CuCT7ihD6PZqgxUS8flHqOnZZl14VyyQjfw8myFToFzOLZjdqAdBf1Bn70drV5s3a2/j84irQLzYFQPGskGOnGB7zChVg+Xto7m1IAKwt4ouRiiBoqEMXgdpxiDkmyHEsYQo31JmSHYc1YQo21JnSHYfvAqMdh4rN8B+RSnTlJSwQBQAAAABJRU5ErkJggg=="

def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)

WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (220, 50, 50)
YELLOW = (240, 200, 0)
GRAY   = (40, 40, 40)
CYAN   = (0, 255, 255)
PURPLE = (160, 60, 220)
ORANGE = (255, 140, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hungry Slime")
clock = pygame.time.Clock()

font = get_korean_font(36)
font_big = get_korean_font(72)
font_small = get_korean_font(22)

# Lv.1~10 설정
# 적 속도: 기존 Lv.3(min7,max12)이 Lv.8 수준이 되도록 보간
# 스폰 간격: 빠를수록 적이 많이 나옴 (낮은 값 = 자주 스폰)
# 노란/주황/보라 적 해금: Lv.3 / Lv.5 / Lv.5
LEVELS = [
    {"min_speed": 3, "max_speed": 5,  "spawn": 55, "label": "Lv.1"},   # 1
    {"min_speed": 4, "max_speed": 6,  "spawn": 50, "label": "Lv.2"},   # 2
    {"min_speed": 4, "max_speed": 7,  "spawn": 45, "label": "Lv.3"},   # 3  ← 노란 해금
    {"min_speed": 3, "max_speed": 6,  "spawn": 40, "label": "Lv.4"},   # 4
    {"min_speed": 4, "max_speed": 7,  "spawn": 34, "label": "Lv.5"},   # 5  ← 주황/보라 해금
    {"min_speed": 5, "max_speed": 8,  "spawn": 28, "label": "Lv.6"},   # 6
    {"min_speed": 5, "max_speed": 10, "spawn": 23, "label": "Lv.7"},   # 7
    {"min_speed": 7, "max_speed": 12, "spawn": 18, "label": "Lv.8"},   # 8  ← 기존 Lv.3 속도
    {"min_speed": 8, "max_speed": 14, "spawn": 14, "label": "Lv.9"},   # 9
    {"min_speed": 9, "max_speed": 16, "spawn": 10, "label": "Lv.10"},  # 10 MAX
]

# 레벨별 점수 임계값 (score >= 이 값이면 해당 레벨)
LEVEL_SCORE_THRESHOLDS = [0, 15, 35, 60, 90, 130, 180, 240, 320, 420]

PLAYER_W, PLAYER_H = 50, 50
ENEMY_W, ENEMY_H = 30, 30

FRAME_W, FRAME_H = 24, 24
COLS = 3

IDLE_FRAME_DELAY = 180
WALK_FRAME_DELAY = 80

sheet_bytes = base64.b64decode(SHEET_B64)
player_sheet = pygame.image.load(io.BytesIO(sheet_bytes)).convert_alpha()

all_frames = []
for i in range(9):
    row, col = divmod(i, COLS)
    rect = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
    all_frames.append(player_sheet.subsurface(rect))

idle_frames = all_frames[0:3]
walk_frames = all_frames[3:6]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 아이템 클래스
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ITEM_SPEED = 3
ITEM_R     = 20
ITEM_SPAWN_INTERVAL = 720
MAX_LIVES = 5
HUNGER_MAX = 100.0

HUNGER_DRAIN_BY_LEVEL = [
    0.020,   # Lv.1  (매우 느림)
    0.030,   # Lv.2
    0.040,   # Lv.3  ← 기존 Lv.3과 비슷한 속도(0.080 → 완만하게 재배치)
    0.052,   # Lv.4
    0.065,   # Lv.5
    0.080,   # Lv.6
    0.096,   # Lv.7
    0.114,   # Lv.8
    0.134,   # Lv.9
    0.158,   # Lv.10 MAX (가장 빠름)
]

HUNGER_GAIN_RED = 8
HUNGER_GAIN_YELLOW = 18
HUNGER_GAIN_PURPLE = 0
HUNGER_GAIN_ORANGE = 12

class Item:
    def __init__(self, kind):
        self.kind   = kind
        self.x      = float(random.randint(ITEM_R, WIDTH - ITEM_R))
        self.y      = float(-ITEM_R * 2)
        self.speed  = ITEM_SPEED
        self.r      = ITEM_R
        self.tick   = 0
        self.being_eaten   = False
        self.eat_progress  = 0

    @property
    def rect(self):
        return pygame.Rect(self.x - self.r, self.y - self.r,
                           self.r * 2, self.r * 2)

    def update(self):
        self.tick += 1
        if not self.being_eaten:
            self.y += self.speed
        return self.y - self.r < HEIGHT

    def pull_toward(self, px, py):
        self.being_eaten  = True
        self.eat_progress += 1
        dx = px - self.x
        dy = py - self.y
        d  = max(1, math.hypot(dx, dy))
        pull = 6 + self.eat_progress * 0.8
        self.x += dx / d * pull
        self.y += dy / d * pull
        dist = math.hypot(self.x - px, self.y - py)
        return self.eat_progress >= 18 or dist < 20

    def draw(self, surface):
        scale = 1.0
        if self.being_eaten:
            scale = max(0.2, 1.0 - (self.eat_progress / 18) * 0.8)

        r = max(1, int(self.r * scale))

        bubble = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        wobble = 0.06 * math.sin(self.tick * 0.12)
        if self.kind == "heart":
            bubble_color = (255, 180, 200, 60)
            rim_color    = (255, 120, 160, 180)
        else:
            bubble_color = (160, 220, 255, 60)
            rim_color    = (80, 180, 255, 180)

        cx = r + 2
        cy = r + 2
        pygame.draw.circle(bubble, bubble_color, (cx, cy), r)
        pygame.draw.circle(bubble, rim_color,    (cx, cy), r, 2)

        hl_r = max(1, r // 4)
        pygame.draw.circle(bubble, (255, 255, 255, 120),
                           (cx - r // 3, cy - r // 3), hl_r)

        bx = int(self.x) - r - 2
        by = int(self.y) - r - 2
        surface.blit(bubble, (bx, by))

        icon_r = max(1, int(r * 0.55 * scale))
        if self.kind == "heart":
            self._draw_heart(surface, int(self.x), int(self.y), icon_r)
        else:
            self._draw_swirl(surface, int(self.x), int(self.y), icon_r)

    def _draw_heart(self, surface, cx, cy, size):
        s = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        sc = size * 2
        color = (255, 80, 120, 230)
        off = size // 2
        r2  = size // 2 + 1
        pygame.draw.circle(s, color, (sc - off, sc - off), r2)
        pygame.draw.circle(s, color, (sc + off, sc - off), r2)
        pts = [
            (sc - size, sc - off + 2),
            (sc + size, sc - off + 2),
            (sc,        sc + size),
        ]
        pygame.draw.polygon(s, color, pts)
        surface.blit(s, (cx - size * 2, cy - size * 2))

    def _draw_swirl(self, surface, cx, cy, size):
        angle_offset = self.tick * 4
        for i in range(3):
            base_angle = math.radians(angle_offset + i * 120)
            arc_r = size * (1.0 - i * 0.2)
            if arc_r < 2:
                continue
            color_alpha = 230 - i * 40
            color = (80, 200, 255, color_alpha)
            rect = pygame.Rect(cx - arc_r, cy - arc_r, arc_r * 2, arc_r * 2)
            start = base_angle
            end   = base_angle + math.pi * 1.3
            pygame.draw.arc(surface, (80, 200, 255), rect,
                    min(start, end), max(start, end), 2)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 파티클 클래스
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AbsorbParticle:
    def __init__(self, x, y, target_rect, color):
        self.x = float(x)
        self.y = float(y)
        self.target = target_rect
        self.color = color
        self.life = 1.0
        self.size = random.randint(4, 9)
        offset_x = random.uniform(-15, 15)
        offset_y = random.uniform(-15, 15)
        self.start_x = x + offset_x
        self.start_y = y + offset_y
        self.x = self.start_x
        self.y = self.start_y
        self.progress = 0.0
        self.speed = random.uniform(0.04, 0.08)

    def update(self):
        self.progress += self.speed
        self.life = 1.0 - self.progress
        tx = self.target.centerx
        ty = self.target.centery
        self.x = self.start_x + (tx - self.start_x) * self.progress
        self.y = self.start_y + (ty - self.start_y) * self.progress
        return self.progress < 1.0

    def draw(self, surface):
        alpha = int(self.life * 255)
        size = max(1, int(self.size * self.life))
        r = min(255, self.color[0])
        g = min(255, self.color[1])
        b = min(255, self.color[2])
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (r, g, b, alpha), (size, size), size)
        surface.blit(s, (int(self.x) - size, int(self.y) - size))


class ScorePopup:
    def __init__(self, x, y, text="+1", color=(255, 100, 180)):
        self.x = float(x)
        self.y = float(y)
        self.text = text
        self.color = color
        self.life = 1.0
        self.vy = -2.0
        self.font = get_korean_font(30)

    def update(self):
        self.life -= 0.025
        self.y += self.vy
        self.vy *= 0.95
        return self.life > 0

    def draw(self, surface):
        alpha = int(self.life * 255)
        s = pygame.Surface((200, 40), pygame.SRCALPHA)
        txt = self.font.render(self.text, True, (*self.color, alpha))
        s.blit(txt, (0, 0))
        surface.blit(s, (int(self.x) - 30, int(self.y)))


class EatRing:
    def __init__(self, center, max_r=80):
        self.center = center
        self.max_r = max_r
        self.r = float(max_r)
        self.life = 1.0

    def update(self):
        self.life -= 0.07
        self.r = self.max_r * self.life
        return self.life > 0

    def draw(self, surface):
        if self.r < 2:
            return
        alpha = int(self.life * 200)
        s = pygame.Surface((self.max_r * 2 + 4, self.max_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 100, 180, alpha),
                           (self.max_r + 2, self.max_r + 2),
                           int(self.r), 2)
        surface.blit(s, (int(self.center[0]) - self.max_r - 2,
                         int(self.center[1]) - self.max_r - 2))


class FlashBurst:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.life = 1.0
        self.max_r = 20

    def update(self):
        self.life -= 0.12
        return self.life > 0

    def draw(self, surface):
        r = int(self.max_r * (1.0 - self.life))
        alpha = int(self.life * 180)
        if r < 1:
            return
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (r + 1, r + 1), r)
        surface.blit(s, (self.x - r - 1, self.y - r - 1))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 보라색 적 폭발 파티클
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PurpleExplosionParticle:
    """보라색 적이 폭발할 때 튀어나오는 파티클"""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(3, 9)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.size = random.randint(4, 10)
        self.color = random.choice([
            (200, 80, 255), (160, 40, 220), (255, 120, 255),
            (120, 0, 200), (220, 150, 255)
        ])

    def update(self):
        self.life -= 0.04
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.92
        self.vy *= 0.92
        return self.life > 0

    def draw(self, surface):
        alpha = int(self.life * 255)
        size = max(1, int(self.size * self.life))
        s = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (size + 1, size + 1), size)
        surface.blit(s, (int(self.x) - size - 1, int(self.y) - size - 1))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 주황색 적 경보 기둥
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class OrangeWarningPillar:
    """주황색 적이 강하하기 전에 표시되는 경보 기둥 — 플레이어를 실시간 추적"""
    WARN_DURATION = FPS * 3  # 3초

    def __init__(self, player_ref):
        self.player_ref = player_ref   # player Rect 참조 (실시간 추적용)
        self.x = float(player_ref.centerx)
        self.timer = 0
        self.done = False
        self.final_x = None            # 카운트 완료 시 확정 X

    @property
    def countdown(self):
        remaining = self.WARN_DURATION - self.timer
        return max(0, math.ceil(remaining / FPS))

    def update(self):
        self.timer += 1
        # 마지막 0.5초(30프레임) 전까지는 플레이어를 추적
        if self.timer < self.WARN_DURATION - 30:
            self.x = float(self.player_ref.centerx)
        if self.timer >= self.WARN_DURATION:
            self.final_x = int(self.x)
            self.done = True
        return not self.done

    def draw(self, surface):
        ratio = self.timer / self.WARN_DURATION
        alpha = int(100 + 80 * math.sin(self.timer * 0.25))
        cx = int(self.x)

        # 마지막 30프레임은 빠르게 깜빡이며 "확정" 표시
        locked = self.timer >= self.WARN_DURATION - 30
        if locked and (self.timer // 4) % 2 == 0:
            return  # 빠른 깜빡임으로 위험 강조

        # 기둥 (화면 위부터 아래까지)
        pillar_w = 32
        pillar_surf = pygame.Surface((pillar_w, HEIGHT), pygame.SRCALPHA)
        pillar_color = (255, 140, 0, max(20, alpha // 3))
        pillar_surf.fill(pillar_color)
        surface.blit(pillar_surf, (cx - pillar_w // 2, 0))

        # 외곽선
        line_s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(line_s, (255, 140, 0, alpha),
                         (cx - pillar_w // 2, 0),
                         (cx - pillar_w // 2, HEIGHT), 1)
        pygame.draw.line(line_s, (255, 140, 0, alpha),
                         (cx + pillar_w // 2, 0),
                         (cx + pillar_w // 2, HEIGHT), 1)
        surface.blit(line_s, (0, 0))

        # 카운트다운 숫자
        count = self.countdown
        count_font = get_korean_font(48)
        count_surf = count_font.render(str(count), True, (255, 200, 80))
        tx = cx - count_surf.get_width() // 2
        if (self.timer // 15) % 2 == 0:
            surface.blit(count_surf, (tx, HEIGHT // 2 - 30))

        # 경고 삼각형 (화살표)
        tip_y = 20 + int(math.sin(self.timer * 0.15) * 10)
        tri_pts = [
            (cx,      tip_y + 30),
            (cx - 12, tip_y),
            (cx + 12, tip_y),
        ]
        tri_alpha = min(255, alpha + 60)
        ts = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(ts, (255, 160, 0, tri_alpha), tri_pts)
        surface.blit(ts, (0, 0))


class LevelUpBanner:
    DURATION = 120

    def __init__(self, label):
        text = f"LEVEL UP!  {label}"
        self.surf = font_big.render(text, True, YELLOW)
        self.timer = 0
        self.w = self.surf.get_width()

    def update(self):
        self.timer += 1
        return self.timer < self.DURATION

    def draw(self, surface):
        t = self.timer / self.DURATION
        if t < 0.3:
            progress = t / 0.3
            x = WIDTH + self.w - (WIDTH + self.w - (WIDTH // 2 - self.w // 2)) * self._ease_out(progress)
        elif t < 0.7:
            x = WIDTH // 2 - self.w // 2
        else:
            progress = (t - 0.7) / 0.3
            x = (WIDTH // 2 - self.w // 2) - (WIDTH // 2 - self.w // 2 + self.w + WIDTH) * self._ease_in(progress)

        alpha = 255
        if t > 0.8:
            alpha = int(255 * (1.0 - (t - 0.8) / 0.2))

        s = pygame.Surface((self.surf.get_width(), self.surf.get_height()), pygame.SRCALPHA)
        s.blit(self.surf, (0, 0))
        s.set_alpha(alpha)
        surface.blit(s, (int(x), HEIGHT // 2 - self.surf.get_height() // 2))

    def _ease_out(self, t): return 1 - (1 - t) ** 2
    def _ease_in(self,  t): return t ** 2


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 헬퍼 함수들
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def spawn_enemy(level_cfg):
    x = random.randint(0, WIDTH - ENEMY_W)
    speed = random.randint(level_cfg["min_speed"], level_cfg["max_speed"])
    return [pygame.Rect(x, -ENEMY_H, ENEMY_W, ENEMY_H), speed, "red", "", [0, 0], 0]

def spawn_yellow_enemy():
    x = random.randint(0, WIDTH - ENEMY_W)
    rect = pygame.Rect(x, -ENEMY_H, ENEMY_W, ENEMY_H)
    return [rect, 4, "yellow", "fall", [0, 0], 0]

def spawn_purple_enemy():
    """보라색 적: 먹으면 폭발해서 체력 -1, 점수 없음"""
    x = random.randint(0, WIDTH - ENEMY_W)
    speed = random.randint(3, 6)
    rect = pygame.Rect(x, -ENEMY_H, ENEMY_W, ENEMY_H)
    return [rect, speed, "purple", "fall", [0, 0], 0]


def draw_dashed_line(surface, color, start_pos, end_pos, dash_length=10):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = x2 - x1; dy = y2 - y1
    dist = max(1, (dx**2 + dy**2) ** 0.5)
    dx /= dist; dy /= dist
    for i in range(0, int(dist), dash_length * 2):
        s = (x1 + dx * i,              y1 + dy * i)
        e = (x1 + dx * (i+dash_length), y1 + dy * (i+dash_length))
        pygame.draw.line(surface, color, s, e, 2)

def draw_hud(surface, score, last_gain, level_cfg, lives, eat_cooldown, player_rect,
             eat_boost_timer, hunger):
    score_base = font.render(f"Score: {score}", True, WHITE)
    score_x = WIDTH // 2 - score_base.get_width() // 2
    surface.blit(score_base, (score_x, 10))

    if last_gain > 0:
        gain_surf = font_small.render(f"+{last_gain}", True, (255, 200, 80))
        surface.blit(gain_surf, (score_x + score_base.get_width() + 6, 14))

    lives_text = font.render(f"{'♥ ' * lives}", True, RED)
    surface.blit(lives_text, (WIDTH - lives_text.get_width() - 50, 10))

    surface.blit(font.render(level_cfg['label'], True, YELLOW), (10, HEIGHT - 44))

    if eat_boost_timer > 0:
        secs = math.ceil(eat_boost_timer / FPS)
        boost_surf = font_small.render(f"EAT BOOST  {secs}s", True, (80, 220, 255))
        surface.blit(boost_surf, (10, 10))

    cx, cy = player_rect.centerx, player_rect.centery
    RING_R = 38
    pygame.draw.circle(surface, (80, 80, 80), (cx, cy), RING_R, 3)
    ratio = 1.0 - eat_cooldown / 60
    if ratio > 0:
        arc_rect = pygame.Rect(cx - RING_R, cy - RING_R, RING_R * 2, RING_R * 2)
        start_angle = math.pi / 2
        end_angle   = start_angle - ratio * 2 * math.pi
        pygame.draw.arc(surface, (255, 100, 180), arc_rect,
                        min(start_angle, end_angle),
                        max(start_angle, end_angle), 3)

    if eat_boost_timer > 0:
        pulse = int(math.sin(pygame.time.get_ticks() * 0.01) * 4)
        pygame.draw.circle(surface, (80, 220, 255), (cx, cy), RING_R + 8 + pulse, 2)

    # ── 허기 게이지
    bar_w = 22
    bar_h = 360
    bar_x = WIDTH - 34
    bar_y = HEIGHT // 2 - bar_h // 2

    hunger_ratio = max(0.0, min(1.0, hunger / HUNGER_MAX))

    if hunger_ratio > 0.6:
        hunger_color = (80, 220, 120)
    elif hunger_ratio > 0.3:
        hunger_color = (255, 190, 60)
    else:
        hunger_color = (255, 90, 90)

    hunger_label = font_small.render("허기", True, WHITE)
    surface.blit(hunger_label, (bar_x - hunger_label.get_width() // 2 + bar_w // 2, bar_y - 30))

    pygame.draw.rect(surface, (70, 70, 70), (bar_x, bar_y, bar_w, bar_h), border_radius=8)
    pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=8)

    fill_h = int(bar_h * hunger_ratio)
    if fill_h > 0:
        fill_rect = pygame.Rect(bar_x + 3, bar_y + bar_h - fill_h + 3, bar_w - 6, fill_h - 6)
        if fill_rect.height > 0:
            pygame.draw.rect(surface, hunger_color, fill_rect, border_radius=6)

    if hunger_ratio <= 0.2 and (pygame.time.get_ticks() // 180) % 2 == 0:
        warning = font_small.render("EMPTY", True, RED)
        surface.blit(warning, (bar_x - warning.get_width() - 8, bar_y + bar_h - 20))

def game_over_screen(score):
    screen.fill(GRAY)
    screen.blit(font_big.render("GAME OVER", True, RED),    (220, 220))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (350, 310))
    screen.blit(font.render("R: Restart   Q: Quit", True, WHITE), (270, 360))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 메인 루프
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    player = pygame.Rect(WIDTH // 2, HEIGHT - 80, PLAYER_W, PLAYER_H)

    frame_index = 0
    frame_timer = 0
    facing_left = False

    eat_active    = 0
    eat_cooldown  = 0
    eat_boost_timer = 0

    absorb_particles = []
    score_popups     = []
    eat_rings        = []
    flash_bursts     = []
    purple_explosion_particles = []

    enemies      = []
    items        = []
    item_eaten   = {}
    item_spawn_timer = 0

    # 주황색 경보 기둥과 대기 중인 낙하 적
    orange_pillars   = []   # OrangeWarningPillar 인스턴스들
    orange_pending   = []   # (pillar_x) → 기둥이 완료되면 실제 enemy 생성

    score = 0
    last_gain = 0
    last_gain_timer = 0
    lives = 4
    hunger = HUNGER_MAX
    spawn_timer = 0
    level_idx   = 0
    level_cfg   = LEVELS[level_idx]
    invincible  = 0
    level_up_banners = []

    being_eaten = {}

    game_surface = pygame.Surface((WIDTH, HEIGHT))
    shake_timer = 0
    shake_strength = 0

    EAT_RANGE      = 80
    EAT_PULL_TICKS = 18

    # 주황색 적 스폰 타이머 (90~180프레임마다 하나씩)
    orange_spawn_timer = 0
    ORANGE_SPAWN_INTERVAL = random.randint(300, 480)

    # 보라색 적 스폰 확률 (적 스폰 시 15%)
    PURPLE_SPAWN_CHANCE = 0.15
    ORANGE_SPAWN_CHANCE = 0.10

    while True:
        dt = clock.tick(FPS)
        
        prev_eat_boost_timer = eat_boost_timer

        if invincible > 0:
            invincible -= 1
        eat_active   = max(0, eat_active - 1)
        eat_cooldown = max(0, eat_cooldown - 1)
        
        if eat_boost_timer > 0:
            eat_boost_timer -= 1
            eat_active = max(eat_active, 1)
            
        if prev_eat_boost_timer > 0 and eat_boost_timer == 0:
            invincible = max(invincible, 90)
            flash_bursts.append(
                FlashBurst(player.centerx, player.centery, (80, 220, 255))
            )

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and eat_cooldown <= 0:
            eat_active   = 20
            eat_cooldown = 60
            eat_rings.append(EatRing(player.center, EAT_RANGE))
            eat_rings.append(EatRing(player.center, EAT_RANGE * 0.6))

        moving = False
        if keys[pygame.K_LEFT]  and player.left  > 0:
            player.x -= 5; moving = True; facing_left = True
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += 5; moving = True; facing_left = False

        current_frames = walk_frames if moving else idle_frames
        current_delay  = WALK_FRAME_DELAY if moving else IDLE_FRAME_DELAY

        frame_timer += dt
        if frame_timer >= current_delay:
            frame_timer = 0
            frame_index = (frame_index + 1) % len(current_frames)
        frame_index = frame_index % len(current_frames)

        # 노란색 ↔ 주황색은 화면에 동시에 존재하지 않음
        yellow_on_screen = any(e[2] == "yellow" for e in enemies)
        orange_on_screen = len(orange_pillars) > 0 or any(e[2] == "orange" for e in enemies)

        # 레벨별 적 해금
        yellow_unlocked = level_idx >= 2   # Lv.3 (인덱스 2)부터
        special_unlocked = level_idx >= 4  # Lv.5 (인덱스 4)부터 주황/보라

        # ── 적 스폰 ──────────────────────────────────────
        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            roll = random.random()
            if special_unlocked and roll < ORANGE_SPAWN_CHANCE and not orange_on_screen and not yellow_on_screen:
                orange_pillars.append(OrangeWarningPillar(player))
            elif special_unlocked and roll < ORANGE_SPAWN_CHANCE + PURPLE_SPAWN_CHANCE:
                enemies.append(spawn_purple_enemy())
            elif yellow_unlocked and roll < ORANGE_SPAWN_CHANCE + PURPLE_SPAWN_CHANCE + 0.2 and not orange_on_screen:
                enemies.append(spawn_yellow_enemy())
            else:
                enemies.append(spawn_enemy(level_cfg))

        # ── 주황색 경보 기둥 업데이트 ─────────────────────
        new_pillars = []
        for pillar in orange_pillars:
            if pillar.update():
                new_pillars.append(pillar)
            else:
                # 카운트 완료 → 확정된 X에서 speed=28 초고속 낙하
                x = pillar.final_x
                rect = pygame.Rect(x - ENEMY_W // 2, -ENEMY_H, ENEMY_W, ENEMY_H)
                enemies.append([rect, 28, "orange", "dash", [0, 1], 0])
        orange_pillars = new_pillars

        # ── 아이템 스폰 ──────────────────────────────────
        item_spawn_timer += 1
        if item_spawn_timer >= ITEM_SPAWN_INTERVAL:
            item_spawn_timer = 0

            if lives >= MAX_LIVES:
                kind = "swirl" if random.random() < 0.4 else None
            else:
                kind = "heart" if random.random() < 0.8 else "swirl"

            if kind:
                items.append(Item(kind))

        # ── 아이템 업데이트 & 먹기 처리 ─────────────────
        new_items = []
        for item in items:
            iid = id(item)

            if eat_active > 0 and iid not in item_eaten:
                dist = math.hypot(item.x - player.centerx,
                                  item.y - player.centery)
                if dist <= EAT_RANGE:
                    item_eaten[iid] = item
                    for _ in range(10):
                        if item.kind == "heart":
                            pcol = (255, 100, 140)
                        else:
                            pcol = (80, 200, 255)
                        absorb_particles.append(
                            AbsorbParticle(item.x, item.y, player, pcol))

            if iid in item_eaten:
                absorbed = item.pull_toward(player.centerx, player.centery)
                if absorbed:
                    if item.kind == "heart":
                        lives = min(lives + 1, 9)
                        flash_bursts.append(
                            FlashBurst(player.centerx, player.centery, (255, 100, 140)))
                        score_popups.append(
                            ScorePopup(item.x, item.y - 10, "♥ +1", (255, 100, 140)))
                    else:
                        eat_boost_timer = FPS * 5
                        eat_active = max(eat_active, 1)
                        for _ in range(3):
                            eat_rings.append(
                                EatRing(player.center, EAT_RANGE * (1 + _ * 0.3)))
                        flash_bursts.append(
                            FlashBurst(player.centerx, player.centery, (80, 200, 255)))
                        score_popups.append(
                            ScorePopup(item.x, item.y - 10, "EAT x5s!", (80, 200, 255)))
                    del item_eaten[iid]
                    continue
                else:
                    if item.update():
                        new_items.append(item)
                    else:
                        del item_eaten[iid]
            else:
                if item.update():
                    new_items.append(item)

        items = new_items

        # ── 적 이동 ──────────────────────────────────────
        survived = []
        for e in enemies:
            rect = e[0]
            eid  = id(rect)

            if eat_active > 0:
                dist = math.hypot(rect.centerx - player.centerx,
                                  rect.centery - player.centery)
                if dist <= EAT_RANGE:
                    if eid not in being_eaten:
                        being_eaten[eid] = 0
                        particle_color = (255, 100, 180)
                        if e[2] == "purple":
                            particle_color = (200, 80, 255)
                        elif e[2] == "orange":
                            particle_color = (255, 160, 40)
                        for _ in range(8):
                            absorb_particles.append(
                                AbsorbParticle(rect.centerx, rect.centery,
                                               player, particle_color))

            if eid in being_eaten:
                being_eaten[eid] += 1
                dx = player.centerx - rect.centerx
                dy = player.centery - rect.centery
                d  = max(1, math.hypot(dx, dy))
                pull = 6 + being_eaten[eid] * 0.8
                rect.x += int(dx / d * pull)
                rect.y += int(dy / d * pull)

                if being_eaten[eid] >= EAT_PULL_TICKS or \
                   math.hypot(rect.centerx - player.centerx,
                               rect.centery - player.centery) < 20:

                    color_type = e[2]

                    if color_type == "purple":
                        # ★ 보라색: 폭발 → 체력 -1, 점수 없음
                        lives -= 1
                        invincible = max(invincible, 90)
                        shake_timer = 20
                        shake_strength = 10
                        # 폭발 파티클 다량 생성
                        for _ in range(25):
                            purple_explosion_particles.append(
                                PurpleExplosionParticle(player.centerx, player.centery))
                        flash_bursts.append(
                            FlashBurst(player.centerx, player.centery, (200, 80, 255)))
                        score_popups.append(
                            ScorePopup(rect.centerx, rect.centery - 10,
                                       "BOOM! ♥-1", (200, 80, 255)))
                        hunger = min(HUNGER_MAX, hunger + HUNGER_GAIN_PURPLE)
                        if lives <= 0:
                            del being_eaten[eid]
                            if game_over_screen(score): main()
                            return

                    elif color_type == "orange":
                        # ★ 주황색: 먹기 쿨타임 초기화, 점수 +10
                        eat_cooldown = 0
                        gain = 10
                        score += gain
                        last_gain = gain
                        last_gain_timer = 90
                        hunger = min(HUNGER_MAX, hunger + HUNGER_GAIN_ORANGE)
                        flash_bursts.append(
                            FlashBurst(player.centerx, player.centery, (255, 160, 40)))
                        score_popups.append(
                            ScorePopup(rect.centerx, rect.centery - 10,
                                       f"+{gain} COOLDOWN!", (255, 160, 40)))

                    else:
                        is_red = color_type == "red"
                        gain = 2 if is_red else 5
                        score += gain
                        last_gain = gain
                        last_gain_timer = 90
                        hunger_gain = HUNGER_GAIN_RED if is_red else HUNGER_GAIN_YELLOW
                        hunger = min(HUNGER_MAX, hunger + hunger_gain)
                        flash_bursts.append(
                            FlashBurst(player.centerx, player.centery, (255, 100, 180)))
                        score_popups.append(
                            ScorePopup(rect.centerx, rect.centery - 10,
                                       f"+{gain}",
                                       RED if is_red else YELLOW))

                    del being_eaten[eid]
                    continue
            else:
                if e[2] == "red":
                    rect.y += e[1]
                elif e[2] == "purple":
                    # 보라색: 천천히 낙하
                    rect.y += e[1]
                elif e[2] == "yellow":
                    if e[3] == "fall":
                        rect.y += e[1]
                        if rect.y > 150:
                            e[3] = "warn"; e[5] = 0
                    elif e[3] == "warn":
                        e[5] += 1
                        if e[5] > 30:
                            dx = player.centerx - rect.centerx
                            dy = player.centery - rect.centery
                            d2 = max(1, (dx**2 + dy**2) ** 0.5)
                            e[4] = [dx / d2, dy / d2]
                            e[3] = "dash"
                    elif e[3] == "dash":
                        rect.x += int(e[4][0] * 10)
                        rect.y += int(e[4][1] * 10)
                elif e[2] == "orange":
                    # 주황색: 직선 초고속 낙하 (아래로만)
                    rect.y += e[1]

            if rect.top < HEIGHT:
                survived.append(e)
            else:
                if eid in being_eaten: del being_eaten[eid]
                if e[2] == "red": score += 1

        enemies = survived

        # ── 충돌 ─────────────────────────────────────────
        new_enemies = []
        for e in enemies:
            rect = e[0]; eid = id(rect)
            if eid in being_eaten:
                new_enemies.append(e); continue
            if invincible <= 0 and player.colliderect(rect):
                if e[2] == "purple":
                    # 보라색 충돌: 폭발 즉시
                    lives -= 1
                    invincible = 90
                    shake_timer = 20
                    shake_strength = 10
                    for _ in range(25):
                        purple_explosion_particles.append(
                            PurpleExplosionParticle(player.centerx, player.centery))
                    flash_bursts.append(
                        FlashBurst(player.centerx, player.centery, (200, 80, 255)))
                    score_popups.append(
                        ScorePopup(rect.centerx, rect.centery - 10,
                                   "BOOM! ♥-1", (200, 80, 255)))
                    being_eaten.clear()
                    enemies.clear()
                    if lives <= 0:
                        if game_over_screen(score): main()
                        return
                    continue
                else:
                    # 주황색 충돌: 체력 2 감소
                    if e[2] == "orange":
                        lives -= 2
                        shake_timer = 22
                        shake_strength = 14
                        score_popups.append(
                            ScorePopup(rect.centerx, rect.centery - 10,
                                       "♥♥ -2", (255, 140, 0)))
                    else:
                        lives -= 1
                        shake_timer = 18
                        shake_strength = 12
                    invincible = 90
                    being_eaten.clear(); enemies.clear()

                    if lives <= 0:
                        if game_over_screen(score): main()
                        return
                    continue
            new_enemies.append(e)
        enemies = new_enemies

        new_level_idx = 0
        for i, threshold in enumerate(LEVEL_SCORE_THRESHOLDS):
            if score >= threshold:
                new_level_idx = i
        new_level_idx = min(new_level_idx, len(LEVELS) - 1)
        if new_level_idx > level_idx:
            level_up_banners.append(LevelUpBanner(LEVELS[new_level_idx]['label']))
        level_idx = new_level_idx
        level_cfg = LEVELS[level_idx]

        hunger -= HUNGER_DRAIN_BY_LEVEL[level_idx]
        hunger = max(0, hunger)

        if hunger <= 0:
            if game_over_screen(score): main()
            return

        if last_gain_timer > 0: last_gain_timer -= 1
        else:                   last_gain = 0

        if shake_timer > 0:
            shake_timer -= 1

        level_up_banners          = [b for b in level_up_banners          if b.update()]
        absorb_particles          = [p for p in absorb_particles          if p.update()]
        score_popups              = [p for p in score_popups              if p.update()]
        eat_rings                 = [r for r in eat_rings                 if r.update()]
        flash_bursts              = [f for f in flash_bursts              if f.update()]
        purple_explosion_particles = [p for p in purple_explosion_particles if p.update()]

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 그리기
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        game_surface.fill(GRAY)

        # 주황색 경보 기둥 (배경 레이어에)
        for pillar in orange_pillars:
            pillar.draw(game_surface)

        for ring in eat_rings:
            ring.draw(game_surface)

        for item in items:
            item.draw(game_surface)

        blink = (invincible // 10) % 2 == 0
        if blink:
            raw_frame = current_frames[frame_index]
            frame_img = pygame.transform.scale(raw_frame, (player.width, player.height))
            if facing_left:
                frame_img = pygame.transform.flip(frame_img, True, False)
            game_surface.blit(frame_img, player.topleft)

            if eat_active > 0:
                pulse = int((1.0 - (eat_active % 20) / 20) * 10)
                ec = (80, 220, 255) if eat_boost_timer > 0 else (255, 100, 180)
                pygame.draw.circle(game_surface, ec, player.center, EAT_RANGE + pulse, 1)
                s = pygame.Surface((EAT_RANGE * 2, EAT_RANGE * 2), pygame.SRCALPHA)
                fill_c = (*ec, 30)
                pygame.draw.circle(s, fill_c, (EAT_RANGE, EAT_RANGE), EAT_RANGE)
                game_surface.blit(s, (player.centerx - EAT_RANGE,
                                      player.centery - EAT_RANGE))

        for e in enemies:
            eid  = id(e[0])
            rect = e[0]
            color_type = e[2]

            if color_type == "purple":
                base_color = PURPLE
            elif color_type == "orange":
                base_color = ORANGE
            elif color_type == "red":
                base_color = RED
            else:
                base_color = YELLOW

            if eid in being_eaten:
                progress = being_eaten[eid] / EAT_PULL_TICKS
                scale    = max(0.2, 1.0 - progress * 0.8)
                w = max(1, int(rect.width  * scale))
                h = max(1, int(rect.height * scale))

                if color_type == "purple":
                    # 보라색: 육각형 느낌으로 (원으로 표현)
                    r_shrink = max(1, int(min(w, h) // 2))
                    ps = pygame.Surface((r_shrink*2+2, r_shrink*2+2), pygame.SRCALPHA)
                    # 경고 효과: 깜빡임
                    pulse_alpha = int(200 + 55 * math.sin(pygame.time.get_ticks() * 0.03))
                    pygame.draw.circle(ps, (*PURPLE, pulse_alpha),
                                       (r_shrink+1, r_shrink+1), r_shrink)
                    game_surface.blit(ps, (rect.centerx - r_shrink - 1,
                                           rect.centery - r_shrink - 1))
                else:
                    pygame.draw.rect(game_surface, base_color,
                                     pygame.Rect(rect.centerx - w//2,
                                                 rect.centery - h//2, w, h))
            else:
                if color_type == "purple":
                    # 보라색: 원형 + 테두리로 위협적으로 표현
                    r = ENEMY_W // 2
                    tick_v = pygame.time.get_ticks()
                    pulse = int(3 * math.sin(tick_v * 0.008))
                    pygame.draw.circle(game_surface, PURPLE,
                                       rect.center, r + pulse)
                    pygame.draw.circle(game_surface, (220, 150, 255),
                                       rect.center, r + pulse, 2)
                    # 가운데 해골 대신 X 표시
                    cx2, cy2 = rect.center
                    sz = 6
                    pygame.draw.line(game_surface, (255, 220, 255),
                                     (cx2-sz, cy2-sz), (cx2+sz, cy2+sz), 2)
                    pygame.draw.line(game_surface, (255, 220, 255),
                                     (cx2+sz, cy2-sz), (cx2-sz, cy2+sz), 2)

                elif color_type == "orange":
                    # 주황색: 빠른 낙하 - 불꽃 느낌으로
                    r = ENEMY_W // 2
                    # 속도선 (trail)
                    trail_len = 30
                    trail_s = pygame.Surface((ENEMY_W + 4, trail_len), pygame.SRCALPHA)
                    for t in range(trail_len):
                        alpha_t = int(150 * (1 - t / trail_len))
                        w_t = max(1, int((ENEMY_W - 4) * (1 - t / trail_len)))
                        pygame.draw.rect(trail_s, (255, 140 + t*2, 0, alpha_t),
                                         (ENEMY_W // 2 - w_t // 2 + 2, t, w_t, 2))
                    game_surface.blit(trail_s, (rect.left - 2, rect.top - trail_len))
                    # 본체
                    pygame.draw.circle(game_surface, ORANGE, rect.center, r)
                    pygame.draw.circle(game_surface, (255, 220, 80), rect.center, r, 2)
                    # 번개 표시
                    cx2, cy2 = rect.center
                    bolt = [(cx2+2, cy2-8), (cx2-2, cy2-1), (cx2+3, cy2-1), (cx2-3, cy2+8)]
                    pygame.draw.lines(game_surface, (255, 255, 180), False, bolt, 2)

                elif color_type == "yellow":
                    if e[3] == "warn":
                        if (e[5] // 5) % 2 == 0:
                            pygame.draw.rect(game_surface, YELLOW, rect)
                        draw_dashed_line(game_surface, YELLOW, rect.center,
                                         player.center, dash_length=8)
                    else:
                        pygame.draw.rect(game_surface, YELLOW, rect)
                else:
                    pygame.draw.rect(game_surface, RED, rect)

        for p in absorb_particles:
            p.draw(game_surface)
        for p in purple_explosion_particles:
            p.draw(game_surface)
        for f in flash_bursts:
            f.draw(game_surface)
        for popup in score_popups:
            popup.draw(game_surface)
        for banner in level_up_banners:
            banner.draw(game_surface)

        draw_hud(game_surface, score, last_gain, level_cfg, lives, eat_cooldown, player,
                 eat_boost_timer, hunger)

        screen.fill(BLACK)
        shake_x, shake_y = 0, 0
        if shake_timer > 0:
            shake_x = random.randint(-shake_strength, shake_strength)
            shake_y = random.randint(-shake_strength, shake_strength)

        screen.blit(game_surface, (shake_x, shake_y))
        pygame.display.flip()

def title_screen():
    font_title = get_korean_font(80)
    font_sub   = get_korean_font(32)
    font_guide = get_korean_font(26)
    PINK = (255, 100, 180)
    DIM  = (160, 160, 160)
    tick = 0

    while True:
        clock.tick(FPS)
        tick += 1

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r: return

        screen.fill(GRAY)

        title_surf = font_title.render("Hungry Slime", True, PINK)
        tx = WIDTH // 2 - title_surf.get_width() // 2
        ty = 140 + int(math.sin(tick * 0.05) * 6)
        screen.blit(title_surf, (tx, ty))
        pygame.draw.line(screen, PINK,
                         (tx, ty + title_surf.get_height() + 4),
                         (tx + title_surf.get_width(),
                          ty + title_surf.get_height() + 4), 3)

        if (tick // 30) % 2 == 0:
            r_surf = font_sub.render("Press  R  to  Game Start", True, WHITE)
            screen.blit(r_surf, (WIDTH // 2 - r_surf.get_width() // 2, 290))

        guides = [
            ("←  →",  "방향키로 이동"),
            ("SPACE",  "먹기"),
            ("🟣 보라색", "먹으면 폭발! ♥-1"),
            ("🟠 주황색", "3초 후 낙하! 먹으면 쿨타임 초기화"),
        ]
        base_y = 360
        for i, (key_txt, desc_txt) in enumerate(guides):
            y  = base_y + i * 44
            ks = font_guide.render(key_txt,  True, PINK)
            ss = font_guide.render("  :  ",  True, DIM)
            ds = font_guide.render(desc_txt, True, WHITE)
            total_w = ks.get_width() + ss.get_width() + ds.get_width()
            x = WIDTH // 2 - total_w // 2
            screen.blit(ks, (x, y))
            screen.blit(ss, (x + ks.get_width(), y))
            screen.blit(ds, (x + ks.get_width() + ss.get_width(), y))

        pygame.display.flip()

title_screen()
main()

