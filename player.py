import pygame
from constantes import *


class Player:
    def __init__(self, x, y, velocidade):
        self.x = x
        self.y = y
        self.velocidade = velocidade

        self.imagem = pygame.image.load('assets/jogador.png')
        self.imagem.set_colorkey(WHITE)
        self.size = self.imagem.get_size()
        self.width = self.imagem.get_width()
        self.height = self.imagem.get_height()

        self.virado = NADA

    def retangulo(self):
        return pygame.Rect(self.x, self.y, *self.size)

    def desenhar(self, screen):
        screen.blit(self.imagem, (self.x, self.y))

    def mover(self, direcao, dt, colide_labirinto):
        self.virado = direcao

        add_x = add_y = 0
        if direcao == ESQ:
            add_x = -dt * self.velocidade
        if direcao == DIR:
            add_x = dt * self.velocidade
        if direcao == CIMA:
            add_y = -dt * self.velocidade
        if direcao == BAIXO:
            add_y = dt * self.velocidade

        # Ve se o player ao andar pixeis colide com a parede
        # se colidir nao deixa andar nessa direcao
        if colide_labirinto(pygame.Rect(self.x + add_x, self.y + add_y, *self.size)):
            add_x = 0

            # animacao pequena
            if add_y < 0:
                self.y += 5
            elif add_y > 0:
                self.y -= 5
            add_y = 0

        self.x += add_x
        self.y += add_y
