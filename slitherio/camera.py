from settings import WIDTH, HEIGHT

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1

    def update(self, target, mass):
        # 🎯 ZOOM DINÁMICO
        target_zoom = max(0.4, min(1.2, 50 / (mass + 1)))
        self.zoom += (target_zoom - self.zoom) * 0.05  # suavizado zoom

        # 🎯 POSICIÓN OBJETIVO (centrar jugador)
        target_x = target[0] - (WIDTH / 2) / self.zoom
        target_y = target[1] - (HEIGHT / 2) / self.zoom

        # 🎯 SUAVIZADO DE CÁMARA (muy importante)
        self.x += (target_x - self.x) * 0.1
        self.y += (target_y - self.y) * 0.1

    def apply(self, pos):
        # 🌍 convierte coordenadas del mundo → pantalla
        x = (pos[0] - self.x) * self.zoom
        y = (pos[1] - self.y) * self.zoom
        return x, y

    def screen_to_world(self, pos):
        # 🖱 convierte mouse (pantalla) → mundo
        x = pos[0] / self.zoom + self.x
        y = pos[1] / self.zoom + self.y
        return x, y