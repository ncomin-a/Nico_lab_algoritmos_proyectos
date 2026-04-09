import pygame
import sys

pygame.init()

# Configuración de la ventana
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
LIGHT_BLUE = (100, 200, 255)
DARK_BLUE = (30, 60, 150)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pantalla de Inicio Avanzada")

clock = pygame.time.Clock()

# ---------- Carga recursos ----------
# Fondo (usa una imagen tuya si quieres)
try:
    background = pygame.image.load("background.jpg").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except:
    # Si no tienes imagen, usa degradado sencillo
    background = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        pygame.draw.line(background, (30, 30 + y//4, 50 + y//3), (0, y), (WIDTH, y))

# Fuente
title_font = pygame.font.SysFont("Arial", 80)
button_font = pygame.font.SysFont("Arial", 40)

# Botón
button_rect = pygame.Rect(0, 0, 260, 65)
button_rect.center = (WIDTH//2, 400)

def draw_button(surface, rect, text, hovered):
    color = LIGHT_BLUE if hovered else DARK_BLUE
    pygame.draw.rect(surface, color, rect, border_radius=12)
    pygame.draw.rect(surface, WHITE, rect, width=3, border_radius=12)
    txt_surface = button_font.render(text, True, WHITE)
    txt_rect = txt_surface.get_rect(center=rect.center)
    surface.blit(txt_surface, txt_rect)

# Animación: círculo saltarín
circle_x = 100
circle_y = HEIGHT//2
circle_radius = 35
circle_dir = 1
circle_speed = 4

# Música de fondo (opcional)
# pygame.mixer.music.load('intro.ogg')
# pygame.mixer.music.play(-1)

def draw_start_screen():
    # Fondo
    screen.blit(background, (0, 0))
    # Título
    title_surface = title_font.render("Mi Juego", True, WHITE)
    screen.blit(title_surface, ((WIDTH - title_surface.get_width()) // 2, 110))

    # Texto instrucción (animado)
    blink = (pygame.time.get_ticks() // 500) % 2
    if blink:
        instr_surface = button_font.render("¡Haz click en JUGAR!", True, WHITE)
        screen.blit(instr_surface, ((WIDTH - instr_surface.get_width()) // 2, 500))

    # Botón (hover visual)
    mouse_pos = pygame.mouse.get_pos()
    hovered = button_rect.collidepoint(mouse_pos)
    draw_button(screen, button_rect, "JUGAR", hovered)

    # Animación círculo
    pygame.draw.circle(screen, (180, 255, 120), (circle_x, circle_y), circle_radius)
    # (puedes agregar más animaciones, personajes, etc.)

# Bucle de pantalla de inicio
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                if button_rect.collidepoint(event.pos):
                    print("¡Comienza el juego!") # aquí cambia a tu función principal
                    running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                print("¡Comienza el juego!") # aquí cambia a tu función principal
                running = False

    # Animación simple: el círculo se mueve horizontalmente y rebota
    circle_x += circle_speed * circle_dir
    if circle_x > WIDTH - circle_radius or circle_x < circle_radius:
        circle_dir *= -1  # Cambia de dirección

    draw_start_screen()
    pygame.display.flip()
    clock.tick(FPS)

# Aquí pondrías tu función principal de juego, o cambiarías de escena
pygame.quit()