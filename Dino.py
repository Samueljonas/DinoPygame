import pygame
from pygame.locals import *
from sys import exit
import os 
from random import randrange, choice

pygame.init()
pygame.mixer.init()

###                         VARIAVEIS
largura = 640
altura = 480
BRANCO = (255,255,255)
pasta_principal = os.path.dirname(__file__)
diretorio_imagens = os.path.join(pasta_principal, 'img')
diretorio_sons = os.path.join(pasta_principal, "sons")
relogio = pygame.time.Clock()
som_colis = pygame.mixer.Sound(os.path.join(diretorio_sons, "death_sound.wav"))
som_colis.set_volume(0.25)
colidiu = False
escolha_obsta = choice([0,1])
pontos = 0
som_pts = pygame.mixer.Sound(os.path.join(diretorio_sons, "score_sound.wav"))
som_pts.set_volume(0.1)
velocidade_jogo = 10
ranking = {}


def salvar_recorde(nome, pts):
    with open("recordes.txt", "a") as arquivo:
        arquivo.write(f"{nome}:{pts}\n")

def exibir_ranking():
    try:
        ranking = {}
        with open("recordes.txt", "r") as arquivo:
            for linha in arquivo:
                nome, pontos = linha.strip().split(":")
                ranking[nome] = int(pontos)  # Armazena o nome e a pontuação como um dicionário

        # Ordena o dicionário por pontos em ordem decrescente
        ranking_ordenado = dict(sorted(ranking.items(), key=lambda item: item[1], reverse=True))

        print("\nRanking:")
        for posicao, (nome, pontos) in enumerate(ranking_ordenado.items(), 1):  # Exibe os 10 melhores
            print(f"{posicao}. {nome} - {pontos} pontos")
            if posicao >= 10:  # Limita a exibição aos 10 melhores
                break
    except FileNotFoundError:
        print("Nenhum recorde encontrado.")

def reiniciar_jogo():
    global pontos, velocidade_jogo, colidiu, escolha_obsta
    velocidade_jogo = 10
    pontos = 0
    colidiu = False
    voador.rect.x = largura
    cacto.rect.x = largura
    escolha_obsta = choice([0,1])
    if hasattr(reiniciar_jogo, "salvo"):
        del reiniciar_jogo.salvo  # Remove o atributo salvo para o próximo jogo



def exibe_msg(msg, tam, cor):
    fonte = pygame.font.SysFont('Arial', tam, True, False)
    mensagem = f'{msg}'
    txt_formatado = fonte.render(mensagem, True, cor)
    return txt_formatado


###                         TELA
tela = pygame.display.set_mode((largura,altura))
pygame.display.set_caption('DINO GAME')
sprite_sheet = pygame.image.load(os.path.join(diretorio_imagens, 'dinoSpritesheet.png')).convert_alpha()

