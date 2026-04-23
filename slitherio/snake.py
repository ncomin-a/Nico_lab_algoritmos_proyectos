"""
Módulo de la serpiente (jugadores y bots).
Versión híbrida: lógica avanzada + compatibilidad con main.py/ui.py.
"""

import math
import random
import pygame

from constants import (
    WORLD_W, WORLD_H, SEGMENT_RADIUS, SEGMENT_GAP,
    INITIAL_LENGTH, SPEED_BASE, SPEED_BOOST, BOOST_DRAIN,
    GROW_PER_FOOD, TURN_SPEED,
    PU_SPEED, PU_GHOST, PU_MAGNET, PU_SHIELD, PU_DOUBLE,
    POWERUP_DURATION, AI_REACTION_TIME, AI_SIGHT_RADIUS, AI_DANGER_RADIUS
)


class Segment:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class Snake:
    def __init__(self, color_info: dict, snake_id: int, x=None, y=None):
        self.id = snake_id
        self.color_info = color_info
        self.body_color = color_info["body"]
        self.head_color = color_info["head"]
        self.glow_color = color_info.get("glow", (*color_info["body"][:3], 60))
        self.name = color_info.get("name", f"Snake {snake_id}")

        cx = x if x is not None else random.randint(300, WORLD_W - 300)
        cy = y if y is not None else random.randint(300, WORLD_H - 300)

        self.angle = random.uniform(0, 2 * math.pi)
        self.target_angle = self.angle

        self.segments: list[Segment] = []
        for i in range(INITIAL_LENGTH):
            sx = cx - i * SEGMENT_GAP * math.cos(self.angle)
            sy = cy - i * SEGMENT_GAP * math.sin(self.angle)
            self.segments.append(Segment(sx, sy))

        self.target_length = float(INITIAL_LENGTH)
        self.alive = True
        self.boosting = False

        self.score = 0
        self.kills = 0
        self.foods_eaten = 0
        self.total_eaten = 0

        self.powerups: dict[str, float] = {}
        self.death_timer = 0.0
        self.killed_by = None

        self.lifetime = 0.0
        self.max_mass = len(self.segments)
        self.boost_energy = 100
        self.max_boost_energy = 100
        self.boost_depleted = False  # True cuando se agotó, hasta recargar al 50%

        self._boost_particle_timer = 0.0
        self.is_human = False
        self.has_shield_flag = False

    @property
    def head(self) -> Segment:
        return self.segments[0]

    @property
    def length(self) -> int:
        return len(self.segments)

    @property
    def speed(self):
        if self.boosting and self.boost_energy > 0:
            base = SPEED_BOOST
        else:
            base = SPEED_BASE

        if PU_SPEED in self.powerups:
            base *= 1.5

        return base

    @property
    def has_ghost(self) -> bool:
        return PU_GHOST in self.powerups

    @property
    def has_shield(self) -> bool:
        return PU_SHIELD in self.powerups

    @property
    def double_score(self) -> bool:
        return PU_DOUBLE in self.powerups

    @property
    def has_magnet(self) -> bool:
        return PU_MAGNET in self.powerups

    def update(self, dt: float):
        if not self.alive:
            return

        self.lifetime += dt

        spd = self.speed
        new_x = self.head.x + spd * dt * math.cos(self.angle)
        new_y = self.head.y + spd * dt * math.sin(self.angle)

        new_x = new_x % WORLD_W
        new_y = new_y % WORLD_H

        self.segments.insert(0, Segment(new_x, new_y))

        while len(self.segments) > max(1, int(round(self.target_length))):
            self.segments.pop()

        # 🔥 BOOST CON ENERGÍA (tipo Slither)
        # Si se agotó, bloquear hasta recargar al 50%
        if self.boost_energy <= 0:
            self.boost_depleted = True
            self.boosting = False

        if self.boost_depleted:
            self.boosting = False
            self.boost_energy += 15 * dt
            if self.boost_energy >= self.max_boost_energy * 0.5:
                self.boost_depleted = False  # ya puede volver a usar boost
            if self.boost_energy > self.max_boost_energy:
                self.boost_energy = self.max_boost_energy
        elif self.boosting:
            self.boost_energy -= 20 * dt
            if self.boost_energy <= 0:
                self.boost_energy = 0
                self.boosting = False
                self.boost_depleted = True
        else:
            self.boost_energy += 15 * dt
            if self.boost_energy > self.max_boost_energy:
                self.boost_energy = self.max_boost_energy

        # Reducir duración de power-ups
        for k in list(self.powerups.keys()):
            self.powerups[k] -= dt
            if self.powerups[k] <= 0:
                del self.powerups[k]

        self.max_mass = max(self.max_mass, len(self.segments))
        self._boost_particle_timer -= dt

    def grow(self, amount: int = GROW_PER_FOOD):
        mult = 2 if self.double_score else 1
        self.target_length += amount * mult
        self.score += 10 * mult
        self.foods_eaten += 1
        self.total_eaten += 1
        self.max_mass = max(self.max_mass, len(self.segments))

    def add_powerup(self, pu_type: str):
        self.powerups[pu_type] = POWERUP_DURATION

    def die(self, killer=None):
        self.alive = False
        self.killed_by = killer
        if killer and killer is not self:
            killer.kills += 1
            killer.score += max(50, self.length * 2)

    def head_rect(self) -> pygame.Rect:
        r = SEGMENT_RADIUS
        return pygame.Rect(int(self.head.x - r), int(self.head.y - r), r * 2, r * 2)

    def collides_with_segment(self, sx: float, sy: float, radius: float = SEGMENT_RADIUS) -> bool:
        dx = self.head.x - sx
        dy = self.head.y - sy
        return (dx * dx + dy * dy) < (SEGMENT_RADIUS + radius) ** 2

    def collides_with_snake(self, other, skip_head=True):
        if self is other:
            start = 1
        else:
            start = 1 if skip_head else 0

        hx, hy = self.head.x, self.head.y

        # 🔥 radio más grande para evitar "atravesar"
        collision_dist = (SEGMENT_RADIUS * 2.5) ** 2

        for seg in other.segments[start:]:
            dx = hx - seg.x
            dy = hy - seg.y

            if dx * dx + dy * dy < collision_dist:
                return True

        return False

    def draw(self, surface: pygame.Surface, camera, alpha_override: int = 255):
        if not self.segments:
            return

        n = len(self.segments)
        body_c = self.body_color
        head_c = self.head_color
        glow_c = self.glow_color

        ghost_alpha = 120 if self.has_ghost else alpha_override

        for i in range(n - 1, -1, -1):
            seg = self.segments[i]
            sx, sy = camera.apply((seg.x, seg.y))
            sx = int(sx)
            sy = int(sy)

            t = 1 - (i / max(1, n)) * 0.3
            r = max(4, int(SEGMENT_RADIUS * t))

            if i == 0:
                color = head_c
            else:
                ratio = i / max(1, n - 1)
                color = (
                    int(head_c[0] * (1 - ratio) + body_c[0] * ratio),
                    int(head_c[1] * (1 - ratio) + body_c[1] * ratio),
                    int(head_c[2] * (1 - ratio) + body_c[2] * ratio),
                )

            if i == 0 or i % 4 == 0:
                glow_surf = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
                ga = int(glow_c[3] * (ghost_alpha / 255))
                pygame.draw.circle(glow_surf, (*glow_c[:3], ga), (r * 2, r * 2), r * 2)
                surface.blit(glow_surf, (sx - r * 2, sy - r * 2))

            if ghost_alpha < 255:
                seg_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(seg_surf, (*color, ghost_alpha), (r + 1, r + 1), r)
                surface.blit(seg_surf, (sx - r - 1, sy - r - 1))
            else:
                pygame.draw.circle(surface, color, (sx, sy), r)
                pygame.draw.circle(
                    surface,
                    (
                        min(255, color[0] + 60),
                        min(255, color[1] + 60),
                        min(255, color[2] + 60),
                    ),
                    (sx - r // 3, sy - r // 3),
                    max(2, r // 3),
                )

        self._draw_eyes(surface, camera)

        if self.has_shield:
            hx, hy = camera.apply((self.head.x, self.head.y))
            hx = int(hx)
            hy = int(hy)

            shield_surf = pygame.Surface((SEGMENT_RADIUS * 5, SEGMENT_RADIUS * 5), pygame.SRCALPHA)
            pygame.draw.circle(
                shield_surf,
                (80, 220, 255, 80),
                (SEGMENT_RADIUS * 2 + 2, SEGMENT_RADIUS * 2 + 2),
                SEGMENT_RADIUS * 2 + 2,
            )
            surface.blit(
                shield_surf,
                (hx - SEGMENT_RADIUS * 2 - 2, hy - SEGMENT_RADIUS * 2 - 2),
            )

    def _draw_eyes(self, surface: pygame.Surface, camera):
        hx, hy = camera.apply((self.head.x, self.head.y))
        hx = int(hx)
        hy = int(hy)

        r = SEGMENT_RADIUS
        eye_offset = r * 0.6
        perp = self.angle + math.pi / 2

        ex1 = hx + eye_offset * math.cos(perp)
        ey1 = hy + eye_offset * math.sin(perp)
        ex2 = hx - eye_offset * math.cos(perp)
        ey2 = hy - eye_offset * math.sin(perp)

        eye_r = max(2, r // 3)
        pygame.draw.circle(surface, (255, 255, 255), (int(ex1), int(ey1)), eye_r)
        pygame.draw.circle(surface, (255, 255, 255), (int(ex2), int(ey2)), eye_r)

        pupil_r = max(1, eye_r // 2)
        px = math.cos(self.angle) * pupil_r * 0.5
        py = math.sin(self.angle) * pupil_r * 0.5

        pygame.draw.circle(surface, (10, 10, 20), (int(ex1 + px), int(ey1 + py)), pupil_r)
        pygame.draw.circle(surface, (10, 10, 20), (int(ex2 + px), int(ey2 + py)), pupil_r)

    def draw_name(self, surface: pygame.Surface, camera, font: pygame.font.Font):
        if not self.alive:
            return

        hx, hy = camera.apply((self.head.x, self.head.y))
        hx = int(hx)
        hy = int(hy)

        label = font.render(self.name, True, (255, 255, 255))
        rect = label.get_rect(center=(hx, hy - SEGMENT_RADIUS * 2 - 4))
        surface.blit(label, rect)

    def get_food_drops(self) -> list[tuple]:
        """Devuelve comida coloreada con el color del gusano al morir."""
        drops = []
        color = self.body_color  # Color del gusano muerto
        step = max(1, len(self.segments) // 20)
        for seg in self.segments[::step]:
            drops.append((seg.x, seg.y, color))
        return drops


class PlayerSnake(Snake):
    def __init__(self, color_info, snake_id, keys: dict, x=None, y=None):
        super().__init__(color_info, snake_id, x, y)
        self.keys = keys
        self.is_human = True
        self.target_angle = self.angle

    def handle_mouse_input(self, mouse_pos, cam_x, cam_y, zoom):
        """Ajusta el objetivo de giro según el mouse."""
        world_x = mouse_pos[0] / zoom + cam_x
        world_y = mouse_pos[1] / zoom + cam_y
        self.target_angle = math.atan2(world_y - self.head.y, world_x - self.head.x)

    def handle_input(self, pressed):
        """Compatibilidad extra si luego querés usar teclado."""
        self.boosting = pressed[self.keys["boost"]]

    def handle_input_dt(self, pressed, dt: float):
        if pressed[self.keys["boost"]]:
            self.boosting = True

        if pressed[self.keys["left"]]:
            self.angle -= TURN_SPEED * dt
        if pressed[self.keys["right"]]:
            self.angle += TURN_SPEED * dt

    def handle_keyboard_direction(self, pressed, dt):
        """Actualiza target_angle basado en input de teclado (para modo pantalla dividida)."""
        # Si presiona left/right: rotar alrededor del ángulo actual
        if pressed[self.keys["left"]]:
            self.target_angle -= TURN_SPEED * 2.5 * dt
        if pressed[self.keys["right"]]:
            self.target_angle += TURN_SPEED * 2.5 * dt
        
        # Si presiona up/down: apuntar hacia direcciones cardinales
        if pressed[self.keys["up"]]:
            self.target_angle = -math.pi / 2  # Arriba
        if pressed[self.keys["down"]]:
            self.target_angle = math.pi / 2   # Abajo

    def update(self, dt):
        diff = (self.target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        max_turn = TURN_SPEED * dt
        if abs(diff) < max_turn:
            self.angle = self.target_angle
        else:
            self.angle += max_turn * (1 if diff > 0 else -1)

        super().update(dt)


class BotSnake(Snake):
    """IA con tres comportamientos: buscar comida, evitar peligros, perseguir."""

    BEHAVIOR_WANDER = "wander"
    BEHAVIOR_HUNT = "hunt"
    BEHAVIOR_FLEE = "flee"

    def __init__(self, color_info, snake_id, difficulty: float = 1.0, x=None, y=None):
        super().__init__(color_info, snake_id, x, y)
        self.is_human = False
        self.difficulty = difficulty

        self._react_timer = 0.0
        self._target_angle = self.angle
        self._behavior = self.BEHAVIOR_WANDER
        self._wander_target: tuple[float, float] | None = None
        self._wander_timer = 0.0

    def ai_update(self, dt: float, food_list: list, snakes: list["Snake"], powerups: list):
        """Toma decisiones de IA y actualiza el ángulo."""
        self._react_timer -= dt
        self._wander_timer -= dt

        if self._react_timer > 0:
            self._smooth_turn(dt)
            super().update(dt)
            return

        self._react_timer = AI_REACTION_TIME / max(0.5, self.difficulty)

        hx, hy = self.head.x, self.head.y

        # 1) HUIR si hay peligro real (solo serpientes BASTANTE más grandes)
        danger_angle = self._find_danger(snakes)
        if danger_angle is not None:
            self._behavior = self.BEHAVIOR_FLEE
            self._target_angle = danger_angle + math.pi + random.uniform(-0.3, 0.3)
            if not self.boost_depleted:
                self.boosting = True
            self._smooth_turn(dt)
            super().update(dt)
            return

        self.boosting = False

        # 2) CAZAR serpiente más pequeña cercana
        hunt_target = self._find_hunt_target(snakes)
        if hunt_target is not None:
            tx, ty = hunt_target
            self._behavior = self.BEHAVIOR_HUNT
            self._target_angle = math.atan2(ty - hy, tx - hx)
            # boost al cazar si tiene energía
            dist = math.hypot(tx - hx, ty - hy)
            if dist < AI_SIGHT_RADIUS * 0.6 and not self.boost_depleted and self.boost_energy > 30:
                self.boosting = True
            self._smooth_turn(dt)
            super().update(dt)
            return

        # 3) Power-ups
        pu_target = self._find_nearest_powerup(powerups)
        if pu_target:
            self._behavior = self.BEHAVIOR_HUNT
            self._target_angle = math.atan2(pu_target[1] - hy, pu_target[0] - hx)
            self._smooth_turn(dt)
            super().update(dt)
            return

        # 4) Comer comida
        food_target = self._find_nearest_food(food_list)
        if food_target:
            self._behavior = self.BEHAVIOR_WANDER
            self._target_angle = math.atan2(food_target[1] - hy, food_target[0] - hx)
            self._smooth_turn(dt)
            super().update(dt)
            return

        # 5) Wandear
        if self._wander_target is None or self._wander_timer <= 0:
            self._wander_target = (
                random.uniform(200, WORLD_W - 200),
                random.uniform(200, WORLD_H - 200),
            )
            self._wander_timer = random.uniform(3, 8)

        tx, ty = self._wander_target
        self._target_angle = math.atan2(ty - hy, tx - hx)
        self._smooth_turn(dt)
        super().update(dt)

    def _smooth_turn(self, dt: float):
        """Gira gradualmente hacia _target_angle."""
        diff = (self._target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        max_turn = TURN_SPEED * dt * max(0.75, self.difficulty)
        if abs(diff) < max_turn:
            self.angle = self._target_angle
        else:
            self.angle += max_turn * (1 if diff > 0 else -1)

    def _find_danger(self, snakes: list) -> float | None:
        hx, hy = self.head.x, self.head.y

        for snake in snakes:
            if snake is self or not snake.alive:
                continue

            # Solo huir de serpientes BASTANTE más grandes (50% más)
            if snake.length > self.length * 1.5:
                dx = snake.head.x - hx
                dy = snake.head.y - hy
                d2 = dx * dx + dy * dy
                if d2 < AI_DANGER_RADIUS * AI_DANGER_RADIUS:
                    return math.atan2(dy, dx)

            # Cuerpo muy cercano de serpiente más grande => peligro
            if snake.length > self.length:
                for seg in snake.segments[3:]:
                    dx = seg.x - hx
                    dy = seg.y - hy
                    d2 = dx * dx + dy * dy
                    if d2 < (AI_DANGER_RADIUS * 0.4) ** 2:
                        return math.atan2(dy, dx)

        return None

    def _find_hunt_target(self, snakes: list) -> tuple[float, float] | None:
        """Busca la serpiente más pequeña cercana para cazar."""
        hx, hy = self.head.x, self.head.y
        best = None
        best_score = -1

        for snake in snakes:
            if snake is self or not snake.alive:
                continue
            # Solo cazar serpientes más chicas
            if snake.length >= self.length * 0.9:
                continue

            dx = snake.head.x - hx
            dy = snake.head.y - hy
            d2 = dx * dx + dy * dy

            if d2 > AI_SIGHT_RADIUS ** 2:
                continue

            # Priorizar: cerca y pequeña
            score = (1 / max(1, d2)) * 1e8 + (self.length - snake.length)
            if score > best_score:
                best_score = score
                best = (snake.head.x, snake.head.y)

        return best

    @staticmethod
    def _pos_of(obj):
        if obj is None:
            return None
        if isinstance(obj, tuple) and len(obj) >= 2:
            return obj[0], obj[1]
        if hasattr(obj, "x") and hasattr(obj, "y"):
            return obj.x, obj.y
        return None

    def _find_nearest_food(self, food_list) -> tuple[float, float] | None:
        hx, hy = self.head.x, self.head.y
        best = None
        best_d2 = AI_SIGHT_RADIUS ** 2

        for f in food_list:
            pos = self._pos_of(f)
            if pos is None:
                continue
            fx, fy = pos
            dx = fx - hx
            dy = fy - hy
            d2 = dx * dx + dy * dy
            if d2 < best_d2:
                best_d2 = d2
                best = (fx, fy)

        return best

    def _find_nearest_powerup(self, powerups) -> tuple[float, float] | None:
        hx, hy = self.head.x, self.head.y
        best = None
        best_d2 = (AI_SIGHT_RADIUS * 0.8) ** 2

        for pu in powerups:
            pos = self._pos_of(pu)
            if pos is None:
                continue
            px, py = pos
            dx = px - hx
            dy = py - hy
            d2 = dx * dx + dy * dy
            if d2 < best_d2:
                best_d2 = d2
                best = (px, py)

        return best