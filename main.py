import pygame
import time
from PIL import Image

# dimencoes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SQ_SIZE = 40  # lado de cada retangulo

# dimencoes do player
PLAYER_SIZE = 20
PLAYER_VELOCITY = 0.2

SCREEN_LINHAS = SCREEN_HEIGHT // SQ_SIZE  # NUMERO DE LINHAS QUE CABEM NA JANELA

# cores
VERMELHO = (255, 0, 0)
AZUL = (000, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0, 0)
VIOLETA = (155, 155, 255)
LARANJA = 0xff8c15


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


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption('Entombed')
    clock = pygame.time.Clock()

    # jogador
    player = pygame.image.load('assets/jogador.png')
    player.set_colorkey(WHITE)

    player_h = player.get_height()
    player_w = player.get_width()

    player_x, player_y = 100, 200

    running = True
    velocidade_y = 0.05
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

        # ver se jogador ultrapassou limites do ecra
        if player_y < 0:
            running = False
        elif player_y > SCREEN_HEIGHT - player.get_height():
            player_y = SCREEN_HEIGHT - player.get_height()

        add_x = 0
        add_y = 0

        dt = clock.tick()  # tempo que passou desde a ultima chamada
        camara_y += dt * velocidade_y  # mover camara
        player_y -= dt * velocidade_y  # mover jogador

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            add_x -= dt * PLAYER_VELOCITY
        if keys[pygame.K_RIGHT]:
            add_x += dt * PLAYER_VELOCITY
        if keys[pygame.K_UP]:
            add_y -= dt * PLAYER_VELOCITY
        if keys[pygame.K_DOWN]:
            add_y += dt * PLAYER_VELOCITY

        y = 0  # y da linha
        for linha in labirinto:
            for x, i in enumerate(linha):
                if i == '1':
                    rect = pygame.Rect(x * SQ_SIZE, y - camara_y, SQ_SIZE, SQ_SIZE)

                    # Quando fica no chao ele andava mais lento se fizer isto isso já nao acontece
                    player_rect = pygame.Rect(player_x + add_x, player_y+1, player_w, player_h)
                    if player_rect.colliderect(rect):
                        player_rect = pygame.Rect(player_x + add_x, player_y-1, player_w, player_h)
                        if player_rect.colliderect(rect):
                            add_x = 0

                    player_rect = pygame.Rect(player_x, player_y + add_y, player_w, player_h)
                    if player_rect.colliderect(rect):
                        add_y = 0

            y += SQ_SIZE

        player_x += add_x
        player_y += add_y

        ############## rendering ##############

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


main()
