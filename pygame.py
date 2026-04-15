import pygame
import random
import sys
import base64, io

pygame.init()

# 🔥 base64 이미지 (여기에 네 값 넣기)
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

def draw_hud(score, level_cfg, lives, eat_cooldown, shield_cooldown):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(level_cfg['label'], True, YELLOW), (10, 40))
    lives_text = font.render(f"Lives: {'♥ ' * lives}", True, RED)
    screen.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))
    
    # 먹기 쿨타임 바
    pygame.draw.rect(screen, (80,80,80), (10, 70, 200, 10))
    pygame.draw.rect(screen, (0,255,255), (10, 70, 200 * (1 - eat_cooldown/60), 10))

    # 보호막 쿨타임 바
    pygame.draw.rect(screen, (80,80,80), (10, 90, 200, 10))
    pygame.draw.rect(screen, (100,200,255), (10, 90, 200 * (1 - shield_cooldown/180), 10))
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
    
    # 🔥 스킬 변수
    eat_active = 0
    eat_cooldown = 0

    shield_active = 0
    shield_cooldown = 0
    
    enemies = []
    score = 0
    lives = 4
    spawn_timer = 0
    level_idx = 0
    level_cfg = LEVELS[level_idx]
    invincible = 0

    while True:
        dt = clock.tick(FPS)
        
        if invincible > 0:
            invincible -= 1
        
        eat_active = max(0, eat_active - 1)
        eat_cooldown = max(0, eat_cooldown - 1)
        shield_active = max(0, shield_active - 1)
        shield_cooldown = max(0, shield_cooldown - 1)
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_SPACE] and eat_cooldown <= 0:
            eat_active = 12          # 약 0.2초
            eat_cooldown = 60        # 1초 쿨

        if keys[pygame.K_LSHIFT] and shield_cooldown <= 0:
            shield_active = 90       # 1.5초
            shield_cooldown = 180    # 3초 쿨
        
        moving = False

        if keys[pygame.K_LEFT] and player.left > 0:
             player.x -= 5
             moving = True
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
             player.x += 5
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
        new_enemies = []

        for e in enemies:
            rect = e[0]

            # 먹기
            if eat_active > 0 and player.inflate(40,40).colliderect(rect):
                score += 1
                continue

            # 보호막
            if shield_active > 0 and player.inflate(60,60).colliderect(rect):
                continue

            # 일반 충돌
            if invincible <= 0 and player.colliderect(rect):
                lives -= 1
                invincible = 90
                enemies.clear()   # 🔥 전체 제거 (안전)
                
                # 🔥 여기 추가
                if lives <= 0:
                    if game_over_screen(score):
                        main()
                    return

                continue

            new_enemies.append(e)

        enemies = new_enemies
                    
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

            # 🔥 먹기 이펙트
            if eat_active > 0:
                pygame.draw.circle(screen, (0, 255, 255), player.center, 40, 2)

            # 🔥 보호막 이펙트
            if shield_active > 0:
                pygame.draw.circle(screen, (100, 200, 255), player.center, 60, 3)

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

        draw_hud(score, level_cfg, lives, eat_cooldown, shield_cooldown)
        pygame.display.flip()

main()
