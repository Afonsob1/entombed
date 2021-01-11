import pygame
import random
from monstro import Monstro

## CONSTANTES ##

# dimencoes

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SQ_SIZE = 40  # lado de cada retangulo
MB_WIDTH = SQ_SIZE / 3  # lado do make a break
MB_HEIGHT = SQ_SIZE / 2  # altura do make a break

# dimencoes do player
PLAYER_SIZE = 20
PLAYER_VELOCITY = 0.2

MAKE_BREAK_VELOCITY = 0.1

SCREEN_LINHAS = SCREEN_HEIGHT // SQ_SIZE  # NUMERO DE LINHAS QUE CABEM NA JANELA

# Pontuacao, vidas e makebreak
pygame.font.init()
TXT_SIZE = 32
font = pygame.font.SysFont(None, TXT_SIZE)

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

CORES_NIVEL = (0xff8c15, (11, 179, 2), (2, 191, 191), (0, 0, 255), (164, 7, 248), (253, 157, 251), (255, 0, 0), WHITE)


def criar_labirinto():
    # esta tabela foi tirada da wikipedia
    # foi este algoritmo que usaram para criar
    # o jogo original, entombed
    #          abcde    X
    TABELA = {'00000': '1',
              '00001': '1',
              '00010': '1',
              '00011': 'R',
              '00100': '0',
              '00101': '0',
              '00110': 'R',
              '00111': 'R',
              '01000': '1',
              '01001': '1',
              '01010': '1',
              '01011': '1',
              '01100': 'R',
              '01101': '0',
              '01110': '0',
              '01111': '0',
              '10000': '1',
              '10001': '1',
              '10010': '1',
              '10011': 'R',
              '10100': '0',
              '10101': '0',
              '10110': '0',
              '10111': '0',
              '11000': 'R',
              '11001': '0',
              '11010': '1',
              '11011': 'R',
              '11100': 'R',
              '11101': '0',
              '11110': '0',
              '11111': '0'}

    l = ['11' + '0' * 8]
    for y in range(100):
        s = "11"  # cada linha começa sempre com 2 paredes
        for x in range(2, 10):
            # aqui vamos fazer o algoritmo conforme a tabela
            if x == 2:
                a, b, c = '1', '0', random.choice(['0', '1'])
            else:
                a, b, c = s[x - 2], s[x - 1], l[-1][x - 1]

            d = l[-1][x]

            # se o 'e' apontar para o um x > 10 é random
            e = l[-1][x + 1] if x + 1 < 10 else random.choice(['0', '1'])
            X = TABELA[a + b + c + d + e]
            if X == 'R':
                s += random.choice(['0', '1'])
            else:
                s += X
        l.append(s)

    return l


