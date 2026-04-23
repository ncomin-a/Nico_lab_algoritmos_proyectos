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

    # Estado de pantalla: "menu" o "multiplayer"
    screen_state = "menu"

    # Caja de nombre jugador 2 (para multiplayer)
    input2_rect = pygame.Rect(WIDTH//2-210, 430, 420, 60)
    user_text2 = ""
    input2_active = False

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

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if screen_state == "multiplayer":
                        screen_state = "menu"
                        user_text2 = ""
                    else:
                        pygame.quit()
                        return None

                # Texto para la caja activa
                active_text = None
                if screen_state == "menu" and input_active:
                    active_text = "p1"
                elif screen_state == "multiplayer" and input_active:
                    active_text = "p1_mp"
                elif screen_state == "multiplayer" and input2_active:
                    active_text = "p2"

                if active_text == "p1" or active_text == "p1_mp":
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    elif len(user_text) < 15 and event.unicode.isprintable():
                        user_text += event.unicode
                elif active_text == "p2":
                    if event.key == pygame.K_RETURN:
                        input2_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        user_text2 = user_text2[:-1]
                    elif len(user_text2) < 15 and event.unicode.isprintable():
                        user_text2 += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if screen_state == "menu":
                    input_active = input_rect.collidepoint(event.pos)
                    if button_ai.collidepoint(event.pos) and user_text.strip():
                        pygame.quit()
                        return user_text
                    if button_online.collidepoint(event.pos) and user_text.strip():
                        screen_state = "multiplayer"

                elif screen_state == "multiplayer":
                    input_active  = input_rect.collidepoint(event.pos)
                    input2_active = input2_rect.collidepoint(event.pos)
                    if not input_active and not input2_active:
                        input_active = False
                        input2_active = False

                    # Botón Jugar en pantalla multiplayer
                    if button_play_mp.collidepoint(event.pos):
                        n1 = user_text.strip()
                        n2 = user_text2.strip()
                        if n1 and n2:
                            pygame.quit()
                            return ("splitscreen", n1, n2)

                    # Botón Volver
                    if button_back.collidepoint(event.pos):
                        screen_state = "menu"
                        user_text2 = ""

        # ----- BOTONES extra para multiplayer -----
        button_play_mp = pygame.Rect(WIDTH//2 - 210, 530, 420, 60)
        button_back    = pygame.Rect(WIDTH//2 - 100, 610, 200, 44)

        # ----- DIBUJAR -----
        screen.fill(BG_COLOR)
        if images_available:
            screen.blit(fondo_pantalla, (0, 0))

        mouse = pygame.mouse.get_pos()

        if screen_state == "menu":
            # Caja nombre P1
            pygame.draw.rect(screen, INPUT_BG, input_rect, border_radius=32)
            pygame.draw.rect(screen, INPUT_BORDER, input_rect, width=4, border_radius=32)
            color_ph = WHITE if user_text else (160, 160, 170)
            ts = input_font.render(user_text or "Ingresa tu nombre...", True, color_ph)
            screen.blit(ts, (input_rect.x + 17, input_rect.y + 15))
            if input_active and cursor_visible and len(user_text) < 15:
                cx = input_rect.x + 17 + ts.get_width()
                pygame.draw.line(screen, WHITE, (cx, input_rect.y + 12), (cx, input_rect.y + 49), 2)

            # Botones
            hover1 = button_online.collidepoint(mouse)
            pygame.draw.rect(screen, BUTTON_HOVER if hover1 else BUTTON_COLOR, button_online, border_radius=30)
            bt1 = button_font.render("Multiplayer", True, WHITE)
            screen.blit(bt1, (button_online.x + (button_online.width - bt1.get_width())//2, button_online.y + 15))

            hover2 = button_ai.collidepoint(mouse)
            pygame.draw.rect(screen, BUTTON_HOVER if hover2 else BUTTON_COLOR, button_ai, border_radius=30)
            bt2 = button_font.render("Play vs AI", True, WHITE)
            screen.blit(bt2, (button_ai.x + (button_ai.width - bt2.get_width())//2, button_ai.y + 15))

        elif screen_state == "multiplayer":
            # Overlay semitransparente
            ov = pygame.Surface((WIDTH, HEIGHT))
            ov.set_alpha(160)
            ov.fill((0, 0, 0))
            screen.blit(ov, (0, 0))

            title_font = pygame.font.SysFont("arial", 52, bold=True)
            sub_font   = pygame.font.SysFont("arial", 22)
            title_surf = title_font.render("MULTIJUGADOR LOCAL", True, (100, 220, 255))
            screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 220))

            # Controles info
            info1 = sub_font.render("Jugador 1:  W A S D  +  LSHIFT (boost)", True, (180, 230, 180))
            info2 = sub_font.render("Jugador 2:  ↑ ↓ ← →  +  RSHIFT (boost)", True, (255, 180, 180))
            screen.blit(info1, (WIDTH//2 - info1.get_width()//2, 140))
            screen.blit(info2, (WIDTH//2 - info2.get_width()//2, 170))

            # Caja P1
            lbl1 = sub_font.render("Jugador 1", True, (100, 200, 255))
            screen.blit(lbl1, (input_rect.x, input_rect.y - 28))
            pygame.draw.rect(screen, (60, 80, 150), input_rect, border_radius=28)
            pygame.draw.rect(screen, (100, 160, 255), input_rect, width=3, border_radius=28)
            ts1 = input_font.render(user_text or "Nombre jugador 1...", True, WHITE if user_text else (140,140,160))
            screen.blit(ts1, (input_rect.x + 14, input_rect.y + 14))
            if input_active and cursor_visible:
                cx = input_rect.x + 14 + ts1.get_width()
                pygame.draw.line(screen, WHITE, (cx, input_rect.y+10), (cx, input_rect.y+48), 2)

            # Caja P2
            lbl2 = sub_font.render("Jugador 2", True, (255, 130, 130))
            screen.blit(lbl2, (input2_rect.x, input2_rect.y - 28))
            pygame.draw.rect(screen, (150, 50, 50), input2_rect, border_radius=28)
            pygame.draw.rect(screen, (255, 110, 110), input2_rect, width=3, border_radius=28)
            ts2 = input_font.render(user_text2 or "Nombre jugador 2...", True, WHITE if user_text2 else (140,140,160))
            screen.blit(ts2, (input2_rect.x + 14, input2_rect.y + 14))
            if input2_active and cursor_visible:
                cx2 = input2_rect.x + 14 + ts2.get_width()
                pygame.draw.line(screen, WHITE, (cx2, input2_rect.y+10), (cx2, input2_rect.y+48), 2)

            # Botón Jugar
            ready = user_text.strip() and user_text2.strip()
            btn_col = BUTTON_HOVER if button_play_mp.collidepoint(mouse) else BUTTON_COLOR
            if not ready:
                btn_col = (80, 80, 80)
            pygame.draw.rect(screen, btn_col, button_play_mp, border_radius=30)
            bt_play = button_font.render("¡JUGAR!" if ready else "Falta un nombre", True, WHITE)
            screen.blit(bt_play, (button_play_mp.x + (button_play_mp.width - bt_play.get_width())//2, button_play_mp.y + 15))

            # Botón Volver
            pygame.draw.rect(screen, (60, 60, 80), button_back, border_radius=20)
            pygame.draw.rect(screen, (120, 120, 160), button_back, width=2, border_radius=20)
            bt_back = sub_font.render("← Volver", True, (180, 180, 220))
            screen.blit(bt_back, (button_back.x + (button_back.width - bt_back.get_width())//2, button_back.y + 10))

        pygame.display.flip()

# Para pruebas locales
if __name__ == "__main__":
    nombre = show_menu()
    if nombre:
        print("Iniciando juego con:", nombre)
    else:
        print("Juego cerrado")