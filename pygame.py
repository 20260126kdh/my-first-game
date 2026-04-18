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

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodger")
clock = pygame.time.Clock()

font = get_korean_font(36)
font_big = get_korean_font(72)
font_small = get_korean_font(22)

LEVELS = [
    {"min_speed": 3, "max_speed": 5, "spawn": 40, "label": "Lv.1"},
    {"min_speed": 5, "max_speed": 8, "spawn": 25, "label": "Lv.2"},
    {"min_speed": 7, "max_speed": 12, "spawn": 15, "label": "Lv.3"},
]

PLAYER_W, PLAYER_H = 50, 50
ENEMY_W, ENEMY_H = 30, 30

FRAME_W, FRAME_H = 24, 24
COLS = 3
FRAME_DELAY = 120

sheet_bytes = base64.b64decode(SHEET_B64)
player_sheet = pygame.image.load(io.BytesIO(sheet_bytes)).convert_alpha()

player_frames = []
for i in range(9):
    row, col = divmod(i, COLS)
    rect = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
    player_frames.append(player_sheet.subsurface(rect))

walk_frames = player_frames


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 파티클 클래스
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AbsorbParticle:
    """적이 먹힐 때 플레이어 쪽으로 빨려 들어가는 파티클"""
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
    """+N 텍스트가 위로 떠오르는 이펙트"""
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
        s = pygame.Surface((80, 40), pygame.SRCALPHA)
        txt = self.font.render(self.text, True, (*self.color, alpha))
        s.blit(txt, (0, 0))
        surface.blit(s, (int(self.x) - 20, int(self.y)))


class EatRing:
    """먹기 스킬 흡입 링 — 바깥에서 안으로 수축"""
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
    """적이 흡수 완료될 때 작은 플래시"""
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


class LevelUpBanner:
    """화면 오른쪽에서 등장해 왼쪽으로 빠져나가는 레벨업 문구"""
    DURATION = 120  # 총 프레임

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
        # 오른쪽 밖(x=WIDTH)에서 중앙으로 들어왔다가 왼쪽 밖으로 나감
        # 0~0.3 : 진입,  0.3~0.7 : 중앙 정지,  0.7~1.0 : 퇴장
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

    def _ease_out(self, t):
        return 1 - (1 - t) ** 2

    def _ease_in(self, t):
        return t ** 2


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

def draw_dashed_line(surface, color, start_pos, end_pos, dash_length=10):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = x2 - x1
    dy = y2 - y1
    dist = max(1, (dx**2 + dy**2) ** 0.5)
    dx /= dist
    dy /= dist
    for i in range(0, int(dist), dash_length * 2):
        start = (x1 + dx * i, y1 + dy * i)
        end = (x1 + dx * (i + dash_length), y1 + dy * (i + dash_length))
        pygame.draw.line(surface, color, start, end, 2)

def draw_hud(score, last_gain, level_cfg, lives, eat_cooldown, player_rect):
    # ── Score : 화면 상단 가운데 ──
    score_base = font.render(f"Score: {score}", True, WHITE)
    score_x = WIDTH // 2 - score_base.get_width() // 2
    screen.blit(score_base, (score_x, 10))

    # 마지막 획득 점수 표시 (+n)
    if last_gain > 0:
        gain_surf = font_small.render(f"+{last_gain}", True, (255, 200, 80))
        screen.blit(gain_surf, (score_x + score_base.get_width() + 6, 14))

    # ── Lives : 오른쪽 상단 ──
    lives_text = font.render(f"{'♥ ' * lives}", True, RED)
    screen.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))

    # ── Level : 왼쪽 하단 ──
    screen.blit(font.render(level_cfg['label'], True, YELLOW), (10, HEIGHT - 44))

    # ── 먹기 쿨타임 : 플레이어 둘레 원 ──
    cx, cy = player_rect.centerx, player_rect.centery
    RING_R = 38
    # 배경 원 (회색)
    pygame.draw.circle(screen, (80, 80, 80), (cx, cy), RING_R, 3)
    # 채워진 호 (핑크) — 쿨타임 0이면 꽉 참
    ratio = 1.0 - eat_cooldown / 60
    if ratio > 0:
        arc_rect = pygame.Rect(cx - RING_R, cy - RING_R, RING_R * 2, RING_R * 2)
        start_angle = math.pi / 2           # 12시 방향에서 시작
        end_angle   = start_angle - ratio * 2 * math.pi
        pygame.draw.arc(screen, (255, 100, 180), arc_rect,
                        min(start_angle, end_angle),
                        max(start_angle, end_angle), 3)

