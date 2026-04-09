import pygame
import math
from settings import *

# 🆕 Cache de fuentes para mejor rendimiento
FONT_CACHE = {}

def get_font(size, bold=False):
    """🆕 Obtiene fuente del cache"""
    key = (size, bold)
    if key not in FONT_CACHE:
        FONT_CACHE[key] = pygame.font.SysFont("arial", size, bold=bold)
    return FONT_CACHE[key]

def draw_text(screen, text, font, color, x, y, center=False):
    """🆕 Helper para dibujar texto con alineación"""
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect()
    
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    
    screen.blit(text_surf, text_rect)
    return text_rect

def draw_hud(screen, player):
    """
    🆕 HUD mejorado con:
    - Información detallada del jugador
    - Barra de boost
    - Estado de salud visual
    - Ranking en tiempo real
    """
    font_large = get_font(32, bold=True)
    font_medium = get_font(24, bold=False)
    font_small = get_font(18, bold=False)

    # 🎯 Panel superior izquierdo
    panel_x, panel_y = 15, 15
    panel_width = 280
    panel_height = 160

    # 🆕 Fondo del panel (semi-transparente)
    panel_surf = pygame.Surface((panel_width, panel_height))
    panel_surf.set_alpha(200)
    panel_surf.fill((20, 20, 40))
    screen.blit(panel_surf, (panel_x, panel_y))

    # 🆕 Borde del panel
    pygame.draw.rect(screen, (100, 150, 255), 
                     (panel_x, panel_y, panel_width, panel_height), 2)

    # Nombre del jugador (grande)
    draw_text(screen, player.name, font_large, (100, 200, 255),
              panel_x + 15, panel_y + 10)

    # Score principal (con colores dinámicos)
    score_color = (0, 255, 100) if player.score > 50 else (255, 255, 100) if player.score > 20 else (255, 150, 100)
    draw_text(screen, f"Score: {player.score}", font_medium, score_color,
              panel_x + 15, panel_y + 45)

    # Masa (tamaño)
    draw_text(screen, f"Masa: {int(player.mass)}", font_medium, (255, 100, 100),
              panel_x + 15, panel_y + 75)

    # Kills
    draw_text(screen, f"Kills: {player.kills}", font_medium, (100, 255, 100),
              panel_x + 15, panel_y + 105)

    # 🆕 Barra de boost (parte derecha del HUD)
    boost_x = panel_x + 160
    boost_y = panel_y + 50
    boost_width = 100
    boost_height = 20

    # Fondo de barra
    pygame.draw.rect(screen, (60, 60, 60), 
                     (boost_x, boost_y, boost_width, boost_height), 1)

    # Barra de boost (proporcional a la masa)
    boost_fill = int(boost_width * (player.mass / 100))
    pygame.draw.rect(screen, (255, 200, 0),
                     (boost_x, boost_y, boost_fill, boost_height))

    draw_text(screen, "Boost", font_small, (200, 200, 200),
              boost_x, boost_y - 20)

    # 🆕 Información adicional
    lifetime = int(player.get_lifetime())
    minutes = lifetime // 60
    seconds = lifetime % 60
    draw_text(screen, f"Tiempo: {minutes}:{seconds:02d}", font_small, (150, 150, 200),
              panel_x + 15, panel_y + 135)

    # 🆕 Contador de comida comida
    draw_text(screen, f"Comidas: {player.total_eaten}", font_small, (0, 255, 120),
              boost_x + 30, boost_y + 30)

    # 🆕 Indicador de estado
    if player.boosting:
        pygame.draw.circle(screen, (255, 200, 0), (panel_x + 7, panel_y + 7), 5)
    else:
        pygame.draw.circle(screen, (100, 100, 100), (panel_x + 7, panel_y + 7), 5)


