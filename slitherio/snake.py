import pygame
import random
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from constants import *
from snake import PlayerSnake, BotSnake
from food import generate
from camera import Camera
from ui import draw_hud, draw_minimap
from ranking import save
import particles


# =========================
# 🧠 SPAWN BOTS
# =========================
def spawn_bots(snakes, count=1):
    bot_ids = [s.id for s in snakes if not s.is_human]
    next_id = max(bot_ids) + 1 if bot_ids else 100

    for i in range(count):
        color_info = BOT_COLORS[(next_id + i) % len(BOT_COLORS)]
        bot = BotSnake(
            color_info,
            next_id + i,
            difficulty=1.0,
            x=random.randint(300, WORLD_W - 300),
            y=random.randint(300, WORLD_H - 300)
        )
        snakes.append(bot)


# =========================
# 💥 DROP FOOD
# =========================
def drop_food_from_snake(snake, food_list):
    for drop_pos in snake.get_food_drops():
        food_list.append(drop_pos)


# =========================
# 🎮 GAME
# =========================
def run_game(player_name):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Slither.io PRO")
    clock = pygame.time.Clock()

    particles.particles = []
    camera = Camera()
    food = generate()

    player_color = PLAYER_COLORS[0]
    player = PlayerSnake(player_color, 0, PLAYER_KEYS[0], x=WORLD_W//2, y=WORLD_H//2)
    snakes = [player]

    spawn_bots(snakes, BOT_COUNT_DEFAULT)

    running = True
    game_over = False

    # =========================
    # 🔥 IMPORTANTE: smooth target init
    # =========================
    player.smooth_target = (WORLD_W//2, WORLD_H//2)

    while running:
        dt = clock.tick(FPS) / 1000.0
        if dt > 0.05:
            dt = 0.05

        # =========================
        # INPUT
        # =========================
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return False

                if e.key == pygame.K_r and game_over:
                    pygame.quit()
                    return run_game(player_name)

        # =========================
        # CAMERA
        # =========================
        if player.alive and player.segments:
            mass = len(player.segments) * SEGMENT_RADIUS
            target_zoom = max(0.3, min(1.5, 50 / (mass / 10 + 1)))

            camera.zoom += (target_zoom - camera.zoom) * 0.08
            camera.update((player.head.x, player.head.y), mass)

        # =========================
        # PLAYER INPUT (🔥 MEJORADO)
        # =========================
        if player.alive:
            mouse_pos = pygame.mouse.get_pos()

            # 🎯 MOVIMIENTO TIPO SLITHER.IO REAL
            head_x = player.head.x
            head_y = player.head.y

            target_x = mouse_pos[0] / camera.zoom + camera.x
            target_y = mouse_pos[1] / camera.zoom + camera.y

            sx, sy = player.smooth_target

            sx += (target_x - sx) * 0.25
            sy += (target_y - sy) * 0.25

            player.smooth_target = (sx, sy)

            dx = sx - head_x
            dy = sy - head_y

            dist = math.hypot(dx, dy)
            if dist != 0:
                dx /= dist
                dy /= dist

            speed = player.boost_speed if player.boosting else player.speed

            player.head.x += dx * speed
            player.head.y += dy * speed

            player.boosting = pygame.key.get_pressed()[pygame.K_SPACE] or pygame.key.get_pressed()[pygame.K_LSHIFT]

        # =========================
        # UPDATE SNAKES
        # =========================
        for s in snakes:
            if s.alive:
                if s.is_human:
                    s.update(dt)
                else:
                    s.ai_update(dt, food, snakes, [])

        # =========================
        # FOOD
        # =========================
        eaten = []
        for food_item in food:
            fx, fy = food_item
            for snake in snakes:
                if not snake.alive:
                    continue
                hx, hy = snake.head.x, snake.head.y

                if (hx - fx) ** 2 + (hy - fy) ** 2 < (SEGMENT_RADIUS + FOOD_RADIUS) ** 2:
                    snake.grow()
                    eaten.append(food_item)
                    break

        for f in eaten:
            food.remove(f)

        if len(food) < FOOD_COUNT:
            for _ in range(FOOD_COUNT - len(food)):
                food.append((
                    random.randint(0, WORLD_W),
                    random.randint(0, WORLD_H)
                ))

        # =========================
        # COLLISIONS
        # =========================
        dead_snakes = []
        for s in snakes:
            if not s.alive or s == player:
                continue

            if player.alive and player.collides_with_snake(s, skip_head=False):
                if len(player.segments) > len(s.segments) + 2:
                    s.die(killer=player)
                    dead_snakes.append(s)
                else:
                    player.die(killer=s)
                    game_over = True

        for i, s1 in enumerate(snakes):
            if not s1.alive:
                continue
            for s2 in snakes[i + 1:]:
                if not s2.alive:
                    continue
                if s1.collides_with_snake(s2, skip_head=False):
                    if len(s1.segments) > len(s2.segments) + 2:
                        s2.die(killer=s1)
                        dead_snakes.append(s2)
                    else:
                        s1.die(killer=s2)
                        dead_snakes.append(s1)

        for s in dead_snakes:
            if s in snakes:
                drop_food_from_snake(s, food)
                snakes.remove(s)

        # =========================
        # BOT RESPAWN
        # =========================
        if sum(1 for s in snakes if not s.is_human) < BOT_COUNT_DEFAULT:
            spawn_bots(snakes, 1)

        # =========================
        # DRAW
        # =========================
        screen.fill(C_BG)

        for f in food:
            x, y = camera.apply(f)
            x = int(x + WIDTH // 2)
            y = int(y + HEIGHT // 2)
            pygame.draw.circle(screen, (0, 255, 140), (x, y), FOOD_RADIUS)

        for s in snakes:
            if s.alive:
                s.draw(screen, camera.x, camera.y)

        particles.update_all()
        particles.draw_all(screen, camera)

        draw_hud(screen, player)
        draw_minimap(screen, snakes, food)

        if game_over and not player.alive:
            font = pygame.font.SysFont("arial", 60, bold=True)
            txt = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))

        pygame.display.flip()

    pygame.quit()

    if player.score > 0:
        try:
            save(player.name, player.score)
        except:
            pass

    return True


if __name__ == "__main__":
    name = input("Enter your name: ").strip() or "Player"
    run_game(name)