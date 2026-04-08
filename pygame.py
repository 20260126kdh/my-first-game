import pygame
import random
import sys
import base64, io

pygame.init()

# 🔥 base64 이미지 (여기에 네 값 넣기)
SHEET_B64 = "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"

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

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodger")
clock = pygame.time.Clock()

font = get_korean_font(36)
font_big = get_korean_font(72)

LEVELS = [
    {"min_speed": 3, "max_speed": 5, "spawn": 40, "label": "Lv.1"},
    {"min_speed": 5, "max_speed": 8, "spawn": 25, "label": "Lv.2"},
    {"min_speed": 7, "max_speed": 12, "spawn": 15, "label": "Lv.3"},
]

PLAYER_W, PLAYER_H = 50, 50
ENEMY_W, ENEMY_H = 30, 30

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔥 스프라이트 로드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FRAME_W, FRAME_H = 32, 32
COLS = 4
FRAME_DELAY = 120

sheet_bytes = base64.b64decode(SHEET_B64)
player_sheet = pygame.image.load(io.BytesIO(sheet_bytes)).convert_alpha()

player_frames = []
for i in range(16):
    row, col = divmod(i, COLS)
    rect = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
    player_frames.append(player_sheet.subsurface(rect))

walk_frames = player_frames

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

def draw_hud(score, level_cfg, lives):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(level_cfg['label'], True, YELLOW), (10, 40))
    screen.blit(font.render(f"Lives: {'♥ ' * lives}", True, RED), (WIDTH - 180, 10))

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

def main():
    player = pygame.Rect(WIDTH // 2, HEIGHT - 80, PLAYER_W, PLAYER_H)

    frame_index = 0
    frame_timer = 0

    enemies = []
    score = 0
    lives = 3
    spawn_timer = 0
    level_idx = 0
    level_cfg = LEVELS[level_idx]
    invincible = 0

    while True:
        dt = clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        moving = False

        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= 5
            moving = True
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += 5
            moving = True
        if keys[pygame.K_UP] and player.top > 0:
            player.y -= 5
            moving = True
        if keys[pygame.K_DOWN] and player.bottom < HEIGHT:
            player.y += 5
            moving = True

        # 🔥 애니메이션 업데이트
        if moving:
            frame_timer += dt
            if frame_timer >= FRAME_DELAY:
                frame_index = (frame_index + 1) % len(walk_frames)
                frame_timer = 0
        else:
            frame_index = 0

        # 🔥 적 스폰
        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            if random.random() < 0.2:
                enemies.append(spawn_yellow_enemy())
            else:
                enemies.append(spawn_enemy(level_cfg))

        # 🔥 적 이동
        survived = []
        for e in enemies:
            rect = e[0]

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
                        dist = max(1, (dx**2 + dy**2) ** 0.5)
                        e[4] = [dx / dist, dy / dist]
                        e[3] = "dash"

                elif e[3] == "dash":
                    rect.x += int(e[4][0] * 10)
                    rect.y += int(e[4][1] * 10)

            if rect.top < HEIGHT:
                survived.append(e)
            else:
                if e[2] == "red":
                    score += 1

        enemies = survived

        # 🔥 충돌
        if invincible > 0:
            invincible -= 1
        else:
            for e in enemies:
                if player.colliderect(e[0]):
                    lives -= 1
                    invincible = 90
                    enemies.clear()

                    if lives <= 0:
                        if game_over_screen(score):
                            main()
                        return
                    break

        level_idx = min(score // 20, len(LEVELS) - 1)
        level_cfg = LEVELS[level_idx]

        # 🎨 그리기
        screen.fill(GRAY)

        blink = (invincible // 10) % 2 == 0
        if blink:
            frame_img = pygame.transform.scale(
                walk_frames[frame_index],
                (player.width, player.height)
            )
            screen.blit(frame_img, player.topleft)

        for e in enemies:
            if e[2] == "red":
                pygame.draw.rect(screen, RED, e[0])

            elif e[2] == "yellow":
                rect = e[0]

                if e[3] == "warn":
                    if (e[5] // 5) % 2 == 0:
                        pygame.draw.rect(screen, YELLOW, rect)

                    draw_dashed_line(
                        screen,
                        YELLOW,
                        rect.center,
                        player.center,
                        dash_length=8
                    )
                else:
                    pygame.draw.rect(screen, YELLOW, rect)

        draw_hud(score, level_cfg, lives)
        pygame.display.flip()

main()
