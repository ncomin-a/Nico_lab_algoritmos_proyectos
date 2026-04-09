import random
from settings import *

def generate():
    """Genera comida aleatoria en el mapa"""
    return [
        (random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE))
        for _ in range(FOOD_COUNT)
    ]

def generate_single():
    """Genera una sola comida en posición aleatoria"""
    return (random.randint(0, WORLD_SIZE), random.randint(0, WORLD_SIZE))