def draw_minimap(screen, snakes, food):
    """
    🆕 Minimapa mejorado con:
    - Borde decorativo
    - Mostrar solo serpientes vivas
    - Escala correcta
    - Cuadro de visión de cámara
    """
    size = MINIMAP_SIZE
    pos_x, pos_y = MINIMAP_POSITION

    # 🆕 Superficie del minimapa
    surf = pygame.Surface((size, size))
    surf.fill(GRID_COLOR)

    scale = size / WORLD_SIZE

    # 🆕 Dibujar comida (pequeña)
    for f in food:
        fx = int(f[0] * scale)
        fy = int(f[1] * scale)
        if 0 <= fx < size and 0 <= fy < size:
            pygame.draw.circle(surf, FOOD_COLOR, (fx, fy), 1)

    # 🆕 Dibujar serpientes (solo vivas)
    for s in snakes:
        if not s.alive:  # 🆕 No mostrar muertas
            continue
            
        x = int(s.body[0][0] * scale)
        y = int(s.body[0][1] * scale)
        
        if 0 <= x < size and 0 <= y < size:
            # 🆕 Tamaño proporcional a la masa
            radius = max(2, int(math.sqrt(s.mass) / 2))
            
            # 🆕 El jugador es más brillante
            color = (255, 200, 100) if not s.is_ai else s.color
            pygame.draw.circle(surf, color, (x, y), radius)
            
            # 🆕 Punto blanco en el centro (cabeza)
            pygame.draw.circle(surf, (255, 255, 255), (x, y), 1)

    # 🆕 Dibujar borde del minimapa
    pygame.draw.rect(screen, (150, 150, 200), 
                     (pos_x - 2, pos_y - 2, size + 4, size + 4), 2)

    # Mostrar minimapa
    screen.blit(surf, (pos_x, pos_y))

    # 🆕 Título del minimapa
    font_small = get_font(14)
    draw_text(screen, "Mapa", font_small, (150, 150, 200),
              pos_x + size // 2, pos_y - 20, center=True)


def draw_ranking(screen, snakes, max_show=5):
    """
    🆕 Muestra ranking en tiempo real de serpientes vivas
    
    Args:
        screen: superficie de pygame
        snakes: lista de serpientes
        max_show: número máximo de serpientes a mostrar
    """
    # Ordenar por score
    sorted_snakes = sorted(snakes, key=lambda s: s.score, reverse=True)[:max_show]
    
    if not sorted_snakes:
        return

    font_medium = get_font(20, bold=True)
    font_small = get_font(16)

    # Posición (parte superior derecha)
    rank_x = WIDTH - 250
    rank_y = 15
    rank_width = 230
    rank_height = 30 + len(sorted_snakes) * 30

    # 🆕 Panel de ranking
    rank_surf = pygame.Surface((rank_width, rank_height))
    rank_surf.set_alpha(200)
    rank_surf.fill((30, 20, 20))
    screen.blit(rank_surf, (rank_x, rank_y))

    # 🆕 Borde
    pygame.draw.rect(screen, (255, 100, 100),
                     (rank_x, rank_y, rank_width, rank_height), 2)

    # Título
    draw_text(screen, "🏆 RANKING", font_medium, (255, 200, 0),
              rank_x + rank_width // 2, rank_y + 5, center=True)

    # 🆕 Mostrar jugadores
    for i, snake in enumerate(sorted_snakes):
        y = rank_y + 35 + (i * 30)
        
        # Número de posición
        pos_text = f"{i+1}. {snake.name[:12]}"
        draw_text(screen, pos_text, font_small, snake.color,
                  rank_x + 10, y)
        
        # Score
        score_text = f"{snake.score}"
        draw_text(screen, score_text, font_small, (255, 255, 100),
                  rank_x + 160, y, center=False)


def draw_game_over(screen, player, snakes):
    """
    🆕 Pantalla de Game Over profesional
    
    Args:
        screen: superficie de pygame
        player: serpiente del jugador
        snakes: todas las serpientes
    """
    # 🆕 Overlay oscuro
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    font_huge = get_font(80, bold=True)
    font_large = get_font(48, bold=True)
    font_medium = get_font(32, bold=False)
    font_small = get_font(24)

    center_x = WIDTH // 2
    center_y = HEIGHT // 2

    # Título GAME OVER (parpadeante rojo)
    game_over_text = "GAME OVER"
    draw_text(screen, game_over_text, font_huge, (255, 0, 0),
              center_x, center_y - 120, center=True)

    # 🆕 Estadísticas finales
    stats_y = center_y - 20
    
    draw_text(screen, f"Score Final: {player.score}", font_large, (0, 255, 100),
              center_x, stats_y, center=True)
    
    draw_text(screen, f"Masa Máxima: {int(player.max_mass)}", font_medium, (255, 150, 0),
              center_x, stats_y + 50, center=True)
    
    draw_text(screen, f"Kills: {player.kills} | Tiempo: {int(player.get_lifetime())}s", 
              font_medium, (255, 100, 100),
              center_x, stats_y + 90, center=True)
    
    # 🆕 Instrucción para reiniciar
    draw_text(screen, "Presiona R para reiniciar", font_small, (100, 255, 100),
              center_x, center_y + 100, center=True)
    
    # 🆕 Mostrar tu ranking
    your_rank = sorted(snakes, key=lambda s: s.score, reverse=True).index(player) + 1 if player in snakes else 0
    draw_text(screen, f"Tu ranking: #{your_rank}", font_small, (200, 200, 255),
              center_x, center_y + 160, center=True)
    
    draw_text(screen, f"Masa Máxima: {int(player.max_mass)}", font_medium, (100, 200, 255),
              center_x, stats_y + 50, center=True)
    
    draw_text(screen, f"Kills: {player.kills}", font_medium, (255, 100, 100),
              center_x, stats_y + 90, center=True)
    
    draw_text(screen, f"Comida Comida: {player.total_eaten}", font_medium, (0, 255, 120),
              center_x, stats_y + 130, center=True)
    
    lifetime = int(player.get_lifetime())
    minutes = lifetime // 60
    seconds = lifetime % 60
    draw_text(screen, f"Tiempo de Vida: {minutes}:{seconds:02d}", font_medium, (200, 200, 100),
              center_x, stats_y + 170, center=True)

    # 🆕 Ganador
    winner = max([s for s in snakes if s.alive], key=lambda s: s.score, default=None)
    if winner:
        winner_color = (255, 200, 0) if winner.is_ai else (100, 255, 100)
        draw_text(screen, f"¡{winner.name} Ganó! ({winner.score} pts)", 
                  font_medium, winner_color,
                  center_x, center_y + 250, center=True)

    # Instrucción
    draw_text(screen, "Presiona R para reiniciar", font_small, (100, 255, 100),
              center_x, center_y + 320, center=True)


def draw_fps(screen, clock):
    """
    🆕 Muestra FPS en la esquina superior derecha
    Útil para debugging
    """
    fps = int(clock.get_fps())
    color = (0, 255, 0) if fps > 50 else (255, 200, 0) if fps > 30 else (255, 0, 0)
    
    font = get_font(16)
    draw_text(screen, f"FPS: {fps}", font, color,
              WIDTH - 80, 10)


def draw_instructions(screen):
    """
    🆕 Muestra instrucciones en pantalla de inicio
    """
    font_large = get_font(48, bold=True)
    font_medium = get_font(32)
    font_small = get_font(24)

    # Overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    center_x = WIDTH // 2
    center_y = HEIGHT // 2

    draw_text(screen, "SLITHER.IO", font_large, (0, 255, 150),
              center_x, center_y - 150, center=True)

    draw_text(screen, "Controles:", font_medium, (255, 255, 100),
              center_x, center_y - 50, center=True)

    draw_text(screen, "🖱️ Mueve el mouse para controlar", font_small, (200, 200, 200),
              center_x, center_y + 10, center=True)

    draw_text(screen, "🖱️ Click izquierdo para boost (gasta masa)", font_small, (200, 200, 200),
              center_x, center_y + 50, center=True)

    draw_text(screen, "Compite con los bots y sé el más grande!", font_small, (100, 255, 100),
              center_x, center_y + 110, center=True)

    draw_text(screen, "Presiona ESPACIO para comenzar", font_medium, (255, 200, 0),
              center_x, center_y + 200, center=True)