import pygame
from settings import *

def draw_hud(screen, player):
    font = pygame.font.SysFont(None, 28)

    screen.blit(font.render(f"Score: {player.score}",True,(255,255,255)),(10,10))
    screen.blit(font.render(f"Kills: {player.kills}",True,(255,255,255)),(10,30))
    screen.blit(font.render(f"Masa: {int(player.mass)}",True,(255,255,255)),(10,50))

def draw_minimap(screen, snakes, food):
    size = 200
    surf = pygame.Surface((size,size))
    surf.fill((30,30,30))

    scale = size / WORLD_SIZE

    for f in food:
        pygame.draw.circle(surf,(0,255,100),(int(f[0]*scale),int(f[1]*scale)),2)

    for s in snakes:
        x = int(s.body[0][0]*scale)
        y = int(s.body[0][1]*scale)
        pygame.draw.circle(surf,s.color,(x,y),4)

    screen.blit(surf,(WIDTH-size-10,10))