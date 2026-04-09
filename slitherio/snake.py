import pygame
import math
import random
import time
from settings import *
import particles  # Efectos visuales


def distance(a, b):
    """Calcula distancia euclidiana entre dos puntos"""
    return math.hypot(a[0] - b[0], a[1] - b[1])


class Snake:
    def __init__(self, x, y, color, name="Jugador", is_ai=False):
        """Inicializa una serpiente"""
        self.body = [(x, y)]
        self.mass = INITIAL_MASS
        self.length = int(self.mass)
        self.angle = random.random() * 6.28
        self.color = color
        self.name = name
        self.is_ai = is_ai
        self.score = 0
        self.boosting = False
        self.alive = True
        self.boost_cooldown = 0

        self.spawn_time = time.time()
        self.kills = 0
        self.max_mass = self.mass
        self.total_eaten = 0

        self.personality = random.choice(["aggressive", "scared", "collector"])

        self.target = None
        self.wander_timer = 0

    def update(self, food, snakes, camera):
        """Actualiza la lógica de la serpiente"""
        if not self.alive:
            return

        if self.is_ai:
            self.ai(food, snakes)
        else:
            self.mouse_control(camera)

        speed = SNAKE_SPEED * (20 / (self.mass + 1))

        if self.boosting and self.mass > 12:
            speed *= BOOST_MULT
            self.mass -= BOOST_COST

        # Movimiento suave para que se vea más orgánico
        x, y = self.body[0]
        nx = (x + math.cos(self.angle) * speed) % WORLD_SIZE
        ny = (y + math.sin(self.angle) * speed) % WORLD_SIZE

        smooth = 0.65
        nx = x + (nx - x) * smooth
        ny = y + (ny - y) * smooth

        self.body.insert(0, (nx, ny))

        self.length = int(self.mass)
        if len(self.body) > self.length:
            self.body.pop()

        if self.mass > self.max_mass:
            self.max_mass = self.mass

        if self.mass < 10:
            self.mass = 10

    def mouse_control(self, camera):
        """Control del jugador con el mouse"""
        mx, my = pygame.mouse.get_pos()

        mx = mx / camera.zoom + camera.x
        my = my / camera.zoom + camera.y

        dx = mx - self.body[0][0]
        dy = my - self.body[0][1]

        if distance((0, 0), (dx, dy)) > 5:
            self.angle = math.atan2(dy, dx)

        self.boosting = pygame.mouse.get_pressed()[0]

    def ai(self, food, snakes):
        """IA mejorada con comportamientos variados"""
        head = self.body[0]
        self.boosting = False
        self.target = None

        if not food:
            return

        bigger_snakes = [
            s for s in snakes
            if s.mass > self.mass * 1.2 and s != self and s.alive
        ]

        if bigger_snakes:
            closest_threat = min(
                bigger_snakes,
                key=lambda s: distance(head, s.body[0])
            )
            threat_distance = distance(head, closest_threat.body[0])

            if threat_distance < 250:
                if self.personality != "aggressive":
                    dx = head[0] - closest_threat.body[0][0]
                    dy = head[1] - closest_threat.body[0][1]
                    self.angle = math.atan2(dy, dx)
                    self.boosting = True
                    return
                elif self.mass > closest_threat.mass * 0.9:
                    self.boosting = True

        if self.personality == "aggressive":
            targets = [s for s in snakes if not s.is_ai and s.alive and s != self]
            if targets:
                target = min(targets, key=lambda s: distance(head, s.body[0]))

                if self.mass > target.mass:
                    self.target = target.body[0]
                    self.boosting = True
                else:
                    self.target = min(food, key=lambda f: distance(head, f))
            else:
                self.target = min(food, key=lambda f: distance(head, f))

        elif self.personality == "scared":
            self.target = min(food, key=lambda f: distance(head, f))

            for s in snakes:
                if s != self and s.alive:
                    threat_dist = distance(head, s.body[0])
                    if threat_dist < 150:
                        dx = head[0] - s.body[0][0]
                        dy = head[1] - s.body[0][1]
                        self.angle = math.atan2(dy, dx)
                        self.boosting = True
                        return

        else:  # collector
            self.target = min(food, key=lambda f: distance(head, f))
            self.boosting = False

        if self.target:
            dx = self.target[0] - head[0]
            dy = self.target[1] - head[1]
            target_angle = math.atan2(dy, dx)

            angle_diff = target_angle - self.angle

            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            elif angle_diff < -math.pi:
                angle_diff += 2 * math.pi

            max_turn = TURN_SPEED
            angle_diff = max(-max_turn, min(max_turn, angle_diff))

            self.angle += angle_diff

    def eat(self, food_list):
        """Detecta colisión con comida"""
        for f in food_list[:]:
            if distance(self.body[0], f) < 10:
                food_list.remove(f)
                self.mass += 1.5
                self.score += 1
                self.total_eaten += 1

                particles.spawn(
                    self.body[0][0],
                    self.body[0][1],
                    self.color,
                    count=8
                )
                return True
        return False

    def _head_hits_body(self, head, other):
        for segment in other.body[1:]:
            if distance(head, segment) < COLLISION_DISTANCE:
                return True
        return False

    def _head_hits_head(self, head, other):
        return distance(head, other.body[0]) < COLLISION_DISTANCE

    def check_collision(self, snakes):
        """Detecta colisiones con otras serpientes"""
        if not self.alive:
            return False

        head = self.body[0]

        for other in snakes:
            if other == self or not other.alive:
                continue

            if self._head_hits_body(head, other):
                self.die(other)
                return True

            if self._head_hits_head(head, other):
                if self.mass > other.mass * MASS_ADVANTAGE:
                    other.die(self)
                    return True
                elif other.mass > self.mass * MASS_ADVANTAGE:
                    self.die(other)
                    return True

        return False

    def die(self, killer=None):
        """Marca la serpiente como muerta"""
        self.alive = False

        if killer:
            killer.kills += 1
            killer.score += 10

        particles.spawn(
            self.body[0][0],
            self.body[0][1],
            self.color,
            count=25
        )

    def draw(self, screen, camera):
        """Dibuja la serpiente estilo Slither.io: cuerpo fluido continuo"""
        if not self.alive or len(self.body) < 2:
            return

        # Calcular radio base según la masa
        head_radius = max(5, int(math.sqrt(self.mass) * 1.2))
        
        # Convertir body a coordenadas de pantalla
        screen_points = [camera.apply(p) for p in self.body]

        # 🎨 DIBUJAR CUERPO SUAVE Y FLUIDO
        if len(screen_points) > 2:
            # Dibujar como polilínea suave con ancho variable
            for i in range(len(screen_points) - 1):
                x1, y1 = screen_points[i]
                x2, y2 = screen_points[i + 1]
                
                # El radio disminuye hacia la cola
                progress = i / len(screen_points)
                current_radius = head_radius * (1 - progress * 0.6)
                line_width = max(2, int(current_radius * 2))
                
                # Color se desvanece hacia la cola
                fade = 1 - progress * 0.3
                faded_color = tuple(int(c * fade) for c in self.color)
                
                # Dibujar segmento
                pygame.draw.line(
                    screen,
                    faded_color,
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    line_width
                )

            # 🔵 SUAVIZAR CON CÍRCULOS EN CADA SEGMENTO (transición suave)
            for i in range(len(screen_points)):
                x, y = screen_points[i]
                progress = i / len(screen_points)
                current_radius = head_radius * (1 - progress * 0.6)
                fade = 1 - progress * 0.3
                faded_color = tuple(int(c * fade) for c in self.color)
                
                pygame.draw.circle(
                    screen,
                    faded_color,
                    (int(x), int(y)),
                    max(1, int(current_radius))
                )

        # 🔴 CABEZA MÁS DEFINIDA
        head_x, head_y = screen_points[0]
        
        # Círculo principal de la cabeza
        pygame.draw.circle(
            screen,
            self.color,
            (int(head_x), int(head_y)),
            head_radius
        )
        
        # Brillo / reflejo en la cabeza
        pygame.draw.circle(
            screen,
            tuple(min(255, c + 60) for c in self.color),
            (int(head_x - head_radius * 0.3), int(head_y - head_radius * 0.3)),
            max(1, head_radius // 3)
        )

        # 👁️ OJOS REALISTAS
        eye_distance = head_radius * 0.6
        eye_size = max(3, head_radius // 2.5)
        perp_angle = self.angle + math.pi / 2

        # Ojo izquierdo
        ex1 = head_x + math.cos(self.angle) * eye_distance + math.cos(perp_angle) * eye_size * 0.8
        ey1 = head_y + math.sin(self.angle) * eye_distance + math.sin(perp_angle) * eye_size * 0.8

        # Ojo derecho
        ex2 = head_x + math.cos(self.angle) * eye_distance - math.cos(perp_angle) * eye_size * 0.8
        ey2 = head_y + math.sin(self.angle) * eye_distance - math.sin(perp_angle) * eye_size * 0.8

        # Ojos blancos
        pygame.draw.circle(screen, (255, 255, 255), (int(ex1), int(ey1)), eye_size)
        pygame.draw.circle(screen, (255, 255, 255), (int(ex2), int(ey2)), eye_size)

        # Pupilas negras
        pupil_size = max(1, eye_size // 2)
        pygame.draw.circle(screen, (0, 0, 0), (int(ex1), int(ey1)), pupil_size)
        pygame.draw.circle(screen, (0, 0, 0), (int(ex2), int(ey2)), pupil_size)

        # ✨ BRILLO EN LAS PUPILAS
        pygame.draw.circle(
            screen,
            (200, 200, 200),
            (int(ex1 - pupil_size * 0.5), int(ey1 - pupil_size * 0.5)),
            max(1, pupil_size // 2)
        )
        pygame.draw.circle(
            screen,
            (200, 200, 200),
            (int(ex2 - pupil_size * 0.5), int(ey2 - pupil_size * 0.5)),
            max(1, pupil_size // 2)
        )

        # 📛 NOMBRE
        font_small = pygame.font.SysFont("arial", 16, bold=True)
        name_text = font_small.render(self.name, True, (255, 255, 255))
        screen.blit(name_text, (head_x - name_text.get_width() // 2, head_y - head_radius - 25))

        # 📊 MASA (solo para el jugador)
        if not self.is_ai:
            mass_text = pygame.font.SysFont("arial", 14, bold=False).render(
                f"{int(self.mass)}", True, self.color
            )
            screen.blit(mass_text, (head_x - mass_text.get_width() // 2, head_y - head_radius - 8))

    def get_lifetime(self):
        """Retorna tiempo vivo en segundos"""
        return time.time() - self.spawn_time

    def __repr__(self):
        """Para debugging"""
        return (
            f"Snake({self.name}, mass={self.mass:.1f}, "
            f"score={self.score}, alive={self.alive})"
        )