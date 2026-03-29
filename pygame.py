import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

player = pygame.Rect(100, 100, 80, 80)

center_pos = (WIDTH // 2, HEIGHT // 2)
box_size = 100
angle = 0

speed = 5

def get_rotated_corners(center, w, h, angle_deg):
    angle_rad = math.radians(angle_deg)
    hw, hh = w / 2, h / 2

    corners = [(-hw,-hh),(hw,-hh),(hw,hh),(-hw,hh)]
    rotated = []

    for x, y in corners:
        rx = x * math.cos(angle_rad) - y * math.sin(angle_rad)
        ry = x * math.sin(angle_rad) + y * math.cos(angle_rad)
        rotated.append((center[0] + rx, center[1] + ry))

    return rotated

def get_axes(corners):
    axes = []
    for i in range(len(corners)):
        p1 = corners[i]
        p2 = corners[(i+1) % len(corners)]

        edge = (p2[0] - p1[0], p2[1] - p1[1])
        normal = (-edge[1], edge[0])

        length = math.hypot(normal[0], normal[1])
        normal = (normal[0]/length, normal[1]/length)

        axes.append(normal)
    return axes

def project(corners, axis):
    dots = []
    for p in corners:
        dots.append(p[0]*axis[0] + p[1]*axis[1])
    return min(dots), max(dots)

def sat_collision(c1, c2):
    axes = get_axes(c1) + get_axes(c2)

    for axis in axes:
        min1, max1 = project(c1, axis)
        min2, max2 = project(c2, axis)

        if max1 < min2 or max2 < min1:
            return False
    return True

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player.x -= speed
    if keys[pygame.K_RIGHT]:
        player.x += speed
    if keys[pygame.K_UP]:
        player.y -= speed
    if keys[pygame.K_DOWN]:
        player.y += speed

    if keys[pygame.K_z]:
        angle += 5
    else:
        angle += 1

    screen.fill(WHITE)

    # -------------------------
    # Circle Collision
    # -------------------------
    p_center = player.center
    c_center = center_pos

    p_radius = player.width // 2
    c_radius = box_size // 2

    dx = p_center[0] - c_center[0]
    dy = p_center[1] - c_center[1]

    circle_hit = (dx*dx + dy*dy) < (p_radius + c_radius) ** 2

    # -------------------------
    # AABB Collision
    # -------------------------
    aabb_box = pygame.Rect(center_pos[0] - box_size//2,
                           center_pos[1] - box_size//2,
                           box_size, box_size)

    aabb_hit = player.colliderect(aabb_box)

    # -------------------------
    # OBB Collision (SAT)
    # -------------------------
    player_corners = [
        player.topleft,
        player.topright,
        player.bottomright,
        player.bottomleft
    ]

    box_corners = get_rotated_corners(center_pos, box_size, box_size, angle)

    obb_hit = sat_collision(player_corners, box_corners)

    # -------------------------
    # Draw Objects
    # -------------------------
    pygame.draw.rect(screen, GRAY, player)
    pygame.draw.rect(screen, RED, player, 2)

    pygame.draw.rect(screen, RED, aabb_box, 2)

    pygame.draw.circle(screen, BLUE, p_center, p_radius, 2)
    pygame.draw.circle(screen, BLUE, c_center, c_radius, 2)

    pygame.draw.polygon(screen, GRAY, box_corners)
    pygame.draw.polygon(screen, GREEN, box_corners, 2)

    # -------------------------
    # Text Display
    # -------------------------
    circle_text = font.render(f"Circle: {'HIT' if circle_hit else 'NO'}", True, (0,0,0))
    aabb_text = font.render(f"AABB : {'HIT' if aabb_hit else 'NO'}", True, (0,0,0))
    obb_text = font.render(f"OBB  : {'HIT' if obb_hit else 'NO'}", True, (0,0,0))

    screen.blit(circle_text, (10, 10))
    screen.blit(aabb_text, (10, 35))
    screen.blit(obb_text, (10, 60))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
