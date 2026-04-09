import pygame
import sys
import os

# Configuración
WIDTH, HEIGHT = 1200, 800
FPS = 60
BG_COLOR = (15, 18, 32)
BUTTON_COLOR = (65, 187, 96)
BUTTON_HOVER = (85, 230, 130)
WHITE = (255, 255, 255)

# Cargar imágenes de gusanos (global)
images_available = False
gusano_izq = None
gusano_der = None

def load_images():
    """Carga las imágenes de decoración"""
    global images_available, gusano_izq, gusano_der
    try:
        gusano_izq = pygame.image.load('slitherio/imagenes/gusano_izq.png')
        gusano_der = pygame.image.load('slitherio/imagenes/gusano_der.png')
        gusano_izq = pygame.transform.scale(gusano_izq, (175, 110))
        gusano_der = pygame.transform.scale(gusano_der, (175, 110))
        images_available = True
    except Exception as e:
        print(f"Advertencia: No se pudieron cargar las imágenes: {e}")
        images_available = False

def gradiente_text(text, font, color1, color2):
    """Crea un texto con gradiente de colores"""
    base = font.render(text, True, color1)
    width, height = base.get_size()
    
    result_text = font.render(text, True, color1)
    result = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y in range(height):
        alpha = y / height
        for x in range(width):
            if 0 <= x < width:
                ca = tuple(int(color1[i]*(1-alpha) + color2[i]*alpha) for i in range(3))
                if x < width and y < height:
                    pixelcolor = base.get_at((x, y))
                    result.set_at((x, y), (*ca, 255))
    
    return result

def show_menu():
    """
    Muestra el menú principal
    Retorna: nombre del jugador si selecciona "Play vs AI", None si cierra el programa
    """
    pygame.init()
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gusano.io - Inicio")
    clock = pygame.time.Clock()
    
    # Cargar imágenes
    load_images()
    
    # Fuentes
    title_font = pygame.font.SysFont('arialrounded', 110, bold=True)
    button_font = pygame.font.SysFont('arial', 38, bold=True)
    input_font = pygame.font.SysFont('arial', 36, bold=True)
    small_font = pygame.font.SysFont('arial', 28)
    
    # Input box config
    input_rect = pygame.Rect(WIDTH//2-210, 340, 420, 60)
    user_text = ""
    input_active = False
    cursor_visible = True
    cursor_timer = 0
    
    # Botones
    button_ai = pygame.Rect(WIDTH//2-220, 440, 220, 68)
    button_online = pygame.Rect(WIDTH//2+10, 440, 220, 68)
    
    # Estado para mostrar mensaje
    show_coming_soon = False
    coming_soon_timer = 0
    
    running = True
    
    while running:
        clock.tick(FPS)
        
        # Control de parpadeo del cursor
        cursor_timer += 1
        if cursor_timer >= 30:
            cursor_visible = not cursor_visible
            cursor_timer = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Activar input
                if input_rect.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False
                
                # Botón Play vs AI
                if button_ai.collidepoint(event.pos):
                    if user_text.strip():
                        pygame.quit()
                        return user_text  # Retornar el nombre para iniciar el juego
                    else:
                        print("Por favor ingresa un nombre")
                
                # Botón Play Online
                if button_online.collidepoint(event.pos):
                    if user_text.strip():
                        show_coming_soon = True
                        coming_soon_timer = 120  # 2 segundos a 60 FPS
                        print("Próximamente disponible")
            
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    if user_text.strip():
                        pygame.quit()
                        return user_text
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif len(user_text) < 15 and event.unicode.isprintable():
                    user_text += event.unicode
        
        # Actualizar contador de "coming soon"
        if show_coming_soon:
            coming_soon_timer -= 1
            if coming_soon_timer <= 0:
                show_coming_soon = False
        
        # Dibujar pantalla
        screen.fill(BG_COLOR)
        
        # Gusanos decorativos
        if images_available:
            screen.blit(gusano_izq, (120, 120))
            screen.blit(gusano_der, (WIDTH-295, 120))

        # Título con gradiente
        title = gradiente_text("Gusano.io", title_font, (126, 255, 101), (163, 102, 251))
        screen.blit(title, (WIDTH//2-title.get_width()//2, 140))

        # Caja de texto para escribir nombre
        pygame.draw.rect(screen, (106, 90, 158), input_rect, border_radius=32)
        pygame.draw.rect(screen, (144, 131, 191), input_rect, width=4, border_radius=32)
        
        text_color = WHITE if user_text else (160, 160, 170)
        text_display = user_text or "Ingresa tu nombre..."
        text_surface = input_font.render(text_display, True, text_color)
        screen.blit(text_surface, (input_rect.x+17, input_rect.y+15))
        
        # Dibujar cursor parpadeante
        if input_active and cursor_visible and len(user_text) < 15:
            cursor_x = input_rect.x + 17 + text_surface.get_width()
            pygame.draw.line(screen, WHITE, (cursor_x, input_rect.y+10), (cursor_x, input_rect.y+50), 2)

        # Botón Play vs AI
        mouse = pygame.mouse.get_pos()
        hover_ai = button_ai.collidepoint(mouse)
        pygame.draw.rect(screen, BUTTON_HOVER if hover_ai else BUTTON_COLOR, button_ai, border_radius=30)
        btn_ai_text = button_font.render("Play vs AI", True, WHITE)
        btn_ai_rect = btn_ai_text.get_rect(center=(button_ai.centerx, button_ai.centery))
        screen.blit(btn_ai_text, btn_ai_rect)

        # Botón Play Online
        hover_online = button_online.collidepoint(mouse)
        pygame.draw.rect(screen, BUTTON_HOVER if hover_online else BUTTON_COLOR, button_online, border_radius=30)
        btn_online_text = button_font.render("Play Online", True, WHITE)
        btn_online_rect = btn_online_text.get_rect(center=(button_online.centerx, button_online.centery))
        screen.blit(btn_online_text, btn_online_rect)
        
        # Mostrar "Próximamente" si se clickeó Play Online
        if show_coming_soon:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            coming_soon_text = pygame.font.SysFont('arial', 72, bold=True).render("PRÓXIMAMENTE", True, (255, 200, 0))
            coming_soon_rect = coming_soon_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(coming_soon_text, coming_soon_rect)

        pygame.display.flip()

if __name__ == "__main__":
    # Para probar el menú directamente
    pygame.init()
    nombre = show_menu()
    if nombre:
        print(f"Iniciando juego con: {nombre}")
    else:
        print("Juego cerrado")