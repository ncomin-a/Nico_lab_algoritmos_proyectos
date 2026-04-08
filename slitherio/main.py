import pygame, random
from settings import *
from snake import Snake
from food import generate
from camera import Camera
from ui import draw_hud, draw_minimap
from ranking import save
import particles  # 🆕 Importar partículas

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slither.io")  # 🆕 Título
clock = pygame.time.Clock()

# Inicializar sistema de partículas
particles.particles = []

camera = Camera()
food = generate()

player = Snake(1500, 1500, (255, 0, 0), "Vos")
snakes = [player]

# 🆕 Crear IA con nombres diferentes
bot_names = ["Bot1", "Bot2", "Bot3", "Bot4", "Bot5"]
bot_colors = [(0, 255, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 128, 0)]

for i in range(5):
    snakes.append(Snake(
        random.randint(500, 2500),
        random.randint(500, 2500),
        bot_colors[i],
        bot_names[i],
        is_ai=True
    ))

running = True
game_over = False

while running:
    clock.tick(FPS)

    # 🔶 Manejo de eventos
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        # 🆕 Presionar R para reiniciar después de game over
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r and game_over:
            game_over = False
            particles.particles = []
            food = generate()
            player = Snake(1500, 1500, (255, 0, 0), "Vos")
            snakes = [player]
            for i in range(5):
                snakes.append(Snake(
                    random.randint(500, 2500),
                    random.randint(500, 2500),
                    bot_colors[i],
                    bot_names[i],
                    is_ai=True
                ))

    screen.fill((15, 15, 15))

    # 🔶 Actualizar cámara (solo si el jugador está vivo)
    if player.alive:
        camera.update(player.body[0], player.mass)
    else:
        # 🆕 Seguir la última posición conocida del jugador
        if player.body:
            camera.update(player.body[0], player.mass)

    # 🔶 Dibujar comida
    for f in food:
        x, y = camera.apply(f)
        pygame.draw.circle(screen, (0, 255, 120), (int(x), int(y)), 3)

    # 🔶 Actualizar serpientes
    for s in snakes[:]:
        s.update(food, snakes, camera)
        s.eat(food)
        
        # 🆕 Verificar colisiones
        s.check_collision(snakes)
        
        # 🆕 Eliminar serpientes muertas (excepto el jugador)
        if not s.alive and s != player:
            snakes.remove(s)
    
    # 🆕 Verificar si el jugador murió
    if not player.alive and not game_over:
        game_over = True
        # 🎨 Efecto de explosión al morir
        particles.spawn(player.body[0][0], player.body[0][1], (255, 0, 0), count=30)

    # 🆕 Regenerar comida si es necesario
    if len(food) < FOOD_COUNT * 0.7:
        new_food_count = FOOD_COUNT - len(food)
        for _ in range(new_food_count):
            food.append((
                random.randint(0, WORLD_SIZE),
                random.randint(0, WORLD_SIZE)
            ))

    # 🔶 Dibujar serpientes
    for s in snakes:
        s.draw(screen, camera)

    # 🆕 Actualizar y dibujar partículas
    particles.update_all()
    particles.draw_all(screen, camera)

    # 🔶 Dibujar HUD
    draw_hud(screen, player)
    draw_minimap(screen, snakes, food)

    # 🆕 Mostrar Game Over
    if game_over:
        font_large = pygame.font.SysFont("arial", 72, bold=True)
        font_small = pygame.font.SysFont("arial", 36)
        
        # Fondo oscuro semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Texto GAME OVER
        game_over_text = font_large.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2-50))
        screen.blit(game_over_text, game_over_rect)
        
        # Estadísticas finales
        stats_text = font_small.render(
            f"Score: {player.score} | Masa: {int(player.max_mass)} | Kills: {player.kills}",
            True, (255, 255, 255)
        )
        stats_rect = stats_text.get_rect(center=(WIDTH//2, HEIGHT//2+30))
        screen.blit(stats_text, stats_rect)
        
        # Instrucción para reiniciar
        restart_text = font_small.render("Presiona R para reiniciar", True, (100, 255, 100))
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2+100))
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()

pygame.quit()
save(player.name, player.score)