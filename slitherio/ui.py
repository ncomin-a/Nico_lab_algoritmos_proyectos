import pygame
import math
from constants import *

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
    draw_text(screen, f"Length: {player.length}", font_medium, (255, 100, 100),
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

    # Barra de boost (proporcional a la energía real)
    boost_fill = int(boost_width * (player.boost_energy / player.max_boost_energy))
    if getattr(player, "boost_depleted", False):
        boost_color = (180, 60, 60)  # rojo oscuro = bloqueado
    elif player.boost_energy < player.max_boost_energy * 0.5:
        boost_color = (255, 80, 80)  # rojo = bajo
    else:
        boost_color = (255, 200, 0)  # amarillo = disponible
    pygame.draw.rect(screen, boost_color,
                     (boost_x, boost_y, boost_fill, boost_height))
    # Línea indicando el umbral del 50%
    mid_x = boost_x + boost_width // 2
    pygame.draw.line(screen, (255, 255, 255), (mid_x, boost_y), (mid_x, boost_y + boost_height), 1)

    draw_text(screen, "Boost", font_small, (200, 200, 200),
              boost_x, boost_y - 20)

    # 🆕 Información adicional
    lifetime = int(player.lifetime)
    minutes = lifetime // 60
    seconds = lifetime % 60
    draw_text(screen, f"Time: {minutes}:{seconds:02d}", font_small, (150, 150, 200),
              panel_x + 15, panel_y + 135)

    # 🆕 Contador de comida comida
    draw_text(screen, f"Foods: {player.foods_eaten}", font_small, (0, 255, 120),
              boost_x + 30, boost_y + 30)

    # 🆕 Indicador de estado
    if player.boosting:
        pygame.draw.circle(screen, (255, 200, 0), (panel_x + 7, panel_y + 7), 5)
    else:
        pygame.draw.circle(screen, (100, 100, 100), (panel_x + 7, panel_y + 7), 5)


def draw_minimap(screen, snakes, food):
    """
    Minimapa mejorado con:
    - Borde decorativo
    - Mostrar solo serpientes vivas
    - Escala correcta
    - Cuadro de visión de cámara
    """
    size = MINIMAP_SIZE
    pos_x, pos_y = MINIMAP_POSITION

    # Superficie del minimapa
    surf = pygame.Surface((size, size))
    surf.fill(GRID_COLOR)

    scale = size / WORLD_SIZE

    # Dibujar comida (pequeña)
    for f in food:
        fx = int(f[0] * scale)
        fy = int(f[1] * scale)
        if 0 <= fx < size and 0 <= fy < size:
            pygame.draw.circle(surf, FOOD_COLOR, (fx, fy), 1)

    # Dibujar serpientes (solo vivas)
    for s in snakes:
        if not s.alive:  # No mostrar muertas
            continue
            
        x = int(s.head.x * scale)
        y = int(s.head.y * scale)
        
        if 0 <= x < size and 0 <= y < size:
            # Tamaño proporcional a la longitud
            radius = max(2, int(math.sqrt(len(s.segments)) / 2))
            
            # El jugador es más brillante
            if s.is_human:
                color = (255, 200, 100)
            else:
                color = s.body_color
            pygame.draw.circle(surf, color, (x, y), radius)
            
            # Punto blanco en el centro (cabeza)
            pygame.draw.circle(surf, (255, 255, 255), (x, y), 1)

    # Dibujar borde del minimapa
    pygame.draw.rect(screen, (150, 150, 200), 
                     (pos_x - 2, pos_y - 2, size + 4, size + 4), 2)

    # Mostrar minimapa
    screen.blit(surf, (pos_x, pos_y))

    # Título del minimapa
    font_small = get_font(14)
    draw_text(screen, "Map", font_small, (150, 150, 200),
              pos_x + size // 2, pos_y - 20, center=True)


def draw_hud_split(surface, player, offset_x, panel_w, label_color):
    """HUD compacto para pantalla dividida. Se dibuja dentro de la mitad del jugador."""
    font_med  = get_font(18, bold=True)
    font_sm   = get_font(14)

    px, py = offset_x + 10, 10
    pw, ph = 200, 110

    bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
    bg.fill((10, 10, 25, 190))
    surface.blit(bg, (px, py))
    pygame.draw.rect(surface, label_color, (px, py, pw, ph), 1)

    # Franja de color del jugador arriba
    pygame.draw.rect(surface, label_color, (px, py, pw, 4))

    draw_text(surface, player.name, font_med, label_color, px + 8, py + 8)
    draw_text(surface, f"Score: {player.score}", font_sm, (200, 255, 200), px + 8, py + 32)
    draw_text(surface, f"Length: {player.length}", font_sm, (255, 180, 100), px + 8, py + 50)
    draw_text(surface, f"Kills: {player.kills}", font_sm, (180, 255, 180), px + 8, py + 68)

    # Barra de boost
    bx, by = px + 8, py + 88
    bw, bh = pw - 16, 12
    pygame.draw.rect(surface, (50, 50, 50), (bx, by, bw, bh))
    fill = int(bw * (player.boost_energy / player.max_boost_energy))
    if getattr(player, "boost_depleted", False):
        bcol = (160, 50, 50)
    elif player.boost_energy < player.max_boost_energy * 0.5:
        bcol = (255, 80, 80)
    else:
        bcol = (255, 200, 0)
    pygame.draw.rect(surface, bcol, (bx, by, fill, bh))
    pygame.draw.line(surface, (255,255,255), (bx + bw//2, by), (bx + bw//2, by + bh), 1)
    draw_text(surface, "BOOST", get_font(10), (180,180,180), bx, by - 12)


def draw_splitscreen_divider(screen):
    """Línea divisoria central entre las dos mitades."""
    mx = WIDTH // 2
    pygame.draw.rect(screen, (30, 30, 50), (mx - 2, 0, 4, HEIGHT))
    pygame.draw.line(screen, (80, 80, 120), (mx, 0), (mx, HEIGHT), 1)


def draw_ranking(screen, snakes, player=None, max_show=10):
    """Ranking estilo slither.io en la esquina superior derecha."""
    alive = [s for s in snakes if s.alive]
    if not alive:
        return

    sorted_snakes = sorted(alive, key=lambda s: s.length, reverse=True)
    player_rank = next((i+1 for i, s in enumerate(sorted_snakes) if s is player), None)

    # Mostrar top N, pero siempre incluir al jugador si está fuera del top
    top = sorted_snakes[:max_show]
    show_player_sep = player is not None and player_rank is not None and player_rank > max_show

    ROW_H = 28
    PANEL_W = 220
    rows = len(top) + (2 if show_player_sep else 0)  # +2 por separador y fila del jugador
    PANEL_H = 36 + rows * ROW_H + 8

    rank_x = WIDTH - PANEL_W - 12
    rank_y = 12

    # Fondo semi-transparente
    bg = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    bg.fill((10, 10, 20, 190))
    screen.blit(bg, (rank_x, rank_y))
    pygame.draw.rect(screen, (60, 60, 100), (rank_x, rank_y, PANEL_W, PANEL_H), 1)

    font_title = get_font(15, bold=True)
    font_row   = get_font(14, bold=False)
    font_bold  = get_font(14, bold=True)

    # Título
    draw_text(screen, "RANKING", font_title, (200, 200, 255),
              rank_x + PANEL_W // 2, rank_y + 8, center=True)

    # Línea separadora bajo el título
    pygame.draw.line(screen, (60, 60, 100),
                     (rank_x + 8, rank_y + 28), (rank_x + PANEL_W - 8, rank_y + 28))

    for i, snake in enumerate(top):
        row_y = rank_y + 36 + i * ROW_H
        is_player = snake is player

        # Resaltar fila del jugador
        if is_player:
            hi = pygame.Surface((PANEL_W - 2, ROW_H), pygame.SRCALPHA)
            hi.fill((255, 200, 0, 40))
            screen.blit(hi, (rank_x + 1, row_y))

        # Número de posición
        num_color = (255, 200, 0) if i == 0 else (200, 200, 200) if i < 3 else (130, 130, 150)
        draw_text(screen, f"{i+1}", font_bold if i < 3 else font_row, num_color,
                  rank_x + 10, row_y + 6)

        # Punto de color de la serpiente
        pygame.draw.circle(screen, snake.body_color[:3],
                           (rank_x + 32, row_y + ROW_H // 2), 5)

        # Nombre (truncado)
        name = snake.name[:13]
        name_color = (255, 230, 80) if is_player else (220, 220, 220)
        draw_text(screen, name, font_bold if is_player else font_row, name_color,
                  rank_x + 42, row_y + 6)

        # Longitud (alineada a la derecha)
        len_text = str(snake.length)
        draw_text(screen, len_text, font_row, (100, 220, 255),
                  rank_x + PANEL_W - 10 - get_font(14).size(len_text)[0], row_y + 6)

    # Si el jugador está fuera del top, mostrar separador + su posición
    if show_player_sep and player is not None:
        sep_y = rank_y + 36 + max_show * ROW_H
        draw_text(screen, "· · ·", font_row, (100, 100, 130),
                  rank_x + PANEL_W // 2, sep_y, center=True)

        row_y = sep_y + ROW_H - 4
        hi = pygame.Surface((PANEL_W - 2, ROW_H), pygame.SRCALPHA)
        hi.fill((255, 200, 0, 40))
        screen.blit(hi, (rank_x + 1, row_y))

        draw_text(screen, f"{player_rank}", font_bold, (255, 200, 0), rank_x + 10, row_y + 6)
        pygame.draw.circle(screen, player.body_color[:3], (rank_x + 32, row_y + ROW_H // 2), 5)
        draw_text(screen, player.name[:13], font_bold, (255, 230, 80), rank_x + 42, row_y + 6)
        len_text = str(player.length)
        draw_text(screen, len_text, font_row, (100, 220, 255),
                  rank_x + PANEL_W - 10 - get_font(14).size(len_text)[0], row_y + 6)


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