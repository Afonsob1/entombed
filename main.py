import pygame
import random
from monstro import Monstro
from player import Player

# CONSTANTES

from constantes import *

HIGHSCORE = 0

# dimencoes

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SQ_SIZE = 40  # lado de cada retangulo
MB_WIDTH = SQ_SIZE / 3  # lado do make a break
MB_HEIGHT = SQ_SIZE / 2  # altura do make a break

MAKE_BREAK_VELOCITY = 0.1

SCREEN_LINHAS = SCREEN_HEIGHT // SQ_SIZE  # NUMERO DE LINHAS QUE CABEM NA JANELA

# Fontes
pygame.font.init()

CORES_NIVEL = (0xff8c15, (11, 179, 2), (2, 191, 191), (0, 0, 255), (164, 7, 248), (253, 157, 251), (255, 0, 0), WHITE)

# GLOBAL
# SOM
som = True

sound_on = pygame.image.load('assets/sound_on.png')
sound_on = pygame.transform.scale(sound_on, (30, 30))

sound_off = pygame.image.load('assets/sound_off.png')
sound_off = pygame.transform.scale(sound_off, (30, 30))

sound_pos = SCREEN_WIDTH - sound_on.get_width() - 2, 2

sound_rect = pygame.Rect(*sound_pos, *sound_on.get_size())

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


def tocar(musica, n=0):
    if som:
        musica.play(n)


def criar_labirinto():
    lab = ['11' + '0' * 8]
    for y in range(100):
        s = "11"            # cada linha começa sempre com 2 paredes
        for x in range(2, 10):
            if x == 2:
                a, b, c = '1', '0', random.choice(['0', '1'])
            else:
                a, b, c = s[x - 2], s[x - 1], lab[-1][x - 1]

            d = lab[-1][x]

            # se o 'e' apontar para o um x > 10 é random
            e = lab[-1][x + 1] if x + 1 < 10 else random.choice(['0', '1'])
            X = TABELA[a + b + c + d + e]
            if X == 'R':
                s += random.choice(['0', '1'])
            else:
                s += X
        lab.append(s)

    return lab


def desenhar_informacoes(screen, makebreak, vidas, score, margem, coracao):
    font = pygame.font.SysFont(None, 32)

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


