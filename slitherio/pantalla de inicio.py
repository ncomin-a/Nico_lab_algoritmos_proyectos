import pygame
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

folder = Path(__file__).parent


# ---- CONFIG -----
WIDTH, HEIGHT = 1200, 800
FPS = 60
BG_COLOR = (15, 18, 32)
BUTTON_COLOR = (65, 187, 96)
BUTTON_HOVER = (85, 230, 130)
INPUT_BG = (106, 90, 158)
INPUT_BORDER = (144, 131, 191)
WHITE = (255, 255, 255)
FONDO_DE_PANTALLA = folder / "imagenes" / "pantalla de inicio Slither sin botones.png"

# ----- GRADIENTE DE TEXTO CORRECTO -------
def render_gradient_text(text, font, color1, color2):
    text_surface = font.render(text, True, (255, 255, 255))
    w, h = text_surface.get_size()
    gradient = pygame.Surface((w, h)).convert_alpha()
    for y in range(h):
        alpha = y / h
        color = (
            int(color1[0] * (1 - alpha) + color2[0] * alpha),
            int(color1[1] * (1 - alpha) + color2[1] * alpha),
            int(color1[2] * (1 - alpha) + color2[2] * alpha)
        )
        pygame.draw.line(gradient, color, (0, y), (w, y))
    text_surface.blit(gradient, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return text_surface

def show_menu():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Fuentes
    try:
        title_font = pygame.font.SysFont("arialrounded", 110, bold=True)
    except:
        title_font = pygame.font.SysFont("arial", 110, bold=True)
    button_font = pygame.font.SysFont('arial', 38, bold=True)
    input_font = pygame.font.SysFont('arial', 36, bold=True)

    # Imagenes de fondo con Pillow
    try:
        if Image:
            fondo_img = Image.open(FONDO_DE_PANTALLA).convert("RGBA")
            fondo_img = fondo_img.resize((WIDTH, HEIGHT), Image.LANCZOS)
            fondo_pantalla = pygame.image.fromstring(
                fondo_img.tobytes(), fondo_img.size, fondo_img.mode
            )
        else:
            fondo_pantalla = pygame.image.load(FONDO_DE_PANTALLA).convert_alpha()
            fondo_pantalla = pygame.transform.smoothscale(fondo_pantalla, (WIDTH, HEIGHT))
        images_available = True
    except Exception as e:
        print("No se encontraron imágenes de fondo:", e)
        images_available = False

    # Caja de nombre
    input_rect = pygame.Rect(WIDTH//2-210, 340, 420, 60)
    user_text = ""
    input_active = False
    cursor_visible = True
    cursor_timer = 0

    # Botones
    button_online = pygame.Rect(WIDTH//2-220, 440, 220, 68)
    button_ai = pygame.Rect(WIDTH//2+10, 440, 220, 68)

    # Estado para mostrar mensaje
    show_coming_soon = False
    coming_soon_timer = 0

    # MAIN LOOP
    running = True
    while running:
        clock.tick(FPS)

        # Parpadeo del cursor de texto
        cursor_timer += 1
        if cursor_timer >= 30:
            cursor_visible = not cursor_visible
            cursor_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False
                if button_ai.collidepoint(event.pos):
                    if user_text.strip():
                        pygame.quit()
                        return user_text
                if button_online.collidepoint(event.pos):
                    if user_text.strip():
                        show_coming_soon = True
                        coming_soon_timer = 120  # ~2 segundos
                        print("Próximamente disponible")

            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif len(user_text) < 15 and event.unicode.isprintable():
                    user_text += event.unicode

        # Actualizar display de "próximamente"
        if show_coming_soon:
            coming_soon_timer -= 1
            if coming_soon_timer <= 0:
                show_coming_soon = False

        # ----- DIBUJAR -----
        screen.fill(BG_COLOR)
        if images_available:
            screen.blit(fondo_pantalla, (0,0))


        # Caja nombre
        pygame.draw.rect(screen, INPUT_BG, input_rect, border_radius=32)
        pygame.draw.rect(screen, INPUT_BORDER, input_rect, width=4, border_radius=32)
        # Texto placeholder
        color_placeholder = WHITE if user_text else (160,160,170)
        text_surface = input_font.render(user_text or "Ingresa tu nombre...", True, color_placeholder)
        screen.blit(text_surface, (input_rect.x+17, input_rect.y+15))
        # Cursor
        if input_active and cursor_visible and len(user_text)<15:
            cursor_x = input_rect.x + 17 + text_surface.get_width()
            pygame.draw.line(screen, WHITE, (cursor_x, input_rect.y + 12), (cursor_x, input_rect.y + 49), 2)

        # Botones
        mouse = pygame.mouse.get_pos()
        # Play Online
        hover1 = button_online.collidepoint(mouse)
        pygame.draw.rect(screen, BUTTON_HOVER if hover1 else BUTTON_COLOR, button_online, border_radius=30)
        btn1_text = button_font.render("Play Online", True, WHITE)
        screen.blit(btn1_text, (button_online.x + (button_online.width-btn1_text.get_width())//2, button_online.y + 15))
        # Play vs AI
        hover2 = button_ai.collidepoint(mouse)
        pygame.draw.rect(screen, BUTTON_HOVER if hover2 else BUTTON_COLOR, button_ai, border_radius=30)
        btn2_text = button_font.render("Play vs AI", True, WHITE)
        screen.blit(btn2_text, (button_ai.x + (button_ai.width-btn2_text.get_width())//2, button_ai.y + 15))

        # Mensaje "próximamente"
        if show_coming_soon:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            coming_soon_font = pygame.font.SysFont('arial', 72, bold=True)
            coming_soon_text = coming_soon_font.render("PRÓXIMAMENTE", True, (255, 200, 0))
            coming_soon_rect = coming_soon_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(coming_soon_text, coming_soon_rect)

        pygame.display.flip()

# Para pruebas locales
if __name__ == "__main__":
    nombre = show_menu()
    if nombre:
        print("Iniciando juego con:", nombre)
    else:
        print("Juego cerrado")