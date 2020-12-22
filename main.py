import pygame
from PIL import Image

# dimencoes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SQ_SIZE = 40  # lado de cada retangulo

# dimencoes do player
PLAYER_SIZE = 20
PLAYER_VELOCITY = 0.2

SCREEN_LINHAS = SCREEN_HEIGHT // SQ_SIZE  # NUMERO DE LINHAS QUE CABEM NA JANELA

# lado que o jogador esta virado
NADA = 0
ESQ = 1
DIR = 2
CIMA = 3
BAIXO = 4

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


def coord_player_to_labirinto(x, y, camara_y):
    return int(x // SQ_SIZE), int((y + camara_y) // SQ_SIZE)


def mover_jogador(keys, player_coord, player_size, labirinto, camara_y, dt):
    player_x, player_y = player_coord
    player_w, player_h = player_size

    add_x = 0
    add_y = 0
    virado = NADA

    if keys[pygame.K_LEFT]:
        add_x -= dt * PLAYER_VELOCITY
        virado = ESQ
    if keys[pygame.K_RIGHT]:
        add_x += dt * PLAYER_VELOCITY
        virado = DIR
    if keys[pygame.K_UP]:
        add_y -= dt * PLAYER_VELOCITY
        virado = CIMA
    if keys[pygame.K_DOWN]:
        add_y += dt * PLAYER_VELOCITY
        virado = BAIXO

    y = 0  # y da linha
    for linha in labirinto:
        for x, i in enumerate(linha):
            if i == '1':
                rect_1 = pygame.Rect(x * SQ_SIZE, y - camara_y, SQ_SIZE, SQ_SIZE)
                rect_2 = pygame.Rect((2 * len(linha) - x - 1) * SQ_SIZE, y - camara_y, SQ_SIZE,
                                     SQ_SIZE)  # Posicao simetrica

                # Ve se o player ao andar "add_x" pixeis colide com alguma parede
                # se colidir nao poe "add_x" a 0, logo nao deixa andar nessa direcao
                # Quando fica no chao ele andava mais lento se fizer isto isso já nao acontece
                player_rect = pygame.Rect(player_x + add_x, player_y + 1, player_w, player_h)

                if player_rect.colliderect(rect_1) or player_rect.colliderect(rect_2):
                    player_rect = pygame.Rect(player_x + add_x, player_y - 1, player_w, player_h)

                    if player_rect.colliderect(rect_1) or player_rect.colliderect(rect_2):
                        add_x = 0

                # Ve se o player ao andar "add_y" pixeis colide com alguma parede
                # se colidir poe o "add_y" a 0 nao deixa andar nessa direcao
                player_rect = pygame.Rect(player_x, player_y + add_y, player_w, player_h)
                if player_rect.colliderect(rect_1) or player_rect.colliderect(rect_2):
                    add_y = 0

        y += SQ_SIZE

    player_x += add_x
    player_y += add_y
    return virado, player_x, player_y


# parte a parede (usa o make_break)
def mover_parede(player_coord, player_size, camara_y, virado, labirinto):
    player_w, player_h = player_size

    # calcula as coordenadas do quadrado onde o player está
    x, y = coord_player_to_labirinto(player_coord[0] + player_w // 2, player_coord[1] + player_h // 2, camara_y)

    if virado == ESQ:
        x -= 1
    elif virado == DIR:
        x += 1
    elif virado == CIMA:
        y -= 1
    elif virado == BAIXO:
        y += 1

    if virado != NADA:
        if x >= 10:
            x = 9 - (x - 10)
        if 2 <= x:  # Não deixa mudar os quadrados da borda do ecra
            if labirinto[y][x] == '1':
                labirinto[y] = labirinto[y][:x] + '0' + labirinto[y][x + 1:]
            else:
                labirinto[y] = labirinto[y][:x] + '1' + labirinto[y][x + 1:]


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption('Entombed')
    clock = pygame.time.Clock()

    # jogador
    player = pygame.image.load('assets/jogador.png')
    player.set_colorkey(WHITE)

    player_size = (player.get_width(), player.get_height())

    player_x, player_y = 100, 200
    virado = NADA

    running = True
    velocidade_y = 0.05
    camara_y = 0

    labirinto = ["1100000000"] * 12 + ler_labirinto("niveis/nivel1.png")

    while running:
        screen.fill(BLACK)

        # ver se o mapa ja acabou
        if len(labirinto) * SQ_SIZE - SCREEN_HEIGHT <= camara_y:
            running = False

        # ver se jogador ultrapassou limites do ecra
        if player_y < 0:
            running = False
        elif player_y > SCREEN_HEIGHT - player.get_height():
            player_y = SCREEN_HEIGHT - player.get_height()

        dt = clock.tick()  # tempo que passou desde a ultima chamada
        camara_y += dt * velocidade_y  # mover camara em funcao do tempo
        player_y -= dt * velocidade_y  # mover jogador em funcao do tempo

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    mover_parede((player_x, player_y), player_size, camara_y, virado, labirinto)
        keys = pygame.key.get_pressed()

        virado, player_x, player_y = mover_jogador(keys, (player_x, player_y), player_size, labirinto, camara_y, dt)

        ############## rendering ##############

        # desenhar labirinto
        y = 0  # y da linha
        for linha in labirinto:
            for x, i in enumerate(linha):
                if i == '1':
                    # Desenha o quadrado na posicao x, y
                    pygame.draw.rect(screen, LARANJA, (x * SQ_SIZE, y - camara_y, SQ_SIZE, SQ_SIZE))

                    # Desenha o quadrado na posicao simetrica
                    pygame.draw.rect(screen, LARANJA, ((2*len(linha) - x-1) * SQ_SIZE, y - camara_y, SQ_SIZE, SQ_SIZE))

            y += SQ_SIZE

        # desenhar o jogador
        screen.blit(player, (player_x, player_y))

        pygame.display.update()

    pygame.quit()


main()
