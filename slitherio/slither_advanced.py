# slither_io_advanced.py
import pygame
import random
import math
import json
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Dict
import time

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

# ==================== ENUMERACIONES ====================
class GameMode(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    LEADERBOARD = 3
    SETTINGS = 4

class PowerUpType(Enum):
    SPEED_BOOST = 1
    SHIELD = 2
    MAGNET = 3
    INVINCIBLE = 4

class Difficulty(Enum):
    EASY = 1
    NORMAL = 2
    HARD = 3
    NIGHTMARE = 4

# ==================== CONFIGURACIÓN ====================
@dataclass
class GameSettings:
    screen_width: int = 1200
    screen_height: int = 800
    fps: int = 60
    grid_size: int = 10
    
    # Colores
    bg_color: Tuple = (10, 10, 20)
    snake_color: Tuple = (0, 255, 100)
    food_color: Tuple = (255, 50, 50)
    obstacle_color: Tuple = (150, 150, 150)
    powerup_colors: Dict = None
    text_color: Tuple = (255, 255, 255)
    
    # Serpiente
    initial_length: int = 5
    base_speed: float = 5.0
    acceleration: float = 0.02
    
    # Dificultad
    difficulty: Difficulty = Difficulty.NORMAL
    
    def __post_init__(self):
        self.powerup_colors = {
            PowerUpType.SPEED_BOOST: (255, 200, 0),
            PowerUpType.SHIELD: (0, 100, 255),
            PowerUpType.MAGNET: (200, 0, 255),
            PowerUpType.INVINCIBLE: (255, 0, 200)
        }

# ==================== CLASES DE PARTÍCULAS ====================
class Particle:
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 color: Tuple, lifetime: float, size: int):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
    
    def update(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        self.vy += 0.2  # Gravedad
    
    def draw(self, surface: pygame.Surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = int(self.size * (self.lifetime / self.max_lifetime))
        if size > 0:
            pygame.draw.circle(surface, self.color, 
                             (int(self.x), int(self.y)), size)
    
    def is_alive(self) -> bool:
        return self.lifetime > 0

class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []
    
    def emit(self, x: float, y: float, count: int, 
             color: Tuple, lifetime: float = 0.5):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            particle = Particle(x, y, vx, vy, color, lifetime, 5)
            self.particles.append(particle)
    
    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update(dt)
    
    def draw(self, surface: pygame.Surface):
        for particle in self.particles:
            particle.draw(surface)

# ==================== CLASES DE OBJETOS DEL JUEGO ====================
@dataclass
class Food:
    x: float
    y: float
    value: int = 1
    powerup_type: PowerUpType = None
    spawned_time: float = 0.0
    
    def draw(self, surface: pygame.Surface, settings: GameSettings):
        if self.powerup_type:
            color = settings.powerup_colors[self.powerup_type]
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 7)
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), 5)
        else:
            pygame.draw.circle(surface, settings.food_color, 
                             (int(self.x), int(self.y)), 5)
    
    def is_old(self, max_age: float = 30.0) -> bool:
        return time.time() - self.spawned_time > max_age

