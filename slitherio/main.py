import pygame
import random
import sys
import os
import math

# Ensure the script can find modules in its directory
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
    """Spawns new bot snakes"""
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
# 💥 DROP FOOD FROM DEAD SNAKE
# =========================
def drop_food_from_snake(snake, food_list):
    """Drops food when a snake dies"""
    drops = snake.get_food_drops()
    for drop_pos in drops:
        food_list.append(drop_pos)


# =========================
# 🎮 MAIN GAME LOOP
# =========================
def run_game(player_name):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Slither.io PRO")
    clock = pygame.time.Clock()

    particles.particles = []
    camera = Camera()
    food = generate()
    powerups = []

    # Create player snake
    player_color = PLAYER_COLORS[0]
    player = PlayerSnake(player_color, 0, PLAYER_KEYS[0], x=WORLD_W//2, y=WORLD_H//2)
    snakes = [player]

    # Spawn initial bots
    spawn_bots(snakes, BOT_COUNT_DEFAULT)

    running = True
    game_over = False
    delta_time = 1.0 / FPS

    # Font for drawing names
    name_font = pygame.font.SysFont("arial", 16, bold=True)

    while running:
        dt = clock.tick(FPS) / 1000.0  # Convert to seconds
        if dt > 0.05:  # Cap dt to prevent huge jumps
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
        # CAMERA UPDATE (before input for accurate mouse transform)
        # =========================
        if player.alive and player.segments:
            # Calculate zoom based on snake size
            mass = len(player.segments) * SEGMENT_RADIUS
            target_zoom = max(0.3, min(1.5, 50 / (mass / 10 + 1)))
            
            # Smooth zoom
            zoom_diff = target_zoom - camera.zoom
            camera.zoom += zoom_diff * 0.08

            # Update camera position
            camera.update((player.head.x, player.head.y), mass)

        # Handle player input
        if player.alive:
            mouse_pos = pygame.mouse.get_pos()
            player.handle_mouse_input(mouse_pos, camera.x, camera.y, camera.zoom)
            
            # Handle boost with SPACE or LSHIFT
            keys_held = pygame.key.get_pressed()
            player.boosting = keys_held[pygame.K_SPACE] or keys_held[pygame.K_LSHIFT]

        # =========================
        # UPDATE SNAKES
        # =========================
        for s in snakes:
            if s.alive:
                if s.is_human:
                    s.update(dt)
                else:
                    s.ai_update(dt, food, snakes, powerups)

        # =========================
        # FOOD EATING
        # =========================
        eaten = []
        for food_item in food:
            fx, fy = food_item
            # Check all snakes eating food
            for snake in snakes:
                if not snake.alive:
                    continue
                hx, hy = snake.head.x, snake.head.y
                dist_sq = (hx - fx) ** 2 + (hy - fy) ** 2
                if dist_sq < (SEGMENT_RADIUS + FOOD_RADIUS) ** 2:
                    snake.grow()
                    eaten.append(food_item)
                    break

        for f in eaten:
            food.remove(f)

        # =========================
        # COLLISION DETECTION
        # =========================
        dead_snakes = []
        for s in snakes:
            if not s.alive or s == player:
                continue
            # Check if player collides with this snake
            if player.alive and player.collides_with_snake(s, skip_head=False):
                if len(player.segments) > len(s.segments) + 2:
                    s.die(killer=player)
                    dead_snakes.append(s)
                elif not player.has_shield:
                    player.die(killer=s)
                    game_over = True

        # Check inter-snake collisions
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
                    elif len(s2.segments) > len(s1.segments) + 2:
                        s1.die(killer=s2)
                        dead_snakes.append(s1)

        # Remove dead snakes and drop their food
        for s in dead_snakes:
            if s in snakes:
                drop_food_from_snake(s, food)
                snakes.remove(s)

        # =========================
        # FOOD REGENERATION
        # =========================
        if len(food) < FOOD_COUNT:
            for _ in range(FOOD_COUNT - len(food)):
                food.append((
                    random.randint(0, WORLD_W),
                    random.randint(0, WORLD_H)
                ))

        # Prevent food list from growing too much
        if len(food) > FOOD_COUNT * 1.5:
            food = food[:FOOD_COUNT]

        # =========================
        # BOT RESPAWN
        # =========================
        bots_alive = sum(1 for s in snakes if not s.is_human)
        if bots_alive < BOT_COUNT_DEFAULT:
            spawn_bots(snakes, BOT_COUNT_DEFAULT - bots_alive)

        # =========================
        # DRAW FOOD
        # =========================
        screen.fill(C_BG)

        for f in food:
            screen_x, screen_y = camera.apply(f)
            screen_x = int(screen_x + WIDTH // 2)
            screen_y = int(screen_y + HEIGHT // 2)
            
            # Only draw if in view
            if -50 < screen_x < WIDTH + 50 and -50 < screen_y < HEIGHT + 50:
                pygame.draw.circle(screen, (0, 255, 140), (screen_x, screen_y), FOOD_RADIUS)

        # =========================
        # DRAW SNAKES
        # =========================
        for s in snakes:
            if s.alive:
                s.draw(screen, camera.x, camera.y)

        # =========================
        # PARTICLES
        # =========================
        particles.update_all()
        particles.draw_all(screen, camera)

        # =========================
        # UI
        # =========================
        draw_hud(screen, player)
        draw_minimap(screen, snakes, food)

        # =========================
        # GAME OVER SCREEN
        # =========================
        if game_over and not player.alive:
            font_big = pygame.font.SysFont("arial", 70, bold=True)
            font_small = pygame.font.SysFont("arial", 30)

            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(160)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            txt_go = font_big.render("GAME OVER", True, (255, 0, 0))
            screen.blit(txt_go, (WIDTH//2 - txt_go.get_width()//2, HEIGHT//2 - 80))

            stats = font_small.render(
                f"Score: {int(player.score)} | Length: {player.length} | Kills: {player.kills}",
                True,
                (255, 255, 255)
            )
            screen.blit(stats, (WIDTH//2 - stats.get_width()//2, HEIGHT//2))

            restart = font_small.render(
                "R = Restart | ESC = Exit",
                True,
                (100, 255, 100)
            )
            screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 60))

        pygame.display.flip()

    pygame.quit()

    if player.score > 0:
        try:
            save(player.name, player.score)
        except Exception as e:
            print(f"Error saving score: {e}")

    return True


if __name__ == "__main__":
    name = input("Enter your name: ").strip() or "Player"
    run_game(name)