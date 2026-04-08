import pygame, math, random, time
from settings import *
import particles  # 🆕 Para efectos visuales

def distance(a, b):
    """Calcula distancia euclidiana entre dos puntos"""
    return math.hypot(a[0]-b[0], a[1]-b[1])

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
        self.alive = True  # 🆕 Control de estado
        self.boost_cooldown = 0  # 🆕 Evitar boost infinito

        # Stats
        self.spawn_time = time.time()
        self.kills = 0
        self.max_mass = self.mass
        self.total_eaten = 0  # 🆕 Total de comida comida

        self.personality = random.choice(["aggressive", "scared", "collector"])
        
        # 🆕 Parámetros de comportamiento IA
        self.target = None
        self.wander_timer = 0

    def update(self, food, snakes, camera):
        """Actualiza la lógica de la serpiente"""
        if not self.alive:  # 🆕 No actualizar muertas
            return

        # Decidir dirección (IA o jugador)
        if self.is_ai:
            self.ai(food, snakes)
        else:
            self.mouse_control(camera)

        # 🎯 MOVIMIENTO
        speed = SNAKE_SPEED * (20 / (self.mass + 1))
        
        # Aplicar boost
        if self.boosting and self.mass > 12:
            speed *= BOOST_MULT
            self.mass -= BOOST_COST

        # Calcular nueva posición
        x, y = self.body[0]
        nx = (x + math.cos(self.angle) * speed) % WORLD_SIZE
        ny = (y + math.sin(self.angle) * speed) % WORLD_SIZE

        self.body.insert(0, (nx, ny))

        # Mantener longitud según masa
        self.length = int(self.mass)
        if len(self.body) > self.length:
            self.body.pop()

        # Actualizar máximos
        if self.mass > self.max_mass:
            self.max_mass = self.mass

        # 🆕 Protección masa mínima (no puede desaparecer)
        if self.mass < 10:
            self.mass = 10

    def mouse_control(self, camera):
        """Control del jugador con el mouse"""
        mx, my = pygame.mouse.get_pos()

        # Convertir coordenadas pantalla → mundo
        mx = mx / camera.zoom + camera.x
        my = my / camera.zoom + camera.y

        dx = mx - self.body[0][0]
        dy = my - self.body[0][1]

        # Solo actualizar ángulo si hay movimiento significativo
        if distance((0, 0), (dx, dy)) > 5:
            self.angle = math.atan2(dy, dx)

        self.boosting = pygame.mouse.get_pressed()[0]

    def ai(self, food, snakes):
        """IA mejorada con comportamientos variados"""
        head = self.body[0]

        if not food:  # 🆕 Validación
            return

        # 🆕 Evitar serpientes más grandes
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

            # Si hay amenaza cercana, huir
            if threat_distance < 250:
                if self.personality != "aggressive":
                    dx = head[0] - closest_threat.body[0][0]
                    dy = head[1] - closest_threat.body[0][1]
                    self.angle = math.atan2(dy, dx)
                    self.boosting = True
                    return
                # Aggressive intenta luchar
                elif self.mass > closest_threat.mass * 0.9:
                    self.boosting = True

        # 🎯 Comportamientos según personalidad
        if self.personality == "aggressive":
            # Atacar jugadores (no IA)
            targets = [s for s in snakes if not s.is_ai and s.alive and s != self]
            if targets:
                target = min(targets, key=lambda s: distance(head, s.body[0]))
                
                # Solo atacar si somos más grandes
                if self.mass > target.mass:
                    self.target = target.body[0]
                    self.boosting = True
                else:
                    # Ir por comida en su lugar
                    self.target = min(food, key=lambda f: distance(head, f))
            else:
                self.target = min(food, key=lambda f: distance(head, f))

        elif self.personality == "scared":
            # Recolectar comida pero ser cauteloso
            self.target = min(food, key=lambda f: distance(head, f))

            # Detectar amenazas cercanas
            for s in snakes:
                if s != self and s.alive:
                    threat_dist = distance(head, s.body[0])
                    if threat_dist < 150:
                        # Huir
                        dx = head[0] - s.body[0][0]
                        dy = head[1] - s.body[0][1]
                        self.angle = math.atan2(dy, dx)
                        self.boosting = True
                        return

        else:  # "collector"
            # Enfocarse puro en comida
            self.target = min(food, key=lambda f: distance(head, f))
            self.boosting = False

        # 🎯 Apuntar hacia el objetivo
        if self.target:
            dx = self.target[0] - head[0]
            dy = self.target[1] - head[1]
            target_angle = math.atan2(dy, dx)
            
            # 🆕 Suavizar rotación (no giros abruptos)
            angle_diff = target_angle - self.angle
            
            # Normalizar diferencia de ángulo (-π a π)
            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            elif angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # Aplicar velocidad angular máxima
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
                
                # 🆕 Efecto visual al comer
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

            # Si nuestra cabeza toca el cuerpo de otro, morimos
            if self._head_hits_body(head, other):
                self.die(other)
                return True

            # Si las cabezas chocan, gana el más grande
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
        
        # 🆕 Le da puntos al asesino
        if killer:
            killer.kills += 1
            killer.score += 10
        
        # 🆕 Explosión de partículas
        particles.spawn(
            self.body[0][0],
            self.body[0][1],
            self.color,
            count=25
        )

    def draw(self, screen, camera):
        """Dibuja la serpiente y su información"""
        if not self.alive:  # 🆕 No dibujar muertas
            return

        radius = max(4, int(self.mass / 10))
        head_x, head_y = camera.apply(self.body[0])

        # 🎨 Efecto degradado del cuerpo
        for i, seg in enumerate(self.body):
            x, y = camera.apply(seg)
            
            # 🆕 Cuerpo se vuelve más oscuro hacia la cola
            fade = 1 - (i / len(self.body)) * 0.5
            faded_color = tuple(int(c * fade) for c in self.color)
            
            pygame.draw.circle(screen, faded_color, (int(x), int(y)), int(radius))

        # 🆕 Brillo en la cabeza
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (int(head_x), int(head_y)),
            int(radius // 2)
        )

        # 🆕 Dibuja ojos
        eye_offset = 8
        eye_x = head_x + math.cos(self.angle) * eye_offset
        eye_y = head_y + math.sin(self.angle) * eye_offset
        pygame.draw.circle(screen, (255, 255, 0), (int(eye_x), int(eye_y)), 2)

        # Información del jugador
        font_small = pygame.font.SysFont(None, 18)
        name_text = font_small.render(self.name, True, (255, 255, 255))
        screen.blit(name_text, (head_x - 20, head_y - 25))

        # 🆕 Mostrar masa solo si está seleccionado o es el jugador
        if not self.is_ai:
            mass_text = font_small.render(f"{int(self.mass)}", True, self.color)
            screen.blit(mass_text, (head_x - 10, head_y - 5))

    def get_lifetime(self):
        """🆕 Retorna tiempo vivo en segundos"""
        return time.time() - self.spawn_time

    def __repr__(self):
        """🆕 Para debugging"""
        return (
            f"Snake({self.name}, mass={self.mass:.1f}, "
            f"score={self.score}, alive={self.alive})"
        )