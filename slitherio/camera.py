from constants import WIDTH, HEIGHT, WORLD_SIZE
import math

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1
        self.velocity_x = 0  # 🆕 Velocidad de cámara para suavizado avanzado
        self.velocity_y = 0
        self.shake = 0  # 🆕 Efecto de temblor

    def update(self, target, mass, screen_width=WIDTH):
        """
        Actualiza la cámara con zoom dinámico y suavizado avanzado
        
        Args:
            target: tupla (x, y) posición del objetivo
            mass: masa del objetivo para cálculo de zoom
            screen_width: ancho de la pantalla para centrar (para splitscreen)
        """
        # 🎯 ZOOM DINÁMICO mejorado
        # Rango: 0.3x (serpiente grande) a 1.3x (serpiente pequeña)
        target_zoom = max(0.3, min(1.3, 50 / (mass + 1)))
        
        # Suavizado exponencial del zoom
        zoom_diff = target_zoom - self.zoom
        self.zoom += zoom_diff * 0.06  # Ligeramente más rápido que antes

        # 🎯 POSICIÓN OBJETIVO (centrar jugador)
        target_x = target[0] - (screen_width / 2) / self.zoom
        target_y = target[1] - (HEIGHT / 2) / self.zoom

        # 🆕 SUAVIZADO DE CÁMARA con EASING (más natural)
        # Usar velocidad para movimiento más fluido
        dx = target_x - self.x
        dy = target_y - self.y
        
        # Aplicar fricción y aceleración
        self.velocity_x += dx * 0.08
        self.velocity_y += dy * 0.08
        
        # Fricción para suavidad
        self.velocity_x *= 0.92
        self.velocity_y *= 0.92
        
        self.x += self.velocity_x
        self.y += self.velocity_y

        # 🆕 Limitar la cámara dentro del mundo (opcional)
        self._clamp_camera()

        # 🆕 Aplicar temblor si está activo
        if self.shake > 0:
            self.shake -= 1

    def apply(self, pos):
        """
        Convierte coordenadas del mundo → pantalla
        Incluye efecto de temblor si está activo
        
        Args:
            pos: tupla (x, y) posición en el mundo
            
        Returns:
            tupla (x, y) posición en la pantalla
        """
        x = (pos[0] - self.x) * self.zoom
        y = (pos[1] - self.y) * self.zoom
        
        # 🆕 Aplicar temblor de cámara
        if self.shake > 0:
            import random
            shake_amount = self.shake * 0.5
            x += random.uniform(-shake_amount, shake_amount)
            y += random.uniform(-shake_amount, shake_amount)
        
        return x, y

    def screen_to_world(self, pos):
        """
        Convierte mouse (pantalla) → mundo
        
        Args:
            pos: tupla (x, y) posición en pantalla
            
        Returns:
            tupla (x, y) posición en el mundo
        """
        x = pos[0] / self.zoom + self.x
        y = pos[1] / self.zoom + self.y
        return x, y

    def _clamp_camera(self):
        """
        🆕 Limita la cámara para que no vea fuera del mundo
        Evita que se vea un fondo negro en los bordes
        """
        margin = 200 / self.zoom
        
        self.x = max(-margin, min(self.x, WORLD_SIZE + margin))
        self.y = max(-margin, min(self.y, WORLD_SIZE + margin))
        self.y = max(-margin, min(self.y, WORLD_SIZE + margin))

    def shake_camera(self, intensity=5):
        """
        🆕 Activa efecto de temblor de cámara
        Útil para impactos y eventos importantes
        
        Args:
            intensity: intensidad del temblor (1-10)
        """
        self.shake = max(self.shake, intensity)

    def get_visible_rect(self):
        """
        🆕 Retorna el rectángulo visible del mundo
        Útil para optimizar renderizado
        
        Returns:
            tupla (x1, y1, x2, y2) coordenadas visibles del mundo
        """
        x1 = self.x
        y1 = self.y
        x2 = self.x + (WIDTH / self.zoom)
        y2 = self.y + (HEIGHT / self.zoom)
        
        return (x1, y1, x2, y2)

    def is_visible(self, pos, radius=10):
        """
        🆕 Verifica si un objeto es visible en pantalla
        
        Args:
            pos: tupla (x, y) posición del objeto
            radius: radio del objeto
            
        Returns:
            bool: True si es visible
        """
        x1, y1, x2, y2 = self.get_visible_rect()
        
        return (
            pos[0] + radius > x1 and
            pos[0] - radius < x2 and
            pos[1] + radius > y1 and
            pos[1] - radius < y2
        )

    def zoom_to_box(self, positions, padding=100):
        """
        🆕 Ajusta el zoom para ver múltiples objetos
        
        Args:
            positions: lista de tuplas (x, y)
            padding: espacio adicional alrededor
        """
        if not positions:
            return
        
        min_x = min(p[0] for p in positions)
        max_x = max(p[0] for p in positions)
        min_y = min(p[1] for p in positions)
        max_y = max(p[1] for p in positions)
        
        width = max_x - min_x + padding * 2
        height = max_y - min_y + padding * 2
        
        # Calcular zoom necesario
        zoom_x = WIDTH / width if width > 0 else 1
        zoom_y = HEIGHT / height if height > 0 else 1
        
        target_zoom = min(zoom_x, zoom_y, 1.5)
        target_zoom = max(0.3, target_zoom)
        
        # Centrar en la caja
        self.x = (min_x + max_x) / 2 - (WIDTH / 2) / self.zoom
        self.y = (min_y + max_y) / 2 - (HEIGHT / 2) / self.zoom
        self.zoom = target_zoom

    def __repr__(self):
        """🆕 Para debugging"""
        return f"Camera(x={self.x:.1f}, y={self.y:.1f}, zoom={self.zoom:.2f}, shake={self.shake})"