def game_over_screen(score):
    screen.fill(GRAY)
    screen.blit(font_big.render("GAME OVER", True, RED), (220, 220))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (350, 310))
    screen.blit(font.render("R: Restart   Q: Quit", True, WHITE), (270, 360))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return True
                if e.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 메인 루프
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    player = pygame.Rect(WIDTH // 2, HEIGHT - 80, PLAYER_W, PLAYER_H)

    frame_index = 0
    frame_timer = 0

    eat_active = 0
    eat_cooldown = 0

    # 이펙트 컨테이너
    absorb_particles = []   # AbsorbParticle 목록
    score_popups = []       # ScorePopup 목록
    eat_rings = []          # EatRing 목록
    flash_bursts = []       # FlashBurst 목록

    enemies = []
    score = 0
    last_gain = 0          # 마지막으로 먹은 점수 (Score 옆 표시용)
    last_gain_timer = 0    # 표시 지속 타이머
    lives = 4
    spawn_timer = 0
    level_idx = 0
    level_cfg = LEVELS[level_idx]
    invincible = 0
    level_up_banners = []  # LevelUpBanner 목록

    # 먹기 스킬 흡입 중인 적 추적 {id(rect): 진행도}
    being_eaten = {}  # rect id -> 흡입 진행 틱

    EAT_RANGE = 80        # 흡입 범위 반경 (px)
    EAT_PULL_TICKS = 18   # 흡입에 걸리는 프레임 수

    while True:
        dt = clock.tick(FPS)

        if invincible > 0:
            invincible -= 1
        eat_active = max(0, eat_active - 1)
        eat_cooldown = max(0, eat_cooldown - 1)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and eat_cooldown <= 0:
            eat_active = 20
            eat_cooldown = 60
            eat_rings.append(EatRing(player.center, EAT_RANGE))
            eat_rings.append(EatRing(player.center, EAT_RANGE * 0.6))

        moving = False
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= 5
            moving = True
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += 5
            moving = True

        if moving:
            frame_timer += dt
            if frame_timer >= FRAME_DELAY:
                frame_index = (frame_index + 1) % len(walk_frames)
                frame_timer = 0
        else:
            frame_index = 0

        # 적 스폰
        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            if random.random() < 0.2:
                enemies.append(spawn_yellow_enemy())
            else:
                enemies.append(spawn_enemy(level_cfg))

        # 적 이동
        survived = []
        for e in enemies:
            rect = e[0]
            eid = id(rect)

            # 먹기 스킬 중 범위 안 적 → 흡입 처리
            if eat_active > 0:
                dist = math.hypot(rect.centerx - player.centerx,
                                  rect.centery - player.centery)
                if dist <= EAT_RANGE:
                    if eid not in being_eaten:
                        being_eaten[eid] = 0
                        # 파티클 스폰
                        for _ in range(8):
                            absorb_particles.append(
                                AbsorbParticle(rect.centerx, rect.centery,
                                               player, (255, 100, 180)))

            # being_eaten 이면 플레이어 방향으로 당김
            if eid in being_eaten:
                being_eaten[eid] += 1
                # 플레이어 쪽으로 이동
                dx = player.centerx - rect.centerx
                dy = player.centery - rect.centery
                d = max(1, math.hypot(dx, dy))
                pull = 6 + being_eaten[eid] * 0.8
                rect.x += int(dx / d * pull)
                rect.y += int(dy / d * pull)

                # 완전히 흡수됨
                if being_eaten[eid] >= EAT_PULL_TICKS or \
                   math.hypot(rect.centerx - player.centerx,
                               rect.centery - player.centery) < 20:
                    is_red = e[2] == "red"
                    gain = 2 if is_red else 5
                    score += gain
                    last_gain = gain
                    last_gain_timer = 90
                    popup_text = f"+{gain}"
                    popup_color = RED if is_red else YELLOW
                    flash_bursts.append(FlashBurst(player.centerx, player.centery, (255, 100, 180)))
                    score_popups.append(ScorePopup(rect.centerx, rect.centery - 10, popup_text, popup_color))
                    del being_eaten[eid]
                    continue  # 적 제거
            else:
                # 일반 이동
                if e[2] == "red":
                    rect.y += e[1]
                elif e[2] == "yellow":
                    if e[3] == "fall":
                        rect.y += e[1]
                        if rect.y > 150:
                            e[3] = "warn"
                            e[5] = 0
                    elif e[3] == "warn":
                        e[5] += 1
                        if e[5] > 30:
                            dx = player.centerx - rect.centerx
                            dy = player.centery - rect.centery
                            dist2 = max(1, (dx**2 + dy**2) ** 0.5)
                            e[4] = [dx / dist2, dy / dist2]
                            e[3] = "dash"
                    elif e[3] == "dash":
                        rect.x += int(e[4][0] * 10)
                        rect.y += int(e[4][1] * 10)

            if rect.top < HEIGHT:
                survived.append(e)
            else:
                if eid in being_eaten:
                    del being_eaten[eid]
                if e[2] == "red":
                    score += 1

        enemies = survived

        # 보호막 & 일반 충돌
        new_enemies = []
        for e in enemies:
            rect = e[0]
            eid = id(rect)

            # 흡입 중인 적은 충돌 체크 완전 면제 — 이게 hp 감소 버그 원인
            if eid in being_eaten:
                new_enemies.append(e)
                continue

            if invincible <= 0 and player.colliderect(rect):
                lives -= 1
                invincible = 90
                being_eaten.clear()
                enemies.clear()
                if lives <= 0:
                    if game_over_screen(score):
                        main()
                    return
                continue

            new_enemies.append(e)

        enemies = new_enemies

        new_level_idx = min(score // 20, len(LEVELS) - 1)
        if new_level_idx > level_idx:
            level_up_banners.append(LevelUpBanner(LEVELS[new_level_idx]['label']))
        level_idx = new_level_idx
        level_cfg = LEVELS[level_idx]

        if last_gain_timer > 0:
            last_gain_timer -= 1
        else:
            last_gain = 0

        level_up_banners = [b for b in level_up_banners if b.update()]

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 이펙트 업데이트
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        absorb_particles = [p for p in absorb_particles if p.update()]
        score_popups = [p for p in score_popups if p.update()]
        eat_rings = [r for r in eat_rings if r.update()]
        flash_bursts = [f for f in flash_bursts if f.update()]

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 그리기
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        screen.fill(GRAY)

        # 흡입 링 (적 뒤에 그려서 분위기 연출)
        for ring in eat_rings:
            ring.draw(screen)

        blink = (invincible // 10) % 2 == 0
        if blink:
            frame_img = pygame.transform.scale(
                walk_frames[frame_index],
                (player.width, player.height)
            )
            screen.blit(frame_img, player.topleft)

            # 먹기 이펙트 — 점선 원형 범위 표시
            if eat_active > 0:
                # 바깥 펄스 원
                pulse = int((1.0 - eat_active / 20) * 10)
                pygame.draw.circle(screen, (255, 100, 180),
                                   player.center, EAT_RANGE + pulse, 1)
                # 안쪽 채워진 원 (반투명)
                s = pygame.Surface((EAT_RANGE * 2, EAT_RANGE * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 100, 180, 30),
                                   (EAT_RANGE, EAT_RANGE), EAT_RANGE)
                screen.blit(s, (player.centerx - EAT_RANGE,
                                player.centery - EAT_RANGE))

        # 적 그리기
        for e in enemies:
            eid = id(e[0])
            rect = e[0]

            # 흡입 중인 적은 축소 + 흐릿하게
            if eid in being_eaten:
                progress = being_eaten[eid] / EAT_PULL_TICKS
                scale = max(0.2, 1.0 - progress * 0.8)
                w = max(1, int(rect.width * scale))
                h = max(1, int(rect.height * scale))
                color = RED if e[2] == "red" else YELLOW
                pygame.draw.rect(screen, color,
                                 pygame.Rect(rect.centerx - w//2,
                                             rect.centery - h//2, w, h))
            elif e[2] == "red":
                pygame.draw.rect(screen, RED, rect)
            elif e[2] == "yellow":
                if e[3] == "warn":
                    if (e[5] // 5) % 2 == 0:
                        pygame.draw.rect(screen, YELLOW, rect)
                    draw_dashed_line(screen, YELLOW, rect.center,
                                     player.center, dash_length=8)
                else:
                    pygame.draw.rect(screen, YELLOW, rect)

        # 파티클 그리기
        for p in absorb_particles:
            p.draw(screen)

        # 플래시 버스트
        for f in flash_bursts:
            f.draw(screen)

        # 스코어 팝업
        for popup in score_popups:
            popup.draw(screen)

        # 레벨업 배너
        for banner in level_up_banners:
            banner.draw(screen)

        draw_hud(score, last_gain, level_cfg, lives, eat_cooldown, player)
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
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                return

        screen.fill(GRAY)

        # 제목
        title_surf = font_title.render("Crazy Begin", True, PINK)
        tx = WIDTH // 2 - title_surf.get_width() // 2
        ty = 140 + int(math.sin(tick * 0.05) * 6)
        screen.blit(title_surf, (tx, ty))
        pygame.draw.line(screen, PINK,
                         (tx, ty + title_surf.get_height() + 4),
                         (tx + title_surf.get_width(), ty + title_surf.get_height() + 4), 3)

        # Press R (깜빡임)
        if (tick // 30) % 2 == 0:
            r_surf = font_sub.render("Press  R  to  Game Start", True, WHITE)
            screen.blit(r_surf, (WIDTH // 2 - r_surf.get_width() // 2, 290))

        # 조작 안내
        guides = [
            ("←  →", "방향키로 이동"),
            ("SPACE", "먹기"),
        ]
        base_y = 370
        for i, (key_txt, desc_txt) in enumerate(guides):
            y = base_y + i * 48
            key_surf  = font_guide.render(key_txt,  True, PINK)
            sep_surf  = font_guide.render("  :  ",   True, DIM)
            desc_surf = font_guide.render(desc_txt, True, WHITE)
            total_w = key_surf.get_width() + sep_surf.get_width() + desc_surf.get_width()
            x = WIDTH // 2 - total_w // 2
            screen.blit(key_surf,  (x, y))
            screen.blit(sep_surf,  (x + key_surf.get_width(), y))
            screen.blit(desc_surf, (x + key_surf.get_width() + sep_surf.get_width(), y))

        pygame.display.flip()


title_screen()
main()

