import pygame, random
from settings import *
from snake import Snake
from food import generate
from camera import Camera
from ui import draw_hud, draw_minimap
from ranking import save

pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()

camera = Camera()
food = generate()

player = Snake(1500,1500,(255,0,0),"Vos")
snakes = [player]

# IA
for _ in range(5):
    snakes.append(Snake(random.randint(0,3000),random.randint(0,3000),
                        (0,255,0),"Bot",True))

running = True
while running:
    clock.tick(FPS)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    screen.fill((15,15,15))

    camera.update(player.body[0], player.mass)

    # comida
    for f in food:
        x,y = camera.apply(f)
        pygame.draw.circle(screen,(0,255,120),(int(x),int(y)),3)

    # update
    for s in snakes[:]:
        s.update(food, snakes, camera)

        if s.eat(food):
            pass

    # draw
    for s in snakes:
        s.draw(screen, camera)

    draw_hud(screen, player)
    draw_minimap(screen, snakes, food)

    pygame.display.flip()

pygame.quit()
save(player.name, player.score)