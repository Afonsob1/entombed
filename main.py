import pygame
import random
from PIL import Image
from monstro import Monstro

## CONSTANTES ##

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


def colisao_jogador_parede(player_coord, player_size, parede_coord, quadrados_linha, camara_y):
    rect_1 = pygame.Rect(parede_coord[0] * SQ_SIZE, parede_coord[1] * SQ_SIZE - camara_y, SQ_SIZE, SQ_SIZE)
    rect_2 = pygame.Rect((quadrados_linha - parede_coord[0] - 1) * SQ_SIZE, parede_coord[1] * SQ_SIZE - camara_y,
                         SQ_SIZE, SQ_SIZE)  # Posicao simetrica

    player_rect = pygame.Rect(player_coord[0], player_coord[1], player_size[0], player_size[1])
    return player_rect.colliderect(rect_1) or player_rect.colliderect(rect_2)


def coord_world_to_labirinto(x, y, camara_y, convert_int=True):
    if convert_int:
        return int(x // SQ_SIZE), int((y + camara_y) // SQ_SIZE)

    return x / SQ_SIZE, (y + camara_y) / SQ_SIZE


def coord_labirinto_to_world(x, y, camara_y):
    return x * SQ_SIZE, y * SQ_SIZE - camara_y


def mover_jogador(keys, player_coord, player_size, labirinto, camara_y, dt):
    player_x, player_y = player_coord

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

    for y, linha in enumerate(labirinto):
        for x, i in enumerate(linha):
            if i == '1':
                # Ve se o player ao andar "add_x" pixeis colide com a parede
                # se colidir nao poe "add_x" a 0, logo nao deixa andar nessa direcao
                # Quando fica no chao ele andava mais lento se fizer isto isso já nao acontece
                if colisao_jogador_parede((player_x + add_x, player_y + 1), player_size, (x, y), 2 * len(linha),
                                          camara_y):

                    if colisao_jogador_parede((player_x + add_x, player_y - 1), player_size, (x, y), 2 * len(linha),
                                              camara_y):
                        add_x = 0

                # Ve se o player ao andar "add_y" pixeis colide com alguma parede
                # se colidir poe o "add_y" a 0 nao deixa andar nessa direcao
                if colisao_jogador_parede((player_x, player_y + add_y), player_size, (x, y), 2 * len(linha), camara_y):
                    add_y = 0

    player_x += add_x
    player_y += add_y
    return virado, player_x, player_y


# parte a parede (usa o make_break)
def mover_parede(player_coord, player_size, camara_y, virado, labirinto):
    player_w, player_h = player_size

    # calcula as coordenadas do quadrado onde o player está
    x, y = coord_world_to_labirinto(player_coord[0] + player_w // 2, player_coord[1] + player_h // 2, camara_y)

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
                # Só adiciona parede se o jogador nao ficar preso nela
                if not colisao_jogador_parede(player_coord, player_size, (x, y), 2 * len(labirinto[0]), camara_y):
                    labirinto[y] = labirinto[y][:x] + '1' + labirinto[y][x + 1:]


def criar_monstros(numero, labirinto, add_y, gravidade):
    # numero de linhas de destancia
    distancia = (len(labirinto) - 4) // numero  # tem -4 pois nao quero monstros logo no inicio

    # cria monstros ,apartir da 4 linha, e a uma distancia minima
    lista_linhas = []
    for i in range(numero):
        if len(lista_linhas) == 0:
            lista_linhas.append(4 + random.randint(0, 3))
        else:
            lista_linhas.append(random.randint(lista_linhas[-1] + distancia, lista_linhas[-1] + distancia + 2))
            if lista_linhas[-1] > len(labirinto):
                del lista_linhas[-1]
                break

    lista_coordenadas = []
    for monstro_y in lista_linhas:
        linha = labirinto[monstro_y]
        vazio = linha.count('0') * 2  # conta o numero de quadriculas vazias na linha
        m_x = random.randint(0, vazio - 1)  # escolhe um x aleatorio

        for x, quadrado in enumerate(linha + linha[::-1]):
            if quadrado == '0':
                if not m_x:
                    calmo = not random.randint(0, 1)  # escolhe se o monstro vai ser calmo ou nao
                    print(x, monstro_y, calmo)
                    lista_coordenadas.append(Monstro(*coord_labirinto_to_world(x, monstro_y + add_y, 0), calmo, gravidade))
                    break
                m_x -= 1

    return lista_coordenadas


def colisao_monstro(coord, monstro_size, camara_y, labirinto):
    for y, linha in enumerate(labirinto):
        for x, quadrado in enumerate(linha):
            if quadrado == '1' and colisao_jogador_parede(coord, monstro_size, (x, y), 2 * len(linha), camara_y):
                return x, y
    return ()


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

    running = True
    velocidade_y = 0.07
    camara_y = 0

    labirinto = ler_labirinto("niveis/nivel1.png")

    monstros = criar_monstros(5, labirinto, 12, velocidade_y)
    labirinto = ["1100000000"] * 12 + labirinto

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
        for m in monstros:
            if m.y - player_y < SCREEN_LINHAS * SQ_SIZE:
                m.acordado = True  # acorda o monstro e ele começa-se a mexer
            m.mover(dt, lambda coord, size: colisao_monstro(coord, size, camara_y, labirinto),
                        lambda coord: coord_world_to_labirinto(*coord, camara_y, convert_int=False),
                        lambda coord: coord_labirinto_to_world(*coord, camara_y))

        keys = pygame.key.get_pressed()

        virado, player_x, player_y = mover_jogador(keys, (player_x, player_y), player_size, labirinto, camara_y, dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    mover_parede((player_x, player_y), player_size, camara_y, virado, labirinto)

                    ############## rendering ##############

        # desenhar labirinto
        for y, linha in enumerate(labirinto):
            for x, i in enumerate(linha):
                if i == '1':
                    # Desenha o quadrado na posicao x, y
                    pygame.draw.rect(screen, LARANJA, [*coord_labirinto_to_world(x, y, camara_y), SQ_SIZE, SQ_SIZE])

                    # Desenha o quadrado na posicao simetrica
                    pygame.draw.rect(screen, LARANJA,
                                     [*coord_labirinto_to_world(2 * len(linha) - x - 1, y, camara_y), SQ_SIZE, SQ_SIZE])

        # desenhar monstros
        for m in monstros:
            m.desenhar(screen)

        # desenhar o jogador
        screen.blit(player, (player_x, player_y))
        pygame.display.update()

    pygame.quit()


main()
