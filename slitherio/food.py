import random
from constants import *

# Paleta de colores vibrantes igual al juego original
FOOD_PALETTE = [
    (255,  80,  80),   # Rojo
    (255, 140,  40),   # Naranja
    (255, 220,  40),   # Amarillo
    ( 80, 255, 120),   # Verde claro
    ( 40, 210, 255),   # Celeste
    (120,  80, 255),   # Violeta
    (255,  80, 200),   # Rosa
    (255, 255, 100),   # Amarillo pálido
    ( 80, 255, 220),   # Turquesa
    (255, 120, 120),   # Salmón
    (180, 255,  80),   # Lima
    (255,  60, 140),   # Magenta
    (100, 200, 255),   # Azul claro
    (255, 180,  60),   # Ámbar
    (200,  80, 255),   # Púrpura
    ( 60, 255, 180),   # Menta
]

def random_color():
    """Devuelve un color aleatorio de la paleta."""
    return random.choice(FOOD_PALETTE)

def generate():
    """Genera comida aleatoria con colores variados."""
    return [
        (random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE), random_color())
        for _ in range(FOOD_COUNT)
    ]

def generate_single():
    """Genera una sola comida con color aleatorio."""
    return (random.randint(0, WORLD_W), random.randint(0, WORLD_H), random_color())

def generate_single_colored(color):
    """Genera una sola comida con un color específico (para drops de serpientes)."""
    return (random.randint(0, WORLD_W), random.randint(0, WORLD_H), color)