###                        CLASSES
###                         DINO
class Dino(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.som_pulo = pygame.mixer.Sound(os.path.join(diretorio_sons, 'jump_sound.wav'))
        self.som_pulo.set_volume(0.1)
        self.imagens_dinossauro = []
        for i in range(3):
            img = sprite_sheet.subsurface(( i * 32 ,0), (32,32))
            img = pygame.transform.scale(img, (32*3, 32*3))
            self.imagens_dinossauro.append(img)
        
        self.index_lista= 0
        self.image = self.imagens_dinossauro[self.index_lista]
        self.rect = self.image.get_rect()
        self.pos_y_inicial = altura -64 -96 / 2
        self.rect.center = (100,altura - 64)
        self.pulo = False
        self.mask = pygame.mask.from_surface(self.image)
    
    def pular(self):
        self.pulo = True
        self.som_pulo.play()
    
    def update(self):
        if self.pulo == True:
            if self.rect.y <=200:
                self.pulo = False
            self.rect.y -= 10
        else:
            if self.rect.y < self.pos_y_inicial:
                self.rect.y += 10
            else:
                self.rect.y = self.pos_y_inicial
        
        if self.index_lista > 2:
            self.index_lista = 0
        self.index_lista += 0.25
        self.image = self.imagens_dinossauro[int(self.index_lista)]

###             NUVENS

class Nuvens(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((7*32, 0), (32,32))
        self.image = pygame.transform.scale(self.image, (32 * 3, 32 * 3))
        self.rect = self.image.get_rect()
        self.rect.y = randrange(50,200,50)
        self.rect.x = largura - randrange(30,300,90)

    def update(self):
        if self.rect.topright[0] < 0:
            self.rect.y = randrange(50, 200, 50)
            self.rect.x = largura
        self.rect.x -= velocidade_jogo

###                 CHÃO

class Chao(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((6 * 32, 0), (32,32))
        self.image = pygame.transform.scale(self.image, (32 * 2, 32 *2))
        self.rect = self.image.get_rect()
        self.rect.y = altura -64
        self.rect.x = pos_x * 64

    def update(self):
        if self.rect.topright[0] <0:
            self.rect.x = largura
        self.rect.x -= 10

##                  CACTO

class Cacto(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((5* 32, 0), (32,32))
        self.image = pygame.transform.scale(self.image, (32*2,32*2))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.escolha = escolha_obsta
        self.rect.center = (largura, altura  -64)
        self.rect.x = largura
    
    def update(self):
        if self.escolha == 0:
            if self.rect.topright[0] < 0:
                self.rect.x = largura
            self.rect.x -= velocidade_jogo

###                  VOADOR

class Voador(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.imagens_dinovoador = []
        for i in range(3,5):
            img = sprite_sheet.subsurface((i*32, 0), (32,32))
            img = pygame.transform.scale(img,(32*3, 32*3))
            self.imagens_dinovoador.append(img)
        
        self.index_lista = 0
        self.image = self.imagens_dinovoador[self.index_lista]
        self.mask = pygame.mask.from_surface(self.image)
        self.escolha = escolha_obsta
        self.rect = self.image.get_rect()
        self.rect.center = (largura, 300)
        self.rect.x = largura

    def update(self):
        if self.escolha == 1:
            if self.rect.topright[0] < 0:
                self.rect.x = largura
            self.rect.x -= velocidade_jogo
            if self.index_lista > 1:
                self.index_lista = 0
            self.index_lista += 0.25
            self.image = self.imagens_dinovoador[int(self.index_lista)]


todas_as_sprites = pygame.sprite.Group()

dino = Dino()
todas_as_sprites.add(dino)

#           instanciando obj nuvem

for i in range(randrange(1,4)):
    nuvem = Nuvens()
    todas_as_sprites.add(nuvem)

#           instanciando obj chão

for i in range (int(largura *2 / 64 )):
    chao = Chao(i)
    todas_as_sprites.add(chao)

#           intanciando obj cacto

cacto = Cacto()
todas_as_sprites.add(cacto)
grupos_colisoes = pygame.sprite.Group()
grupos_colisoes.add(cacto)

#           instanciando dino voador
voador = Voador()
todas_as_sprites.add(voador)
grupos_colisoes.add(voador)

#            Loop principal

while True:
    relogio.tick(60)
    tela.fill(BRANCO)
    ###         loop de eventos
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                if dino.rect.y != dino.pos_y_inicial:
                    pass
                else:
                    dino.pular()
            if event.key == K_r and colidiu == True:
                reiniciar_jogo()


    todas_as_sprites.draw(tela)
    #           obstaculos

    if cacto.rect.topright[0] <= 0 or voador.rect.topright[0] <= 0:
        escolha_obsta = choice([0,1])
        cacto.rect.x = largura
        voador.rect.x = largura
        cacto.escolha = escolha_obsta
        voador.escolha =escolha_obsta


    colisoes = pygame.sprite.spritecollide(dino, grupos_colisoes, False, pygame.sprite.collide_mask)

    if colisoes and colidiu == False:
        colidiu = True
        som_colis.play()
    
    if colidiu == True:
        if pontos % 100 == 0:
            pontos += 1 

        over = exibe_msg("GAME OVER", 40, (0,0,0))
        tela.blit(over, (largura/2, altura/2))
        restart = exibe_msg('Pressione R para reiniciar', 20, (0,0,0))
        tela.blit(restart, (largura/2, (altura/2) + 60))

        # Solicitar nome do usuário ao final do jogo
        if not hasattr(reiniciar_jogo, "salvo"):
            nome = input("Digite seu nome: ")
            salvar_recorde(nome, pontos)
            exibir_ranking()
            reiniciar_jogo.salvo = True  # Impede que salve múltiplas vezes


    else:
        pontos += 1
        todas_as_sprites.update()
        texto_pts = exibe_msg(pontos, 30, (0,0,0))
    if pontos % 100 == 0:
        som_pts.play()
        if velocidade_jogo >= 23:
            velocidade_jogo +=0
        

        velocidade_jogo += 1
    
    tela.blit(texto_pts, (520,30))
    pygame.display.flip()