class Obstacle:
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
    
    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, surface: pygame.Surface, settings: GameSettings):
        pygame.draw.rect(surface, settings.obstacle_color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
    
    def collides_with_point(self, x: float, y: float, radius: float = 5) -> bool:
        return self.rect.collidepoint(x, y)
    
    def collides_with_circle(self, x: float, y: float, radius: float) -> bool:
        closest_x = max(self.rect.left, min(x, self.rect.right))
        closest_y = max(self.rect.top, min(y, self.rect.bottom))
        distance = math.sqrt((x - closest_x)**2 + (y - closest_y)**2)
        return distance < radius

class PowerUp:
    def __init__(self, ptype: PowerUpType, duration: float = 5.0):
        self.type = ptype
        self.duration = duration
        self.activated_time = time.time()
    
    def is_expired(self) -> bool:
        return time.time() - self.activated_time > self.duration
    
    def get_remaining_time(self) -> float:
        return max(0, self.duration - (time.time() - self.activated_time))

# ==================== CLASE SERPIENTE ====================
class Snake:
    def __init__(self, x: float, y: float, settings: GameSettings, 
                 color: Tuple = None, ai: bool = False):
        self.settings = settings
        self.body: List[Tuple[float, float]] = []
        self.color = color or settings.snake_color
        self.ai = ai
        
        # Inicializar cuerpo
        for i in range(settings.initial_length):
            self.body.append((x - i * settings.grid_size, y))
        
        self.direction = (1.0, 0.0)
        self.next_direction = (1.0, 0.0)
        self.speed = settings.base_speed
        self.score = 0
        self.grow_pending = 0
        self.alive = True
        self.name = "Player" if not ai else f"AI_{random.randint(1000, 9999)}"
        
        # Power-ups
        self.active_powerups: List[PowerUp] = []
        self.shield = False
        self.magnet_range = 0
        self.invincible = False
        self.invincible_flashing = False
        
        # Estadísticas
        self.foods_eaten = 0
        self.start_time = time.time()
    
    def set_direction(self, dx: float, dy: float):
        # Evitar que la serpiente se voltee hacia sí misma
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.next_direction = (dx, dy)
    
    def apply_powerup(self, powerup_type: PowerUpType):
        # Remover power-ups del mismo tipo
        self.active_powerups = [p for p in self.active_powerups 
                               if p.type != powerup_type]
        
        if powerup_type == PowerUpType.SPEED_BOOST:
            self.speed *= 1.3
        elif powerup_type == PowerUpType.SHIELD:
            self.shield = True
        elif powerup_type == PowerUpType.MAGNET:
            self.magnet_range = 150
        elif powerup_type == PowerUpType.INVINCIBLE:
            self.invincible = True
        
        self.active_powerups.append(PowerUp(powerup_type, 8.0))
    
    def update_powerups(self):
        expired = []
        for powerup in self.active_powerups:
            if powerup.is_expired():
                expired.append(powerup)
                
                if powerup.type == PowerUpType.SPEED_BOOST:
                    self.speed /= 1.3
                elif powerup_type == PowerUpType.SHIELD:
                    self.shield = False
                elif powerup_type == PowerUpType.MAGNET:
                    self.magnet_range = 0
                elif powerup_type == PowerUpType.INVINCIBLE:
                    self.invincible = False
        
        for powerup in expired:
            self.active_powerups.remove(powerup)
    
    def update(self, foods: List[Food], obstacles: List[Obstacle]):
        if not self.alive:
            return
        
        self.update_powerups()
        self.direction = self.next_direction
        
        # Calcular nueva posición de la cabeza
        head_x, head_y = self.body[0]
        new_x = head_x + self.direction[0] * self.speed
        new_y = head_y + self.direction[1] * self.speed
        
        # Colisión con bordes (envolvimiento)
        new_x = new_x % self.settings.screen_width
        new_y = new_y % self.settings.screen_height
        
        # Agregar nueva cabeza
        self.body.insert(0, (new_x, new_y))
        
        # Eliminar cola si no hay crecimiento pendiente
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
        
        # Verificar colisión con obstáculos
        if not self.invincible:
            for obstacle in obstacles:
                if obstacle.collides_with_circle(new_x, new_y, 5):
                    self.alive = False
                    return
        
        # Verificar colisión con uno mismo
        if not self.invincible:
            for segment in self.body[5:]:  # No contar los primeros 5 segmentos
                if math.sqrt((new_x - segment[0])**2 + (new_y - segment[1])**2) < 8:
                    self.alive = False
                    return
        
        # Verificar colisión con comida
        for food in foods[:]:
            dx = food.x - new_x
            dy = food.y - new_y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 10 or (self.magnet_range > 0 and distance < self.magnet_range):
                self.eat_food(food, foods)
                foods.remove(food)
    
    def eat_food(self, food: Food, foods: List[Food]):
        self.grow_pending += food.value
        self.score += food.value * 10
        self.foods_eaten += 1
        
        if food.powerup_type:
            self.apply_powerup(food.powerup_type)
    
    def ai_update(self, foods: List[Food]):
        if not self.ai or not self.alive:
            return
        
        if not foods:
            return
        
        # Encontrar la comida más cercana
        head_x, head_y = self.body[0]
        closest_food = min(foods, 
                          key=lambda f: (f.x - head_x)**2 + (f.y - head_y)**2)
        
        dx = closest_food.x - head_x
        dy = closest_food.y - head_y
        
        # Convertir a dirección normalizada
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            dx /= length
            dy /= length
            
            # Determinar mejor dirección
            if abs(dx) > abs(dy):
                self.set_direction(1 if dx > 0 else -1, 0)
            else:
                self.set_direction(0, 1 if dy > 0 else -1)
    
    def draw(self, surface: pygame.Surface):
        if not self.alive:
            return
        
        # Dibujar cuerpo
        for i, (x, y) in enumerate(self.body):
            # Degradado de color
            alpha = int(255 * (1 - i / len(self.body)))
            color = (
                int(self.color[0] * alpha / 255),
                int(self.color[1] * alpha / 255),
                int(self.color[2] * alpha / 255)
            )
            pygame.draw.circle(surface, color, (int(x), int(y)), 5)
            
            if i == 0 and self.invincible:
                pygame.draw.circle(surface, (255, 0, 0), (int(x), int(y)), 8, 2)
        
        # Dibujar escudo
        if self.shield:
            head_x, head_y = self.body[0]
            pygame.draw.circle(surface, (0, 100, 255), (int(head_x), int(head_y)), 15, 2)
        
        # Dibujar rango de imán
        if self.magnet_range > 0:
            head_x, head_y = self.body[0]
            pygame.draw.circle(surface, (200, 0, 255), 
                             (int(head_x), int(head_y)), 
                             int(self.magnet_range), 1)
    
    def get_length(self) -> int:
        return len(self.body)

# ==================== CLASE CÁMARA ====================
class Camera:
    def __init__(self, width: float, height: float, 
                 screen_width: float, screen_height: float):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def follow(self, target_x: float, target_y: float):
        self.x = target_x - self.screen_width / 2
        self.y = target_y - self.screen_height / 2
        
        self.x = max(0, min(self.x, self.width - self.screen_width))
        self.y = max(0, min(self.y, self.height - self.screen_height))
    
    def apply(self, x: float, y: float) -> Tuple[float, float]:
        return (x - self.x, y - self.y)
    
    def is_visible(self, x: float, y: float, radius: float = 0) -> bool:
        return (self.x - radius < x < self.x + self.screen_width + radius and
                self.y - radius < y < self.y + self.screen_height + radius)

# ==================== ADMINISTRADOR DE TABLA DE POSICIONES ====================
class LeaderboardManager:
    def __init__(self, filename: str = "leaderboard.json"):
        self.filename = filename
        self.scores: List[Dict] = []
        self.load()
    
    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.scores = json.load(f)
                self.scores = sorted(self.scores, 
                                    key=lambda x: x['score'], 
                                    reverse=True)[:10]
            except:
                self.scores = []
        else:
            self.scores = []
    
    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.scores, f)
    
    def add_score(self, name: str, score: int, length: int, time_played: float):
        self.scores.append({
            'name': name,
            'score': score,
            'length': length,
            'time': time_played,
            'date': time.strftime("%Y-%m-%d %H:%M:%S")
        })
        self.scores = sorted(self.scores, 
                            key=lambda x: x['score'], 
                            reverse=True)[:10]
        self.save()
    
    def get_top_scores(self, count: int = 10) -> List[Dict]:
        return self.scores[:count]
    
    def is_high_score(self, score: int) -> bool:
        if len(self.scores) < 10:
            return True
        return score > self.scores[-1]['score']

