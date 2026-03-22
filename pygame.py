import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My First Pygame")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

clock = pygame.time.Clock()
running = True

# 원 위치
x = 400
y = 300
speed = 5   # 초당 이동 속도 느낌 (프레임당 5픽셀)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 키 입력 받기
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        x -= speed
    if keys[pygame.K_RIGHT]:
        x += speed
    if keys[pygame.K_UP]:
        y -= speed
    if keys[pygame.K_DOWN]:
        y += speed

    screen.fill(WHITE)
    pygame.draw.circle(screen, BLUE, (x, y), 50)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
