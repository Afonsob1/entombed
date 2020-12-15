import pygame
import time
from PIL import Image


# AINDA NAO SEI SE VOU LER O LABIRINTO POR UMA IMAGEM OU SE CRIO UM FCHEIRO TXT A PARTE
def ler_labirinto(imagem):
    im = Image.open(imagem, 'r')
    width, height = im.size
    pixel_values = list(im.getdata())
    l = []
    for a in range(100):
        s = "11"
        for b in range(2, 10):
            x = b * (width // 20) + width // 20 // 2
            y = int(20.77 * a + 10)
            s += '0' if sum(pixel_values[width * y + x]) / 3 > 240 else '1'
        l.append(s)
    return l


# dimencoes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SQ_SIZE = 40  # lado de cada retangulo
SCREEN_LINHAS = SCREEN_HEIGHT // SQ_SIZE  # NUMERO DE LINHAS QUE CABEM NA JANELA

# cores
RED = (255, 0, 0)
BLUE = (000, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0, 0)
VIOLETA = (155, 155, 255)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption('Entombed')
clock = pygame.time.Clock()

running = True
velocidade_y = 0.2
camara_y = 0

labirinto = ["1100000000"] * 8 + ler_labirinto("niveis/nivel1.png")

while running:
    screen.fill(WHITE)
    
    # ver se o mapa ja acabou
    if len(labirinto) * SQ_SIZE - SCREEN_HEIGHT <= camara_y:
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    dt = clock.tick()     # tempo que passou desde a ultima chamada
    camara_y += dt*velocidade_y # mover camara
    
    # desenhar labirinto
    y = 0  # y da linha
    for linha in labirinto:
        for x, i in enumerate(linha):
            if i == '1':
                pygame.draw.rect(screen, VIOLETA, (x * SQ_SIZE, y - camara_y, SQ_SIZE, SQ_SIZE))
                pygame.draw.rect(screen, VIOLETA, ((2 * len(linha) - x - 1) * SQ_SIZE, y - camara_y, SQ_SIZE, SQ_SIZE))
        y += SQ_SIZE
    pygame.display.update()

pygame.quit()
