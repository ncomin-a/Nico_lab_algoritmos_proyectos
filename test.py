import pygame
import math
import random

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 800, 600
WORLD_SIZE = 3000
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Slither.io PRO")
clock = pygame.time.Clock()

BG = (18, 18, 18)
SNAKE_COLOR = (0, 220, 0)
FOOD_COLOR = (220, 60, 60)

# ---------------- CAMERA ----------------
class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

    def update(self, target):
        tx, ty = target
        self.x += (tx - WIDTH // 2 - self.x) * 0.08
        self.y += (ty - HEIGHT // 2 - self.y) * 0.08

    def apply(self, pos):
        return (pos[0] - self.x, pos[1] - self.y)


camera = Camera()

# ---------------- SNAKE ----------------
class Snake:
    def __init__(self):
        self.segments = [(WORLD_SIZE // 2, WORLD_SIZE // 2)]
        self.length = 35
        self.speed = 4
        self.boost_speed = 7
        self.boosting = False

        self.smooth_target = (WORLD_SIZE // 2, WORLD_SIZE // 2)

    def update(self, mouse_pos):
        head_x, head_y = self.segments[0]

        # mouse en mundo
        target_x = mouse_pos[0] + camera.x
        target_y = mouse_pos[1] + camera.y

        # suavizado del objetivo (CLAVE del feeling)
        sx, sy = self.smooth_target
        sx += (target_x - sx) * 0.25
        sy += (target_y - sy) * 0.25
        self.smooth_target = (sx, sy)

        # dirección normalizada
        dx = sx - head_x
        dy = sy - head_y
        dist = math.hypot(dx, dy)

        if dist != 0:
            dx /= dist
            dy /= dist

        speed = self.boost_speed if self.boosting else self.speed

        new_x = head_x + dx * speed
        new_y = head_y + dy * speed

        # límites del mundo
        new_x = max(0, min(WORLD_SIZE, new_x))
        new_y = max(0, min(WORLD_SIZE, new_y))

        self.segments.insert(0, (new_x, new_y))

        if len(self.segments) > self.length:
            self.segments.pop()

    def draw(self, surface):
        for i, (x, y) in enumerate(self.segments):
            cx, cy = camera.apply((x, y))
            radius = max(2, 10 - i // 6)
            pygame.draw.circle(surface, SNAKE_COLOR, (int(cx), int(cy)), radius)


# ---------------- FOOD ----------------
class Food:
    def __init__(self):
        self.pos = (random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE))

    def respawn(self):
        self.pos = (random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE))

    def draw(self, surface):
        cx, cy = camera.apply(self.pos)
        pygame.draw.circle(surface, FOOD_COLOR, (int(cx), int(cy)), 5)


# ---------------- INIT ----------------
snake = Snake()
foods = [Food() for _ in range(80)]

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                snake.boosting = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                snake.boosting = False

    mouse = pygame.mouse.get_pos()

    # UPDATE
    snake.update(mouse)
    camera.update(snake.segments[0])

    # COLISIÓN COMIDA
    head = snake.segments[0]
    for food in foods:
        if math.hypot(head[0] - food.pos[0], head[1] - food.pos[1]) < 12:
            snake.length += 8
            food.respawn()

    # DRAW
    screen.fill(BG)

    for food in foods:
        food.draw(screen)

    snake.draw(screen)

    pygame.display.flip()

pygame.quit()