import pygame
import random
from constantes import *

VELOCIDADE = 0.15


class Monstro:
    direcao = DIR
    anterior = DIR
    acordado = False
    centro = False

    def __init__(self, x, y, calmo, gravidade, SQ_SIZE):
        self.calmo = calmo
        self.size = int(SQ_SIZE * 0.7), int(SQ_SIZE * 0.7)

        self.imagem_list = []
        if calmo:
            self.imagem_list = [pygame.image.load('assets/monstros/calmo_1.png'),
                                pygame.image.load('assets/monstros/calmo_2.png')]
        else:
            self.imagem_list = [pygame.image.load('assets/monstros/agressivo_1.png'),
                                pygame.image.load('assets/monstros/agressivo_2.png')]

        for i, img in enumerate(self.imagem_list):
            self.imagem_list[i] = pygame.transform.scale(img, self.size)
            self.imagem_list[i].set_colorkey(WHITE)

        self.gravidade = gravidade
        self.x = x
        self.y = y + (SQ_SIZE - self.size[1]) / 2

    def mover(self, dt, colide_labirinto, cordenadas_word_2_lab, cordenadas_lab_2_word):
        self.y -= self.gravidade * dt
        if self.acordado:
            if self.calmo:
                self.direcao = self.direcao if random.randint(0, 1000) > 2 else CIMA  # Quando se lembra sobe
                if self.direcao == DIR:
                    # Anda para a direita até encontrar um obstaculo quando encontra pode andar para
                    # o lado contrario ou subir
                    if colide_labirinto(pygame.Rect(self.x + dt * VELOCIDADE, self.y, *self.size)):
                        self.direcao = CIMA if random.randint(0, 1) else ESQ
                        self.anterior = DIR
                    else:
                        self.x += dt * VELOCIDADE
                elif self.direcao == ESQ:
                    # Anda para a esquerda até encontrar um obstaculo quando encontra pode andar para
                    # o lado contrario ou subir
                    if colide_labirinto(pygame.Rect(self.x - dt * VELOCIDADE, self.y, *self.size)):
                        self.direcao = CIMA if random.randint(0, 1) else DIR
                        self.anterior = ESQ
                    else:
                        self.x -= dt * VELOCIDADE
                elif self.direcao == CIMA:
                    # Se estiver a andar para cima anda até nao conseguir mais e depois,
                    # se antes de subir estava a andar para a esquerda começa a andar para a direita de nao o contrario
                    if colide_labirinto(pygame.Rect(self.x, self.y - dt * VELOCIDADE, *self.size)):
                        self.y += 1
                        self.direcao = DIR if self.anterior == ESQ else ESQ
                        self.anterior = CIMA
                    else:
                        self.y -= dt * VELOCIDADE

                # Se chegar ao centro de um quadrado em y

                if 0 <= abs(cordenadas_word_2_lab((self.x, self.y))[1] % 1) < 0.01:
                    if not self.centro:
                        # mexe o x e o y para o centro
                        self.y -= abs(cordenadas_word_2_lab((self.x, self.y))[1] % 1)

                        self.direcao = random.choice([DIR, ESQ] + [CIMA] * 3)  # quando se lembra vira
                        self.centro = True
                else:
                    self.centro = False

            else:
                # Quando nao e calmo pode andar nas paredes
                # Tem comportamento imprevisivel

                if self.direcao == ESQ:
                    # Verifica se sai do labirinto, se o x for 1
                    if int(cordenadas_word_2_lab((self.x - dt * VELOCIDADE, self.y))[0]) <= 1:
                        self.x = cordenadas_lab_2_word((2, 0))[0]
                        self.direcao = DIR
                    else:
                        self.x -= dt * VELOCIDADE
                elif self.direcao == DIR:
                    # Verifica se sai do labirinto, se o x for 2
                    if int(cordenadas_word_2_lab((self.x + self.size[0] + dt * VELOCIDADE, self.y))[0]) >= 18:
                        self.x = cordenadas_lab_2_word((18, 0))[0] - self.size[0]
                        self.direcao = ESQ
                    else:
                        self.x += dt * VELOCIDADE
                elif self.direcao == CIMA:
                    self.y -= dt * VELOCIDADE
                # Se chegar ao centro de um quadrado
                dist_c_x, dist_c_y = cordenadas_word_2_lab((self.x + self.size[0] / 2, self.y + self.size[1] / 2))

                if 0 <= abs(dist_c_x % 1 - 0.5) < 0.1 and 0 <= abs(dist_c_y % 1 - 0.5) < 0.1:
                    if not self.centro:
                        # mexe o x e o y para o centro
                        r = dist_c_x
                        self.x -= r % 1 - 0.5
                        self.y -= abs(dist_c_y % 1)
                        self.direcao = random.choice([(DIR if r < 10 else ESQ), DIR, ESQ, self.direcao, CIMA])
                        self.centro = True
                else:
                    self.centro = False

    def desenhar(self, screen):
        i = 0
        if self.direcao == ESQ:
            i = 1
        screen.blit(self.imagem_list[i], (self.x, self.y))

    def colide(self, figura):
        return figura.colliderect(pygame.Rect(self.x, self.y, *self.size))