def coord_world_to_labirinto(x, y, camara_y, convert_int=True):
    if convert_int:
        return int(x // SQ_SIZE), int((y + camara_y) // SQ_SIZE)

    return x / SQ_SIZE, (y + camara_y) / SQ_SIZE


def coord_labirinto_to_world(x, y, camara_y):
    return x * SQ_SIZE, y * SQ_SIZE - camara_y


def colisao_parede(retangulo, parede_coord, quadrados_linha, camara_y):
    rect_1 = pygame.Rect(parede_coord[0] * SQ_SIZE, parede_coord[1] * SQ_SIZE - camara_y, SQ_SIZE, SQ_SIZE)
    rect_2 = pygame.Rect((quadrados_linha - parede_coord[0] - 1) * SQ_SIZE, parede_coord[1] * SQ_SIZE - camara_y,
                         SQ_SIZE, SQ_SIZE)  # Posicao simetrica

    return retangulo.colliderect(rect_1) or retangulo.colliderect(rect_2)


# parte a parede (usa o make_break)
def mover_parede(jogador, camara_y, labirinto):
    # calcula as coordenadas do quadrado onde o player está
    x, y = coord_world_to_labirinto(jogador.x + jogador.width // 2, jogador.y + jogador.height // 2, camara_y)

    if jogador.virado == ESQ:
        x -= 1
    elif jogador.virado == DIR:
        x += 1
    elif jogador.virado == CIMA:
        y -= 1
    elif jogador.virado == BAIXO:
        y += 1

    if jogador.virado != NADA:
        if x >= 10:
            x = 9 - (x - 10)
        if 2 <= x:  # Não deixa mudar os quadrados da borda do ecra
            if labirinto[y][x] == '1':
                labirinto[y] = labirinto[y][:x] + '0' + labirinto[y][x + 1:]
                return True
            else:
                # Só adiciona parede se o jogador nao ficar preso nela
                if not colisao_parede(jogador.retangulo(), (x, y), 2 * len(labirinto[0]), camara_y):
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
                    lista_coordenadas.append(Monstro(*coord_labirinto_to_world(x, monstro_y + add_y, camara_y), calmo,
                                                     gravidade, SQ_SIZE))
                    break
                m_x -= 1

    return lista_coordenadas


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
                    lista_coordenadas.append([*coord_labirinto_to_world(x, break_y + add_y, camara_y), DIR])
                    break
                m_x -= 1

    return lista_coordenadas


def jogo(cor, coracao, jogador, makebreak_info, velocidade_y, score, vidas, labirinto, screen):
    number_make_break, n_make_break_labirinto = makebreak_info

    # sons
    global som
    apanhou = pygame.mixer.Sound('assets/sounds/apanhou.wav')
    perigo = pygame.mixer.Sound('assets/sounds/perigoso.mp3')
    clicou_sound = False

    perdeu = False
    acabou = False
    sair = False
    margem = 32
    camara_y = margem
    clock = pygame.time.Clock()

    monstros = criar_monstros(5, labirinto, 12, velocidade_y, camara_y)

    make_breaks = criar_make_breaks(n_make_break_labirinto, labirinto, 12, camara_y)

    labirinto = ["1100000000"] * 12 + labirinto

    def colisao_labirinto(rect):
        for y, linha in enumerate(labirinto):
            for x, quadrado in enumerate(linha):
                if quadrado == '1' and colisao_parede(rect, (x, y), 2 * len(linha), camara_y):
                    return x, y
        return ()

    while not (perdeu or acabou or sair):
        screen.fill(BLACK)

        # ver se o mapa ja acabou
        if len(labirinto) * SQ_SIZE - SCREEN_HEIGHT <= camara_y:
            acabou = True

        # ver se jogador ultrapassou limites do ecra
        if jogador.y < margem:
            perdeu = True
        elif jogador.y > SCREEN_HEIGHT - jogador.height:
            jogador.y = SCREEN_HEIGHT - jogador.height

        dt = clock.tick()               # tempo que passou desde a ultima chamada
        camara_y += dt * velocidade_y   # mover camara em funcao do tempo
        jogador.y -= dt * velocidade_y  # mover jogador em funcao do tempo

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            jogador.mover(ESQ, dt, colisao_labirinto)
        if keys[pygame.K_RIGHT]:
            jogador.mover(DIR, dt, colisao_labirinto)
        if keys[pygame.K_UP]:
            jogador.mover(CIMA, dt, colisao_labirinto)
        if keys[pygame.K_DOWN]:
            jogador.mover(BAIXO, dt, colisao_labirinto)

        for m in monstros:
            if 0 <= m.y < SCREEN_LINHAS * SQ_SIZE:
                m.acordado = True  # acorda o monstro e ele começa-se a mexer
                tocar(perigo, -1)
            elif m.acordado:
                m.acordado = False
                perigo.stop()
            m.mover(dt, colisao_labirinto,
                    lambda coord: coord_world_to_labirinto(*coord, camara_y, convert_int=False),
                    lambda coord: coord_labirinto_to_world(*coord, camara_y))

            # Vê se o jogador colide com o monstro
            if m.colide(jogador.retangulo()):
                perdeu = True

        for i, mb in enumerate(make_breaks):
            m_x, m_y, direcao = mb
            m_y -= dt * velocidade_y            # mover em funcao do tempo, para acompanhar o labirinto

            if 0 < m_y < SCREEN_LINHAS * SQ_SIZE:
                # mover make a break
                if direcao == DIR:
                    if colisao_labirinto(figura_make_break((m_x + dt * MAKE_BREAK_VELOCITY, m_y))):
                        direcao = ESQ
                    else:
                        m_x += dt * MAKE_BREAK_VELOCITY
                elif direcao == ESQ:
                    if colisao_labirinto(figura_make_break((m_x - dt * MAKE_BREAK_VELOCITY, m_y))):
                        direcao = DIR
                    else:
                        m_x -= dt * MAKE_BREAK_VELOCITY

            # ver se jogador o apanha
            if jogador.retangulo().colliderect(figura_make_break((m_x, m_y))):
                number_make_break += 3
                tocar(apanhou)
                del make_breaks[i]
            else:
                # guarda as alteracoes feitas, a posicao e a direcao
                make_breaks[i] = m_x, m_y, direcao

        rato_no_sound = sound_rect.collidepoint(*pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sair = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # usar make a break
                    if number_make_break and mover_parede(jogador, camara_y, labirinto):
                        number_make_break -= 1
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rato_no_sound:
                    clicou_sound = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if rato_no_sound:
                    if clicou_sound:
                        som = not som
                        if som:
                            tocar(musica_fundo)
                        else:
                            musica_fundo.stop()
                            perigo.stop()
                    clicou_sound = False

        # aumenar score
        score += dt * velocidade_y / SQ_SIZE / (SCREEN_HEIGHT / SQ_SIZE)

        ############## rendering ##############

        # desenhar monstros
        for m in monstros:
            m.desenhar(screen)

        # desenhar labirinto
        for y, linha in enumerate(labirinto):
            for x, i in enumerate(linha):
                if i == '1':
                    # Desenha o quadrado na posicao x, y
                    pygame.draw.rect(screen, cor, [*coord_labirinto_to_world(x, y, camara_y), SQ_SIZE, SQ_SIZE])

                    # Desenha o quadrado na posicao simetrica
                    pygame.draw.rect(screen, cor, [*coord_labirinto_to_world(2 * len(linha) - x - 1, y, camara_y),
                                                   SQ_SIZE, SQ_SIZE])

        # desenhar make-break
        for mx, my, _ in make_breaks:
            pygame.draw.rect(screen, WHITE, figura_make_break((mx, my)))

        # desenhar o jogador
        jogador.desenhar(screen, dt)

        # desenhar informacoes
        pygame.draw.rect(screen, BLACK, [0, 0, SCREEN_WIDTH, margem])
        desenhar_informacoes(screen, number_make_break, vidas, int(score), margem, coracao)

        screen.blit(sound_on if som else sound_off, sound_pos)

        pygame.display.update()

    perigo.stop()
    return perdeu, sair, number_make_break, score


def gameover(screen, score):
    gameover_img = pygame.transform.scale(pygame.image.load("assets/gameover.png"), (500, 130))
    gameover_pos = SCREEN_WIDTH/2-gameover_img.get_width()/2, SCREEN_HEIGHT/2 - gameover_img.get_height()

    fonte = pygame.font.SysFont(None, 50)
    size_go = fonte.render("Score: " + str(score), True, (255, 255, 255)).get_size()
    pos_go = SCREEN_WIDTH/2-size_go[0]/2, gameover_pos[1] + gameover_img.get_height() + 100

    i = 0

    highscore_txt = fonte.render("HighScore: "+str(HIGHSCORE), True, (255, 255, 255))
    highscore_pos = SCREEN_WIDTH/2-highscore_txt.get_width()/2, pos_go[1] + size_go[1] + 20

    clock = pygame.time.Clock()
    sair = False
    while i <= score and not sair:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sair = True

        screen.fill(BLACK)
        screen.blit(gameover_img, gameover_pos)

        score_txt = fonte.render("Score: "+str(i), True, (255, 255, 255))
        screen.blit(score_txt, pos_go)
        screen.blit(highscore_txt, highscore_pos)
        pygame.display.update()
        i += 1
        clock.tick(10)

    i = 3
    while i > 0 and not sair:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sair = True
        i -= clock.tick(10)/1000


def comecar_jogo(screen, n_make_break_labirinto):
    global HIGHSCORE

    # coracao
    coracao = pygame.image.load('assets/coracao.png')
    coracao.set_colorkey(BLACK)

    # jogador
    jogador = Player(100, 200, 0.2)

    # sounds
    die = pygame.mixer.Sound('assets/sounds/die.wav')
    lost = pygame.mixer.Sound('assets/sounds/lost.wav')

    labirinto = criar_labirinto()
    velocidade_y = 0.1
    vidas = 3
    make_brakes = 3
    nivel = 1

    tocar(musica_fundo, -1)
    score = 1

    while vidas:
        perdeu, sair, make_brakes, score = jogo(CORES_NIVEL[(nivel - 1) % len(CORES_NIVEL)], coracao, jogador,
                                                (make_brakes, n_make_break_labirinto), velocidade_y, score, vidas,
                                                labirinto.copy(), screen)
        jogador.x = 100
        jogador.y = 200
        if sair:
            break
        if perdeu:
            vidas -= 1
            if vidas != 0:
                tocar(die)
        else:
            # passa de nivel
            velocidade_y += 0.03
            jogador.velocidade += jogador.velocidade * 0.10
            labirinto = criar_labirinto()  # muda de labirinto
            nivel += 1

    musica_fundo.stop()

    if score > HIGHSCORE:
        HIGHSCORE = int(score)

    if vidas == 0:
        tocar(lost)
        gameover(screen, int(score))


def inicio():
    global som

    pygame.display.set_caption('Entombed')
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    background = pygame.image.load("assets/background.png")
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    clicou_sound = False

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

    musica_menu = pygame.mixer.Sound('assets/sounds/menu.mp3')
    tocar(musica_menu, 0)

    clock = pygame.time.Clock()

    while not sair:
        rato_no_insert_coin = insert_coin_rect.collidepoint(*pygame.mouse.get_pos())
        rato_no_sound = sound_rect.collidepoint(*pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sair = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rato_no_insert_coin:  # clicou no insert coin
                    clicou_comecar = True

                if rato_no_sound:
                    clicou_sound = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if rato_no_insert_coin:  # clicou no insert coin
                    if clicou_comecar:
                        # COMECAR JOGO
                        musica_menu.stop()
                        comecar_jogo(screen, 4)
                        tocar(musica_menu, -1)
                    clicou_comecar = False

                if rato_no_sound:
                    if clicou_sound:
                        som = not som
                        tocar(musica_menu, -1)
                        if not som:
                            musica_menu.stop()
                    clicou_sound = False

        dt = clock.tick(10)
        insert_coin_n += dt/1000 * 4            # mudar de cor 4 vezes por segundo
        if insert_coin_n >= len(insert_coin):
            insert_coin_n = 0

        screen.blit(background, (0, 0))
        if rato_no_insert_coin:
            screen.blit(insert_coin_selected, insert_coin_pos)
        else:
            screen.blit(insert_coin[int(insert_coin_n)], insert_coin_pos)

        screen.blit(titulo, (SCREEN_WIDTH/2 - titulo.get_width()/2, SCREEN_HEIGHT * (1/6) - titulo.get_height()/2))

        screen.blit(sound_on if som else sound_off, sound_pos)

        pygame.display.update()

    musica_menu.stop()


pygame.init()
musica_fundo = pygame.mixer.Sound('assets/sounds/musica_fundo.mp3')
musica_fundo.set_volume(.5)
inicio()

pygame.quit()