# ==================== ADMINISTRADOR DE JUEGO ====================
class GameManager:
    def __init__(self, settings: GameSettings):
        self.settings = settings
        self.screen = pygame.display.set_mode(
            (settings.screen_width, settings.screen_height)
        )
        pygame.display.set_caption("Slither.io - Advanced Edition")
        
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        self.mode = GameMode.MENU
        self.leaderboard_manager = LeaderboardManager()
        
        self.player_snake = None
        self.ai_snakes: List[Snake] = []
        self.foods: List[Food] = []
        self.obstacles: List[Obstacle] = []
        self.particle_system = ParticleSystem()
        self.camera = None
        
        self.game_time = 0.0
        self.spawn_timer = 0.0
        self.ai_spawn_timer = 0.0
        self.difficulty_timer = 0.0
        
        self.setup_game()
    
    def setup_game(self):
        self.player_snake = Snake(
            self.settings.screen_width / 2,
            self.settings.screen_height / 2,
            self.settings,
            (0, 255, 100)
        )
        self.player_snake.name = "Tú"
        
        self.ai_snakes = []
        for i in range(3 if self.settings.difficulty == Difficulty.EASY else 
                      5 if self.settings.difficulty == Difficulty.NORMAL else 8):
            ai_snake = Snake(
                random.randint(100, self.settings.screen_width - 100),
                random.randint(100, self.settings.screen_height - 100),
                self.settings,
                (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
                ai=True
            )
            self.ai_snakes.append(ai_snake)
        
        self.foods = []
        self.obstacles = []
        
        # Crear obstáculos
        self._create_obstacles()
        
        # Generar comida inicial
        for _ in range(50):
            self._spawn_food()
        
        self.camera = Camera(self.settings.screen_width, 
                            self.settings.screen_height,
                            self.settings.screen_width,
                            self.settings.screen_height)
        
        self.game_time = 0.0
        self.spawn_timer = 0.0
    
    def _create_obstacles(self):
        # Crear una red de obstáculos
        num_obstacles = 8 if self.settings.difficulty.value <= 2 else 12
        for _ in range(num_obstacles):
            x = random.randint(0, self.settings.screen_width - 100)
            y = random.randint(0, self.settings.screen_height - 100)
            width = random.randint(50, 150)
            height = random.randint(50, 150)
            self.obstacles.append(Obstacle(x, y, width, height))
    
    def _spawn_food(self):
        x = random.uniform(50, self.settings.screen_width - 50)
        y = random.uniform(50, self.settings.screen_height - 50)
        
        # 10% de probabilidad de power-up
        powerup_type = None
        if random.random() < 0.1:
            powerup_type = random.choice(list(PowerUpType))
        
        food = Food(x, y, powerup_type=powerup_type)
        food.spawned_time = time.time()
        self.foods.append(food)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.mode == GameMode.MENU:
                    if event.key == pygame.K_SPACE:
                        self.mode = GameMode.PLAYING
                    elif event.key == pygame.K_l:
                        self.mode = GameMode.LEADERBOARD
                    elif event.key == pygame.K_s:
                        self.mode = GameMode.SETTINGS
                
                elif self.mode == GameMode.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.mode = GameMode.MENU
                    elif event.key == pygame.K_UP:
                        self.player_snake.set_direction(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.player_snake.set_direction(0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.player_snake.set_direction(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.player_snake.set_direction(1, 0)
                
                elif self.mode == GameMode.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.mode = GameMode.PLAYING
                        self.setup_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.mode = GameMode.MENU
                
                elif self.mode == GameMode.LEADERBOARD:
                    if event.key == pygame.K_ESCAPE:
                        self.mode = GameMode.MENU
                
                elif self.mode == GameMode.SETTINGS:
                    if event.key == pygame.K_1:
                        self.settings.difficulty = Difficulty.EASY
                    elif event.key == pygame.K_2:
                        self.settings.difficulty = Difficulty.NORMAL
                    elif event.key == pygame.K_3:
                        self.settings.difficulty = Difficulty.HARD
                    elif event.key == pygame.K_4:
                        self.settings.difficulty = Difficulty.NIGHTMARE
                    elif event.key == pygame.K_ESCAPE:
                        self.mode = GameMode.MENU
        
        return True
    
    def update(self, dt: float):
        if self.mode != GameMode.PLAYING:
            return
        
        self.game_time += dt
        self.spawn_timer += dt
        self.ai_spawn_timer += dt
        self.difficulty_timer += dt
        
        # Aumentar dificultad con el tiempo
        if self.difficulty_timer > 30:
            self.settings.base_speed += 0.1
            self.difficulty_timer = 0
        
        # Actualizar serpientes
        self.player_snake.update(self.foods, self.obstacles)
        
        for ai_snake in self.ai_snakes:
            ai_snake.ai_update(self.foods)
            ai_snake.update(self.foods, self.obstacles)
        
        # Remover serpientes IA muertas y reemplazarlas
        alive_ai = [s for s in self.ai_snakes if s.alive]
        dead_count = len(self.ai_snakes) - len(alive_ai)
        self.ai_snakes = alive_ai
        
        for _ in range(dead_count):
            ai_snake = Snake(
                random.randint(100, self.settings.screen_width - 100),
                random.randint(100, self.settings.screen_height - 100),
                self.settings,
                (random.randint(100, 255), random.randint(100, 255), 
                 random.randint(100, 255)),
                ai=True
            )
            self.ai_snakes.append(ai_snake)
        
        # Generar comida
        if self.spawn_timer > 0.5 and len(self.foods) < 100:
            self._spawn_food()
            self.spawn_timer = 0
        
        # Remover comida vieja
        self.foods = [f for f in self.foods 
                     if not f.is_old()]
        
        # Actualizar partículas
        self.particle_system.update(dt)
        
        # Verificar si el jugador está muerto
        if not self.player_snake.alive:
            self.mode = GameMode.GAME_OVER
            time_played = time.time() - self.player_snake.start_time
            self.leaderboard_manager.add_score(
                self.player_snake.name,
                self.player_snake.score,
                self.player_snake.get_length(),
                time_played
            )
        
        # Actualizar cámara
        if self.player_snake.body:
            head_x, head_y = self.player_snake.body[0]
            self.camera.follow(head_x, head_y)
    
    def draw(self):
        self.screen.fill(self.settings.bg_color)
        
        if self.mode == GameMode.MENU:
            self._draw_menu()
        elif self.mode == GameMode.PLAYING:
            self._draw_game()
        elif self.mode == GameMode.GAME_OVER:
            self._draw_game_over()
        elif self.mode == GameMode.LEADERBOARD:
            self._draw_leaderboard()
        elif self.mode == GameMode.SETTINGS:
            self._draw_settings()
        
        pygame.display.flip()
    
    def _draw_menu(self):
        title = self.font_large.render("SLITHER.IO ADVANCED", True, 
                                       self.settings.text_color)
        self.screen.blit(title, (self.settings.screen_width // 2 - 
                                 title.get_width() // 2, 50))
        
        play_text = self.font_medium.render("Presiona ESPACIO para jugar", True, 
                                           (0, 255, 100))
        self.screen.blit(play_text, (self.settings.screen_width // 2 - 
                                     play_text.get_width() // 2, 200))
        
        leaderboard_text = self.font_small.render("Presiona L para tabla de posiciones", 
                                                 True, self.settings.text_color)
        self.screen.blit(leaderboard_text, (self.settings.screen_width // 2 - 
                                           leaderboard_text.get_width() // 2, 300))
        
        settings_text = self.font_small.render("Presiona S para opciones", True, 
                                              self.settings.text_color)
        self.screen.blit(settings_text, (self.settings.screen_width // 2 - 
                                        settings_text.get_width() // 2, 350))
        
        # Mostrar serpientes demostrativas
        for i, ai_snake in enumerate(self.ai_snakes[:3]):
            offset_x = 200 + i * 300
            for j, (x, y) in enumerate(ai_snake.body[:5]):
                alpha = int(255 * (1 - j / 5))
                color = (ai_snake.color[0] * alpha // 255,
                        ai_snake.color[1] * alpha // 255,
                        ai_snake.color[2] * alpha // 255)
                pygame.draw.circle(self.screen, color, 
                                 (offset_x - j * 10, 500), 4)
    
    def _draw_game(self):
        # Dibujar grid
        grid_color = (20, 20, 40)
        for x in range(0, self.settings.screen_width + 100, 100):
            screen_x = x - self.camera.x
            if -50 < screen_x < self.settings.screen_width + 50:
                pygame.draw.line(self.screen, grid_color, 
                               (screen_x, 0), (screen_x, self.settings.screen_height), 1)
        
        for y in range(0, self.settings.screen_height + 100, 100):
            screen_y = y - self.camera.y
            if -50 < screen_y < self.settings.screen_height + 50:
                pygame.draw.line(self.screen, grid_color, 
                               (0, screen_y), (self.settings.screen_width, screen_y), 1)
        
        # Dibujar obstáculos
        for obstacle in self.obstacles:
            screen_x, screen_y = self.camera.apply(obstacle.x, obstacle.y)
            if self.camera.is_visible(obstacle.x, obstacle.y, 100):
                pygame.draw.rect(self.screen, self.settings.obstacle_color,
                               (screen_x, screen_y, obstacle.width, obstacle.height))
                pygame.draw.rect(self.screen, (200, 200, 200),
                               (screen_x, screen_y, obstacle.width, obstacle.height), 2)
        
        # Dibujar comida
        for food in self.foods:
            if self.camera.is_visible(food.x, food.y, 10):
                screen_x, screen_y = self.camera.apply(food.x, food.y)
                food.draw(self.screen, self.settings)
                # Mover a coordenadas de pantalla
                if food.powerup_type:
                    color = self.settings.powerup_colors[food.powerup_type]
                    pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), 7)
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                     (int(screen_x), int(screen_y)), 5)
                else:
                    pygame.draw.circle(self.screen, self.settings.food_color,
                                     (int(screen_x), int(screen_y)), 5)
        
        # Dibujar serpientes
        for snake in [self.player_snake] + self.ai_snakes:
            if snake.alive and snake.body:
                head_x, head_y = snake.body[0]
                if self.camera.is_visible(head_x, head_y, 50):
                    for i, (x, y) in enumerate(snake.body):
                        screen_x, screen_y = self.camera.apply(x, y)
                        alpha = int(255 * (1 - i / len(snake.body)))
                        color = (
                            int(snake.color[0] * alpha / 255),
                            int(snake.color[1] * alpha / 255),
                            int(snake.color[2] * alpha / 255)
                        )
                        pygame.draw.circle(self.screen, color, 
                                         (int(screen_x), int(screen_y)), 5)
                        
                        if i == 0 and snake.invincible:
                            pygame.draw.circle(self.screen, (255, 0, 0), 
                                             (int(screen_x), int(screen_y)), 8, 2)
                    
                    if snake.shield:
                        head_x_screen, head_y_screen = self.camera.apply(head_x, head_y)
                        pygame.draw.circle(self.screen, (0, 100, 255), 
                                         (int(head_x_screen), int(head_y_screen)), 15, 2)
        
        # Dibujar partículas
        self.particle_system.draw(self.screen)
        
        # Dibujar HUD
        self._draw_hud()
    
    def _draw_hud(self):
        # Score
        score_text = self.font_medium.render(f"Puntuación: {self.player_snake.score}", 
                                            True, self.settings.text_color)
        self.screen.blit(score_text, (10, 10))
        
        # Longitud
        length_text = self.font_small.render(f"Longitud: {self.player_snake.get_length()}", 
                                            True, self.settings.text_color)
        self.screen.blit(length_text, (10, 50))
        
        # Velocidad
        speed_text = self.font_small.render(f"Velocidad: {self.player_snake.speed:.1f}", 
                                           True, self.settings.text_color)
        self.screen.blit(speed_text, (10, 80))
        
        # Tiempo
        time_text = self.font_small.render(f"Tiempo: {int(self.game_time)}s", 
                                          True, self.settings.text_color)
        self.screen.blit(time_text, (10, 110))
        
        # Power-ups activos
        y_offset = 10
        for powerup in self.player_snake.active_powerups:
            remaining = powerup.get_remaining_time()
            powerup_text = self.font_small.render(
                f"{powerup.type.name}: {remaining:.1f}s",
                True,
                self.settings.powerup_colors[powerup.type]
            )
            self.screen.blit(powerup_text, 
                           (self.settings.screen_width - powerup_text.get_width() - 10, 
                            y_offset))
            y_offset += 30
        
        # Top 3 serpientes
        all_snakes = [self.player_snake] + self.ai_snakes
        all_snakes.sort(key=lambda s: s.score, reverse=True)
        
        y_offset = self.settings.screen_height - 120
        ranking_title = self.font_small.render("Top Serpientes:", True, 
                                              self.settings.text_color)
        self.screen.blit(ranking_title, (10, y_offset))
        
        for i, snake in enumerate(all_snakes[:3]):
            rank_text = self.font_small.render(
                f"{i+1}. {snake.name}: {snake.score} pts ({snake.get_length()})",
                True,
                snake.color
            )
            self.screen.blit(rank_text, (10, y_offset + 30 + i * 25))
    
    def _draw_game_over(self):
        self._draw_game()  # Dibujar el juego de fondo
        
        # Overlay oscuro
        overlay = pygame.Surface((self.settings.screen_width, 
                                 self.settings.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Texto
        game_over_text = self.font_large.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(game_over_text, 
                        (self.settings.screen_width // 2 - 
                         game_over_text.get_width() // 2, 100))
        
        score_text = self.font_medium.render(
            f"Puntuación Final: {self.player_snake.score}",
            True,
            self.settings.text_color
        )
        self.screen.blit(score_text,
                        (self.settings.screen_width // 2 - 
                         score_text.get_width() // 2, 200))
        
        length_text = self.font_medium.render(
            f"Longitud Final: {self.player_snake.get_length()}",
            True,
            self.settings.text_color
        )
        self.screen.blit(length_text,
                        (self.settings.screen_width // 2 - 
                         length_text.get_width() // 2, 260))
        
        # Verificar si es high score
        if self.leaderboard_manager.is_high_score(self.player_snake.score):
            high_score_text = self.font_medium.render(
                "¡NUEVO RÉCORD!",
                True,
                (255, 215, 0)
            )
            self.screen.blit(high_score_text,
                            (self.settings.screen_width // 2 - 
                             high_score_text.get_width() // 2, 320))
        
        continue_text = self.font_small.render(
            "Presiona ESPACIO para reintentar o ESC para menú",
            True,
            self.settings.text_color
        )
        self.screen.blit(continue_text,
                        (self.settings.screen_width // 2 - 
                         continue_text.get_width() // 2, 400))
    
    def _draw_leaderboard(self):
        title = self.font_large.render("TABLA DE POSICIONES", True, 
                                       self.settings.text_color)
        self.screen.blit(title, (self.settings.screen_width // 2 - 
                                 title.get_width() // 2, 50))
        
        scores = self.leaderboard_manager.get_top_scores()
        
        if not scores:
            no_scores = self.font_medium.render("Sin puntuaciones registradas", 
                                               True, self.settings.text_color)
            self.screen.blit(no_scores, (self.settings.screen_width // 2 - 
                                        no_scores.get_width() // 2, 200))
        else:
            y_offset = 150
            for i, score in enumerate(scores):
                rank_text = self.font_medium.render(
                    f"{i+1}. {score['name']}: {score['score']} pts (Longitud: {score['length']})",
                    True,
                    (255, 215, 0) if i == 0 else self.settings.text_color
                )
                self.screen.blit(rank_text, (self.settings.screen_width // 2 - 
                                            rank_text.get_width() // 2, y_offset))
                
                date_text = self.font_small.render(
                    f"  {score['date']}",
                    True,
                    (150, 150, 150)
                )
                self.screen.blit(date_text, (self.settings.screen_width // 2 - 
                                            date_text.get_width() // 2, y_offset + 30))
                
                y_offset += 80
        
        back_text = self.font_small.render("Presiona ESC para volver", True, 
                                          self.settings.text_color)
        self.screen.blit(back_text, (self.settings.screen_width // 2 - 
                                    back_text.get_width() // 2, 
                                    self.settings.screen_height - 50))
    
    def _draw_settings(self):
        title = self.font_large.render("OPCIONES", True, self.settings.text_color)
        self.screen.blit(title, (self.settings.screen_width // 2 - 
                                 title.get_width() // 2, 50))
        
        diff_title = self.font_medium.render("Selecciona Dificultad:", True, 
                                            self.settings.text_color)
        self.screen.blit(diff_title, (150, 200))
        
        difficulties = [
            ("1. FÁCIL", (0, 255, 0)),
            ("2. NORMAL", (255, 255, 0)),
            ("3. DIFÍCIL", (255, 100, 0)),
            ("4. PESADILLA", (255, 0, 0))
        ]
        
        for i, (text, color) in enumerate(difficulties):
            is_selected = (i + 1 == self.settings.difficulty.value)
            current_color = (255, 255, 255) if is_selected else color
            prefix = "► " if is_selected else "  "
            diff_text = self.font_medium.render(prefix + text, True, current_color)
            self.screen.blit(diff_text, (200, 280 + i * 60))
        
        back_text = self.font_small.render("Presiona ESC para volver", True, 
                                          self.settings.text_color)
        self.screen.blit(back_text, (self.settings.screen_width // 2 - 
                                    back_text.get_width() // 2, 
                                    self.settings.screen_height - 50))
    
    def run(self):
        running = True
        
        while running:
            running = self.handle_events()
            dt = self.clock.tick(self.settings.fps) / 1000.0
            self.update(dt)
            self.draw()
        
        pygame.quit()

# ==================== PUNTO DE ENTRADA ====================
if __name__ == "__main__":
    settings = GameSettings()
    game = GameManager(settings)
    game.run()