def desenhar_informacoes(screen, makebreak, vidas, score, margem, coracao):
    makebreak_txt = "Make-Break: " + str(makebreak)
    score_txt = "Score: " + str(score)
    text_height = max(font.size(i)[1] for i in (makebreak_txt, score_txt))

    info = font.render(makebreak_txt, True, (255, 255, 255))
    screen.blit(info, (100, (margem - text_height) / 2))

    for i in range(vidas):
        screen.blit(coracao, (SCREEN_WIDTH / 2 - (32 * vidas) // 2 + 32 * i, (margem - coracao.get_size()[0]) / 2))

    score_size = font.size(score_txt)[0]

    info = font.render(score_txt, True, (255, 255, 255))
    screen.blit(info, (SCREEN_WIDTH - score_size - 100, (margem - text_height) / 2))


def figura_make_break(coord):
    return pygame.Rect(coord[0], coord[1] + (SQ_SIZE - MB_HEIGHT) / 2, MB_WIDTH, MB_HEIGHT)


def figura_jogador(coord, size):
    return pygame.Rect(*coord, *size)


def colisao_jogador_parede(player_coord, player_size, parede_coord, quadrados_linha, camara_y):
    rect_1 = pygame.Rect(parede_coord[0] * SQ_SIZE, parede_coord[1] * SQ_SIZE - camara_y, SQ_SIZE, SQ_SIZE)
    rect_2 = pygame.Rect((quadrados_linha - parede_coord[0] - 1) * SQ_SIZE, parede_coord[1] * SQ_SIZE - camara_y,
                         SQ_SIZE, SQ_SIZE)  # Posicao simetrica

    player_rect = figura_jogador(player_coord, player_size)
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

    player_x_lab, player_y_lab = coord_world_to_labirinto(player_x, player_y, camara_y)

    for y, linha in enumerate(labirinto[player_y_lab - 1:player_y_lab + 2], player_y_lab - 1):
        for x, i in enumerate(linha):
            if i == '1':
                # Ve se o player ao andar "add_x" pixeis colide com a parede
                # se colidir nao poe "add_x" a 0, logo nao deixa andar nessa direcao
                if add_x != 0 and colisao_jogador_parede((player_x + add_x, player_y), player_size, (x, y),
                                                         2 * len(linha), camara_y):
                    add_x = 0

                # Ve se o player ao andar "add_y" pixeis colide com alguma parede
                # se colidir poe o "add_y" a 0 nao deixa andar nessa direcao
                if add_y > 0 and colisao_jogador_parede((player_x, player_y + add_y), player_size, (x, y),
                                                        2 * len(linha), camara_y):
                    player_y = coord_labirinto_to_world(0, y, camara_y)[1] - player_size[1] - 5
                elif add_y < 0 and colisao_jogador_parede((player_x, player_y + add_y), player_size, (x, y),
                                                          2 * len(linha), camara_y):
                    player_y = coord_labirinto_to_world(0, y + 1, camara_y)[1] + 5

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
                return True
            else:
                # Só adiciona parede se o jogador nao ficar preso nela
                if not colisao_jogador_parede(player_coord, player_size, (x, y), 2 * len(labirinto[0]), camara_y):
                    labirinto[y] = labirinto[y][:x] + '1' + labirinto[y][x + 1:]
                    return True
    return False


def criar_monstros(numero, labirinto, add_y, gravidade, camara_y):
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
        if monstro_y >= len(labirinto):
            break
        linha = labirinto[monstro_y]
        vazio = linha.count('0') * 2                    # conta o numero de quadriculas vazias na linha
        if vazio == 0:                                  # nao pode por se a linha nao tiver espacos vazios
            continue
        m_x = random.randint(0, vazio - 1)              # escolhe um x aleatorio

        for x, quadrado in enumerate(linha + linha[::-1]):
            if quadrado == '0':
                if not m_x:
                    calmo = not random.randint(0, 1)    # escolhe se o monstro vai ser calmo ou nao
                    print("MONSTROS: ", x, monstro_y, calmo)
                    lista_coordenadas.append(
                        Monstro(*coord_labirinto_to_world(x, monstro_y + add_y, camara_y), calmo, gravidade))
                    break
                m_x -= 1

    return lista_coordenadas


def colisao_monstro(coord, monstro_size, camara_y, labirinto):
    for y, linha in enumerate(labirinto):
        for x, quadrado in enumerate(linha):
            if quadrado == '1' and colisao_jogador_parede(coord, monstro_size, (x, y), 2 * len(linha), camara_y):
                return x, y
    return ()


def criar_make_breaks(make_break, labirinto, add_y, camara_y):
    distancia = (len(labirinto) - 10) // make_break  # tem -10 pois nao quero logo no inicio

    lista_linhas = []
    for i in range(make_break):
        if len(lista_linhas) == 0:
            lista_linhas.append(random.randint(10, 10 + distancia))
        else:
            lista_linhas.append(random.randint(lista_linhas[-1] + distancia, lista_linhas[-1] + distancia + 1))
            if lista_linhas[-1] > len(labirinto):
                del lista_linhas[-1]
                break

    lista_coordenadas = []
    for break_y in lista_linhas:
        if break_y >= len(labirinto):
            continue

        linha = labirinto[break_y]
        vazio = linha.count('0') * 2  # conta o numero de quadriculas vazias na linha
        m_x = random.randint(0, vazio - 1)  # escolhe um x aleatorio

        for x, quadrado in enumerate(linha + linha[::-1]):
            if quadrado == '0':
                if not m_x:
                    print("MAKE-BREAK", x, break_y)
                    lista_coordenadas.append([*coord_labirinto_to_world(x, break_y + add_y, camara_y), DIR])
                    break
                m_x -= 1

    return lista_coordenadas


def colisao_makebreak(rect, camara_y, labirinto):
    for y, linha in enumerate(labirinto):
        for x, quadrado in enumerate(linha):
            if quadrado == '1' and colisao_jogador_parede((rect.x, rect.y), rect.size, (x, y), 2 * len(linha), camara_y):
                return x, y
    return ()


def jogo(cor, coracao, player_info, makebreak_info, velocidade_y, score, vidas, labirinto, screen):
    player, player_x, player_y, player_size = player_info
    number_make_break, n_make_break_labirinto = makebreak_info

    perdeu = False
    acabou = False
    sair = False
    margem = 32
    camara_y = 32
    clock = pygame.time.Clock()

    monstros = criar_monstros(5, labirinto, 12, velocidade_y, camara_y)

    make_breaks = criar_make_breaks(n_make_break_labirinto, labirinto, 12, camara_y)

    labirinto = ["1100000000"] * 12 + labirinto

    while not (perdeu or acabou or sair):
        screen.fill(BLACK)

        # ver se o mapa ja acabou
        if len(labirinto) * SQ_SIZE - SCREEN_HEIGHT <= camara_y:
            acabou = True

        # ver se jogador ultrapassou limites do ecra
        if player_y < margem:
            perdeu = True
        elif player_y > SCREEN_HEIGHT - player_size[0]:
            player_y = SCREEN_HEIGHT - player_size[1]

        dt = clock.tick()  # tempo que passou desde a ultima chamada
        camara_y += dt * velocidade_y  # mover camara em funcao do tempo
        player_y -= dt * velocidade_y  # mover jogador em funcao do tempo

        keys = pygame.key.get_pressed()

        virado, player_x, player_y = mover_jogador(keys, (player_x, player_y), player_size, labirinto, camara_y, dt)

        for m in monstros:
            if m.y - player_y < SCREEN_LINHAS * SQ_SIZE:
                m.acordado = True  # acorda o monstro e ele começa-se a mexer
            m.mover(dt, lambda coord, size: colisao_monstro(coord, size, camara_y, labirinto),
                    lambda coord: coord_world_to_labirinto(*coord, camara_y, convert_int=False),
                    lambda coord: coord_labirinto_to_world(*coord, camara_y))

            # Vê se o jogador colide com o monstro
            if m.colide(figura_jogador((player_x, player_y), player_size)):
                perdeu = True

        for n, mb in enumerate(make_breaks):
            x, y, direcao = mb
            y -= dt * velocidade_y  # mover em funcao do tempo, para acompanhar o labirinto

            if 0 < y < SCREEN_LINHAS * SQ_SIZE:
                # mover make a break
                if direcao == DIR:
                    if colisao_makebreak(figura_make_break((x + dt * MAKE_BREAK_VELOCITY, y)), camara_y, labirinto):
                        direcao = ESQ
                    else:
                        x += dt * MAKE_BREAK_VELOCITY
                elif direcao == ESQ:
                    if colisao_makebreak(figura_make_break((x - dt * MAKE_BREAK_VELOCITY, y)), camara_y, labirinto):
                        direcao = DIR
                    else:
                        x -= dt * MAKE_BREAK_VELOCITY

            # ver se jogador o apanha
            if figura_jogador((player_x, player_y), player_size).colliderect(figura_make_break((x, y))):
                number_make_break += 3
                print("mb: ", number_make_break)
                del make_breaks[n]
            else:
                # guarda as alteracoes feitas, a posicao e a direcao
                make_breaks[n] = x, y, direcao

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sair = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # usar make a break
                    if number_make_break and mover_parede((player_x, player_y), player_size, camara_y, virado,
                                                          labirinto):
                        number_make_break -= 1
                        print("mb: ", number_make_break)

        # aumenar score
        score += dt * velocidade_y / SQ_SIZE / (SCREEN_HEIGHT / SQ_SIZE)

        ############## rendering ##############

        # desenhar labirinto
        for y, linha in enumerate(labirinto):
            for x, i in enumerate(linha):
                if i == '1':
                    # Desenha o quadrado na posicao x, y
                    pygame.draw.rect(screen, cor, [*coord_labirinto_to_world(x, y, camara_y), SQ_SIZE, SQ_SIZE])

                    # Desenha o quadrado na posicao simetrica
                    pygame.draw.rect(screen, cor, [*coord_labirinto_to_world(2 * len(linha)-x-1, y, camara_y),
                                                   SQ_SIZE, SQ_SIZE])

        # desenhar monstros
        for m in monstros:
            m.desenhar(screen)

        # desenhar make-break
        for mx, my, _ in make_breaks:
            pygame.draw.rect(screen, WHITE, figura_make_break((mx, my)))

        # desenhar o jogador
        screen.blit(player, (player_x, player_y))

        # desenhar informacoes
        pygame.draw.rect(screen, BLACK, [0, 0, SCREEN_WIDTH, margem])
        desenhar_informacoes(screen, number_make_break, vidas, int(score), margem, coracao)
        pygame.display.update()

    return perdeu, sair, number_make_break, score


def comecar_jogo(screen, n_make_break_labirinto, score):
    global PLAYER_VELOCITY
    PLAYER_VELOCITY = 0.2

    # coracao
    coracao = pygame.image.load('assets/coracao.png')
    coracao.set_colorkey(BLACK)

    # jogador
    player = pygame.image.load('assets/jogador.png')
    player.set_colorkey(WHITE)

    player_size = (player.get_width(), player.get_height())
    player_x, player_y = 100, 200

    player_info = (player, player_x, player_y, player_size)

    labirinto = criar_labirinto()
    velocidade_y = 0.1
    vidas = 3
    make_brakes = 3
    nivel = 1

    while vidas:
        perdeu, sair, make_brakes, score = jogo(CORES_NIVEL[nivel - 1], coracao, player_info,
                                                (make_brakes, n_make_break_labirinto), velocidade_y, score, vidas,
                                                labirinto.copy(), screen)
        if sair:
            break
        if perdeu:
            vidas -= 1
        else:
            # passa de nivel
            velocidade_y += 0.03
            PLAYER_VELOCITY += PLAYER_VELOCITY * 0.10
            labirinto = criar_labirinto()  # muda de labirinto
            nivel += 1

    if vidas == 0:
        print("PERDEU")


def inicio():
    pygame.init()
    pygame.display.set_caption('Entombed')
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    background = pygame.image.load("assets/background.png")
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    insert_coin = [pygame.image.load("assets/insert coin/insert_coin_1.png"),
                   pygame.image.load("assets/insert coin/insert_coin_2.png"),
                   pygame.image.load("assets/insert coin/insert_coin_3.png"),
                   pygame.image.load("assets/insert coin/insert_coin_4.png"),
                   pygame.image.load("assets/insert coin/insert_coin_5.png"),
                   pygame.image.load("assets/insert coin/insert_coin_6.png"),
                   pygame.image.load("assets/insert coin/insert_coin_7.png")]
    insert_coin_selected = pygame.transform.scale(pygame.image.load("assets/insert coin/insert_coin_8.png"), (200, 100))

    for i, img in enumerate(insert_coin):
        insert_coin[i] = pygame.transform.scale(img, (200, 100))
    insert_coin_size = insert_coin[0].get_size()
    insert_coin_pos = SCREEN_WIDTH / 2 - insert_coin_size[0] / 2, SCREEN_HEIGHT * (2 / 3) - insert_coin_size[1] / 2
    insert_coin_n = 0
    insert_coin_rect = pygame.Rect(*insert_coin_pos, *insert_coin_size)
    clicou_comecar = False
    sair = False

    titulo = pygame.transform.scale(pygame.image.load("assets/entombed.png"), (500, 100))
    titulo.set_colorkey(WHITE)

    clock = pygame.time.Clock()

    while not sair:
        rato_no_insert_coin = insert_coin_rect.collidepoint(*pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sair = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rato_no_insert_coin:
                    clicou_comecar = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if rato_no_insert_coin:
                    if clicou_comecar:
                        # COMECAR JOGO
                        comecar_jogo(screen, 4, 1)
                    clicou_comecar = False

        dt = clock.tick(10)
        insert_coin_n += dt/1000 * 4            # mudar de cor 4 vezes por segundo
        if insert_coin_n >= len(insert_coin):
            insert_coin_n = 0

        screen.blit(background, (0, 0))
        if rato_no_insert_coin:
            screen.blit(insert_coin_selected, insert_coin_pos)
        else:
            screen.blit(insert_coin[int(insert_coin_n)], insert_coin_pos)

        screen.blit(titulo, (SCREEN_WIDTH/2 - titulo.get_size()[0]/2, SCREEN_HEIGHT*(1/6) - titulo.get_size()[1]/2))
        pygame.display.update()

    pygame.quit()


inicio()
