import pygame
import random
import sys
import os
import importlib.util

# Ensure the script can find modules in its directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from constants import *
from snake import PlayerSnake, BotSnake
from food import generate, generate_single, generate_single_colored
from camera import Camera
from ui import draw_hud, draw_minimap, draw_ranking, draw_hud_split, draw_splitscreen_divider
from ranking import save
import particles


def draw_food_orb(surface, color, sx, sy, radius=FOOD_RADIUS):
    """Dibuja una bolita con glow al estilo del juego original."""
    # Glow exterior (circulo difuso semitransparente)
    glow_r = radius + 5
    glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
    glow_color = (*color, 80)
    pygame.draw.circle(glow_surf, glow_color, (glow_r, glow_r), glow_r)
    surface.blit(glow_surf, (sx - glow_r, sy - glow_r))
    # Cuerpo principal
    pygame.draw.circle(surface, color, (sx, sy), radius)
    # Brillo interior (destello blanco pequeño)
    bright = (
        min(255, color[0] + 100),
        min(255, color[1] + 100),
        min(255, color[2] + 100),
    )
    pygame.draw.circle(surface, bright, (sx - radius // 3, sy - radius // 3), max(1, radius // 3))


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
    for drop_pos in snake.get_food_drops():
        food_list.append(drop_pos)


# =========================
# 🪟 LOAD START SCREEN
# =========================
def show_start_screen():
    """Carga y ejecuta la pantalla de inicio aunque el archivo tenga espacios."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    menu_path = os.path.join(base_dir, "pantalla de inicio.py")

    spec = importlib.util.spec_from_file_location("pantalla_inicio", menu_path)
    if spec is None or spec.loader is None:
        print("No se pudo cargar la pantalla de inicio.")
        return None

    menu_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(menu_module)

    if hasattr(menu_module, "show_menu"):
        return menu_module.show_menu()

    print("La pantalla de inicio no tiene show_menu().")
    return None


# =========================
# 🎮 SPLITSCREEN GAME LOOP
# =========================
def run_splitscreen(p1_name, p2_name):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Slither.io PRO - Multijugador")
    clock = pygame.time.Clock()

    HALF_W = WIDTH // 2

    particles.particles = []
    food = generate()
    powerups = []

    # Jugador 1: WASD (izquierda)
    p1 = PlayerSnake(PLAYER_COLORS[0], 0, PLAYER_KEYS[0],
                     x=WORLD_W // 2 - 500, y=WORLD_H // 2)
    p1.name = p1_name

    # Jugador 2: Flechitas (derecha)
    p2 = PlayerSnake(PLAYER_COLORS[2], 1, PLAYER_KEYS[1],
                     x=WORLD_W // 2 + 500, y=WORLD_H // 2)
    p2.name = p2_name

    snakes = [p1, p2]

    cam1 = Camera()
    cam2 = Camera()
    cam1.x = p1.head.x - (HALF_W / 2) / cam1.zoom
    cam1.y = p1.head.y - (HEIGHT / 2) / cam1.zoom
    cam2.x = p2.head.x - (HALF_W / 2) / cam2.zoom
    cam2.y = p2.head.y - (HEIGHT / 2) / cam2.zoom

    spawn_bots(snakes, BOT_COUNT_DEFAULT)

    # Superficies para cada mitad
    surf1 = pygame.Surface((HALF_W, HEIGHT))
    surf2 = pygame.Surface((HALF_W, HEIGHT))

    font_big   = pygame.font.SysFont("arial", 60, bold=True)
    font_small = pygame.font.SysFont("arial", 26)

    running = True
    _restart = False

    while running:
        dt = clock.tick(FPS) / 1000.0
        if dt > 0.05:
            dt = 0.05

        # INPUT GLOBAL
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                if e.key == pygame.K_r and (not p1.alive or not p2.alive):
                    running = False
                    _restart = True

        keys = pygame.key.get_pressed()

        # INPUT JUGADORES (teclado directo, sin mouse)
        if p1.alive:
            p1.handle_keyboard_direction(keys, dt)
            p1.boosting = keys[p1.keys["boost"]] and not p1.boost_depleted and p1.boost_energy > 0

        if p2.alive:
            p2.handle_keyboard_direction(keys, dt)
            p2.boosting = keys[p2.keys["boost"]] and not p2.boost_depleted and p2.boost_energy > 0

        # CÁMARAS
        if p1.alive:
            cam1.update((p1.head.x, p1.head.y), len(p1.segments) * SEGMENT_RADIUS, HALF_W)
        if p2.alive:
            cam2.update((p2.head.x, p2.head.y), len(p2.segments) * SEGMENT_RADIUS, HALF_W)

        # UPDATE SERPIENTES
        for s in snakes:
            if s.alive:
                if s.is_human:
                    # handle_keyboard_direction ya seteó target_angle,
                    # PlayerSnake.update() interpola igual que en modo mouse
                    s.update(dt)
                else:
                    s.ai_update(dt, food, snakes, powerups)

        # COMER COMIDA
        eaten = []
        for food_item in food:
            fx, fy = food_item[0], food_item[1]
            for snake in snakes:
                if not snake.alive:
                    continue
                dist_sq = (snake.head.x - fx)**2 + (snake.head.y - fy)**2
                if dist_sq < (SEGMENT_RADIUS + FOOD_RADIUS)**2:
                    snake.grow()
                    eaten.append(food_item)
                    break
        for f in eaten:
            food.remove(f)

        # COLISIONES
        dead_snakes = []
        for i, s1 in enumerate(snakes):
            if not s1.alive:
                continue
            for s2 in snakes[i+1:]:
                if not s2.alive:
                    continue
                if s1.collides_with_snake(s2, skip_head=False):
                    if len(s1.segments) > len(s2.segments) + 2:
                        s2.die(killer=s1)
                        dead_snakes.append(s2)
                    elif len(s2.segments) > len(s1.segments) + 2:
                        s1.die(killer=s2)
                        dead_snakes.append(s1)
                    else:
                        # Mismo tamaño: ambos mueren
                        s1.die(killer=None)
                        s2.die(killer=None)
                        dead_snakes.extend([s1, s2])
        for s in dead_snakes:
            if s in snakes:
                drop_food_from_snake(s, food)
                if not s.is_human:
                    snakes.remove(s)

        # REGENERAR COMIDA
        while len(food) < FOOD_COUNT:
            food.append(generate_single())

        # RESPAWN BOTS
        bots_alive = sum(1 for s in snakes if not s.is_human)
        if bots_alive < BOT_COUNT_DEFAULT:
            spawn_bots(snakes, BOT_COUNT_DEFAULT - bots_alive)

        # ========================= DIBUJO =========================
        name_font = pygame.font.SysFont("arial", 14)

        def draw_half(surf, cam, half_offset_x):
            surf.fill(C_BG)
            # Comida
            for f in food:
                sx, sy = cam.apply((f[0], f[1]))
                sx, sy = int(sx), int(sy)
                if -50 < sx < HALF_W + 50 and -50 < sy < HEIGHT + 50:
                    draw_food_orb(surf, f[2], sx, sy)
            # Serpientes — dibujar relativo a esta cámara en la mitad
            for s in snakes:
                if not s.alive:
                    continue
                # Redirigir draw al surf con esta cámara
                s.draw(surf, cam)
                s.draw_name(surf, cam, name_font)

        draw_half(surf1, cam1, 0)
        draw_half(surf2, cam2, HALF_W)

        # HUDs por mitad
        draw_hud_split(surf1, p1, 0, HALF_W, (100, 200, 255))
        draw_hud_split(surf2, p2, 0, HALF_W, (255, 110, 110))

        # Volcar mitades a pantalla
        screen.blit(surf1, (0, 0))
        screen.blit(surf2, (HALF_W, 0))

        # Línea divisoria
        draw_splitscreen_divider(screen)

        # Pantallas de game over individuales
        for surf, player, ox in [(surf1, p1, 0), (surf2, p2, HALF_W)]:
            if not player.alive:
                ov = pygame.Surface((HALF_W, HEIGHT), pygame.SRCALPHA)
                ov.fill((0, 0, 0, 140))
                screen.blit(ov, (ox, 0))

                killer_name = player.killed_by.name if player.killed_by else "el mundo"
                lines = [
                    ("MUERTO", font_big, (255, 60, 60)),
                    (f"Eliminado por {killer_name}", font_small, (255, 200, 200)),
                    (f"Score: {player.score}  |  Kills: {player.kills}", font_small, (255, 255, 255)),
                    ("R = reiniciar  |  ESC = salir", font_small, (100, 255, 100)),
                ]
                cy = HEIGHT // 2 - 80
                for text, font, color in lines:
                    surf_t = font.render(text, True, color)
                    screen.blit(surf_t, (ox + HALF_W//2 - surf_t.get_width()//2, cy))
                    cy += surf_t.get_height() + 10

        pygame.display.flip()

    for p in [p1, p2]:
        if p.score > 0:
            try:
                save(p.name, p.score)
            except Exception as e:
                print(f"Error saving score: {e}")
    
    pygame.quit()
    return _restart


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
    player = PlayerSnake(player_color, 0, PLAYER_KEYS[0], x=WORLD_W // 2, y=WORLD_H // 2)
    player.name = player_name
    snakes = [player]

    # Center camera on the player from the start
    camera.x = player.head.x - (WIDTH / 2) / camera.zoom
    camera.y = player.head.y - (HEIGHT / 2) / camera.zoom

    # Spawn initial bots
    spawn_bots(snakes, BOT_COUNT_DEFAULT)

    running = True
    game_over = False

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
        # CAMERA UPDATE
        # =========================
        if player.alive and player.segments:
            mass = len(player.segments) * SEGMENT_RADIUS
            camera.update((player.head.x, player.head.y), mass)

        # =========================
        # PLAYER INPUT
        # =========================
        if player.alive:
            mouse_pos = pygame.mouse.get_pos()
            player.handle_mouse_input(mouse_pos, camera.x, camera.y, camera.zoom)

            keys_held = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            player.boosting = mouse_buttons[0] and not player.boost_depleted and player.boost_energy > 0
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
            fx, fy = food_item[0], food_item[1]
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

            # 🔥 si el BOT toca al PLAYER (cuerpo)
            if s.collides_with_snake(player, skip_head=True):
                if not getattr(s, "has_shield", False):
                    s.die(killer=player)
                    dead_snakes.append(s)

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

        for s in dead_snakes:
            if s in snakes:
                drop_food_from_snake(s, food)
                snakes.remove(s)

        # =========================
        # FOOD REGENERATION
        # =========================
        if len(food) < FOOD_COUNT:
            for _ in range(FOOD_COUNT - len(food)):
                food.append(generate_single())

        if len(food) > FOOD_COUNT * 1.5:
            food = food[:FOOD_COUNT]

        # =========================
        # BOT RESPAWN
        # =========================
        bots_alive = sum(1 for s in snakes if not s.is_human)
        if bots_alive < BOT_COUNT_DEFAULT:
            spawn_bots(snakes, BOT_COUNT_DEFAULT - bots_alive)

        # =========================
        # DRAW
        # =========================
        screen.fill(C_BG)

        for f in food:
            screen_x, screen_y = camera.apply((f[0], f[1]))
            screen_x = int(screen_x)
            screen_y = int(screen_y)
            if -50 < screen_x < WIDTH + 50 and -50 < screen_y < HEIGHT + 50:
                draw_food_orb(screen, f[2], screen_x, screen_y)

        for s in snakes:
            if s.alive:
                s.draw(screen, camera)
                s.draw_name(screen, camera, pygame.font.SysFont("arial", 14))

        particles.update_all()
        particles.draw_all(screen, camera)

        draw_hud(screen, player)
        draw_minimap(screen, snakes, food)
        draw_ranking(screen, snakes, player=player)

        if game_over and not player.alive:
            font_big = pygame.font.SysFont("arial", 70, bold=True)
            font_small = pygame.font.SysFont("arial", 30)

            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(160)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            txt_go = font_big.render("GAME OVER", True, (255, 0, 0))
            screen.blit(txt_go, (WIDTH // 2 - txt_go.get_width() // 2, HEIGHT // 2 - 80))

            stats = font_small.render(
                f"Score: {int(player.score)} | Length: {player.length} | Kills: {player.kills}",
                True,
                (255, 255, 255)
            )
            screen.blit(stats, (WIDTH // 2 - stats.get_width() // 2, HEIGHT // 2))

            restart = font_small.render(
                "R = Restart | ESC = Exit",
                True,
                (100, 255, 100)
            )
            screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 60))

        pygame.display.flip()

    pygame.quit()

    if player.score > 0:
        try:
            save(player.name, player.score)
        except Exception as e:
            print(f"Error saving score: {e}")

    return True

if __name__ == "__main__":
    while True:
        result = show_start_screen()
        if result is None:
            break
        
        if isinstance(result, tuple):
            # Modo multijugador: (modo, nombre1, nombre2)
            mode, name1, name2 = result
            if mode == "splitscreen":
                restart = run_splitscreen(name1, name2)
                # Si restart es False, vuelve a la pantalla inicial
                # Si restart es True, continúa el loop para mostrar pantalla inicial
        else:
            run_game(result)