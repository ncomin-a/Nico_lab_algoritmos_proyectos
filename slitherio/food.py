import random
from settings import *

def generate():
    return [(random.randint(0,WORLD_SIZE), random.randint(0,WORLD_SIZE)) for _ in range(FOOD_COUNT)]