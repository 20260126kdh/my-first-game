import pygame
import random
import sys

pygame.init()

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
BLUE   = (50, 120, 220)
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

PLAYER_W, PLAYER_H = 50, 30
ENEMY_W, ENEMY_H = 30, 30

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
    player = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 60, PLAYER_W, PLAYER_H)

    enemies = []
    score = 0
    lives = 3
    spawn_timer = 0
    level_idx = 0
    level_cfg = LEVELS[level_idx]
    invincible = 0

    while True:
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= 5
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += 5
        if keys[pygame.K_UP] and player.top > 0:
            player.y -= 5
        if keys[pygame.K_DOWN] and player.bottom < HEIGHT:
            player.y += 5

        # 🔥 스폰
        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            if random.random() < 0.2:
                enemies.append(spawn_yellow_enemy())
            else:
                enemies.append(spawn_enemy(level_cfg))

        # 🔥 이동 처리
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

            if rect.top < HEIGHT and rect.bottom > 0:
                survived.append(e)
            else:
                if e[2] == "red":
                    score += 1

        enemies = survived

        # 충돌
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
            pygame.draw.rect(screen, BLUE, player)

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
