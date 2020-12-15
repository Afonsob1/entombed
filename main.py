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
PLAYER_SIZE = 20

SCREEN_LINHAS = SCREEN_HEIGHT // SQ_SIZE  # NUMERO DE LINHAS QUE CABEM NA JANELA

# cores
VERMELHO = (255, 0, 0)
AZUL = (000, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0, 0)
VIOLETA = (155, 155, 255)
LARANJA = 0xff8c15 

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption('Entombed')
clock = pygame.time.Clock()

# jogador
player = pygame.image.load('assets/jogador.png')
player.set_colorkey(WHITE)

player_x , player_y = 100, 10


running = True
velocidade_y = 0.1
camara_y = 0

labirinto = ["1100000000"] * 12 + ler_labirinto("niveis/nivel1.png")

while running:
    screen.fill(BLACK)
    
    # ver se o mapa ja acabou
    if len(labirinto) * SQ_SIZE - SCREEN_HEIGHT <= camara_y:
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    keys=pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= 0.5
    if keys[pygame.K_RIGHT]:
        player_x += 0.5
    if keys[pygame.K_UP]:
        player_y -= 0.5
    if keys[pygame.K_DOWN]:
        player_y += 0.5
            
    
            
    dt = clock.tick()     # tempo que passou desde a ultima chamada
    camara_y += dt*velocidade_y # mover camara
    
    ############### rendering ##############   
    
    # desenhar labirinto    
    y = 0  # y da linha
    for linha in labirinto:
        for x, i in enumerate(linha):
            if i == '1':
                pygame.draw.rect(screen, LARANJA, (x * SQ_SIZE, y - camara_y, SQ_SIZE, SQ_SIZE))
                pygame.draw.rect(screen, LARANJA, ((2 * len(linha) - x - 1) * SQ_SIZE, y - camara_y, SQ_SIZE, SQ_SIZE))
        y += SQ_SIZE
        
        
    # desenhar o jogador
    screen.blit(player, (player_x, player_y))
    
    pygame.display.update()

pygame.quit()
