import pygame
# dimencoes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# cores
WHITE = (255,255,255)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Entombed')

running = True

while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()
pygame.quit()