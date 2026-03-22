#week3 목표
Pygame 첫 실행 및 Ai와 함께 키보드 입력 구현

##AI 대화 기록
질문1:아래 Pygame 코드를 처음 프로그래밍하는 사람에게 설명해줘. 각 줄이 뭘 하는지, 왜 필요한지 알려줘.
import pygame 
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My First Pygame")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

clock = pygame.time.Clock()
running = True

while running:
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         running = False

   screen.fill(WHITE)
   pygame.draw.circle(screen, BLUE, (400, 300), 50)
   pygame.display.flip()
   clock.tick(60)

pygame.quit()
sys.exit()
답1:요약하면 이 프로그램은 800x600 창을 만들고, 가운데 파란 원을 그리고, 60FPS로 계속 화면을 업데이트하다가 창 닫으면 종료되는 프로그램입니다.

질문2:위 코드에서 screen.fill(WHITE) 줄을 삭제하고 실행하면 어떻게 달라져?
답2:screen.fill(WHITE)를 삭제하면
👉 원이 움직이거나 그려질 때 이전 프레임이 지워지지 않아서 화면에 그림이 계속 남습니다.
즉, 화면이 지워지지 않고 계속 덧그려집니다.

질문3:위 코드에 방향키로 5픽셀씩 움직이게 만들어줘
답3:지금 코드에 방향키로 초당 5픽셀씩 이동 기능을 추가하려면
원 좌표를 변수로 만들고 키 입력을 받아서 좌표를 변경하면 됩니다.

##어려웠던 점
AI한테 정확히 어떤 말을 입력해야 내가 원하는 값이 나오는가에서 제대로 이뤄지지 않는 부분이 생각보다 많아서 꽤 어려웠다.

##배운 점
AI가 내가 예상한 것보다 훨씬 코드를 수정 또는 추가하는데 엄청난 도움을 받을 수 있었고 내가 무엇이 틀렸는지 내가 무슨 짓을 했는지 AI한테 아주 자세하게 설명받을 수 있어서 정말 좋았다. 아직 겨우 한 계단을 오른 것 뿐인데 이 다음 단계에서 AI가 더 얼마나 멋진 활약을 해줄지 정말 기대되고 그만큼 AI한테 적극적으로 도움을 받아야겠다고 생각한다.