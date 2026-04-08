import pygame, math, random, time
from settings import *

def distance(a,b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

class Snake:
    def __init__(self, x, y, color, name="Jugador", is_ai=False):
        self.body = [(x,y)]
        self.mass = INITIAL_MASS
        self.length = int(self.mass)
        self.angle = random.random()*6.28
        self.color = color
        self.name = name
        self.is_ai = is_ai
        self.score = 0
        self.boosting = False

        # stats
        self.spawn_time = time.time()
        self.kills = 0
        self.max_mass = self.mass

        self.personality = random.choice(["aggressive","scared","collector"])

    def update(self, food, snakes, camera):
        if self.is_ai:
            self.ai(food, snakes)
        else:
            self.mouse_control(camera)

        speed = SNAKE_SPEED * (20/(self.mass+1))
        if self.boosting:
            speed *= BOOST_MULT
            self.mass -= 0.05

        x,y = self.body[0]
        nx = (x + math.cos(self.angle)*speed) % WORLD_SIZE
        ny = (y + math.sin(self.angle)*speed) % WORLD_SIZE

        self.body.insert(0,(nx,ny))

        self.length = int(self.mass)
        if len(self.body) > self.length:
            self.body.pop()

        if self.mass > self.max_mass:
            self.max_mass = self.mass

    def mouse_control(self, camera):
        mx,my = pygame.mouse.get_pos()
        mx = mx / camera.zoom + camera.x
        my = my / camera.zoom + camera.y

        dx = mx - self.body[0][0]
        dy = my - self.body[0][1]

        self.angle = math.atan2(dy,dx)
        self.boosting = pygame.mouse.get_pressed()[0]

    def ai(self, food, snakes):
        head = self.body[0]

        if self.personality == "aggressive":
            targets = [s for s in snakes if not s.is_ai]
            if targets:
                target = min(targets, key=lambda s: distance(head, s.body[0])).body[0]
                self.boosting = True
            else:
                target = random.choice(food)

        elif self.personality == "scared":
            target = min(food, key=lambda f: distance(head,f))
            for s in snakes:
                if s!=self and distance(head,s.body[0])<150:
                    dx = head[0]-s.body[0][0]
                    dy = head[1]-s.body[0][1]
                    self.angle = math.atan2(dy,dx)
                    return

        else:
            target = min(food, key=lambda f: distance(head,f))

        dx,dy = target[0]-head[0], target[1]-head[1]
        self.angle = math.atan2(dy,dx)

    def eat(self, food_list):
        for f in food_list[:]:
            if distance(self.body[0], f) < 10:
                food_list.remove(f)
                self.mass += 1.5
                self.score += 1
                return True
        return False

    def draw(self, screen, camera):
        radius = max(4, int(self.mass/10))

        for seg in self.body:
            x,y = camera.apply(seg)
            pygame.draw.circle(screen, self.color, (int(x),int(y)), radius)

        # nombre
        font = pygame.font.SysFont(None, 20)
        hx,hy = camera.apply(self.body[0])
        screen.blit(font.render(self.name,True,(255,255,255)),(hx-20,hy-20))