import pygame
import random

# lista global de partículas
particles = []

class Particle:
    def __init__(self, x, y, color, lifetime=30, size=4, vel=None):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.size = size
        if vel:
            self.vel = vel
        else:
            angle = random.uniform(0, 6.28)
            speed = random.uniform(1, 3)
            self.vel = [speed * pygame.math.Vector2(1,0).rotate_rad(angle).x,
                        speed * pygame.math.Vector2(1,0).rotate_rad(angle).y]

    def update(self):
        self.x += self.vel[0]
        self.y += self.vel[1]
        self.lifetime -= 1
        # efecto de fricción
        self.vel[0] *= 0.9
        self.vel[1] *= 0.9

    def draw(self, screen, camera):
        x, y = camera.apply((self.x, self.y))
        pygame.draw.circle(screen, self.color, (int(x), int(y)), self.size)

def spawn(x, y, color, count=10):
    for _ in range(count):
        particles.append(Particle(x, y, color))

def update_all():
    for p in particles[:]:
        p.update()
        if p.lifetime <= 0:
            particles.remove(p)

def draw_all(screen, camera):
    for p in particles:
        p.draw(screen, camera)