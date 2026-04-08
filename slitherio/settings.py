# 🎮 CONFIGURACIÓN DE PANTALLA
WIDTH = 1200
HEIGHT = 800
FPS = 60

# 🌍 CONFIGURACIÓN DEL MUNDO
WORLD_SIZE = 3000
WORLD_BORDER_COLOR = (40, 40, 40)

# 🐍 CONFIGURACIÓN DE SERPIENTES
INITIAL_MASS = 30  # 🆕 Aumentado de 20 para más equidad
SNAKE_SPEED = 2.5
BOOST_MULT = 1.8  # Multiplicador de velocidad al hacer boost
BOOST_COST = 0.05  # 🆕 Costo por frame de boost (más realista)
TURN_SPEED = 0.05  # Velocidad de rotación máxima

# 🍌 CONFIGURACIÓN DE COMIDA
FOOD_COUNT = 300  # 🆕 Aumentado de 200 para mejor gameplay
FOOD_SPAWN_RATE = 0.7  # 🆕 Regenerar comida cuando baja al 70%
FOOD_RADIUS = 3  # 🆕 Radio visual de la comida

# 🎯 CONFIGURACIÓN DE COLISIONES
COLLISION_DISTANCE = 10  # Distancia para detectar colisión con comida
THREAT_DISTANCE = 250  # Distancia a la que las IA detectan amenazas
MASS_ADVANTAGE = 1.15  # Cuánto más grande debe ser para ganar colisión

# 🎨 COLORES (RGB)
BACKGROUND_COLOR = (15, 15, 15)
FOOD_COLOR = (0, 255, 120)
GRID_COLOR = (30, 30, 30)

# 🎥 CONFIGURACIÓN DE CÁMARA
CAMERA_SMOOTHING = 0.08  # 🆕 Suavidad del movimiento (0-1)
CAMERA_ZOOM_MIN = 0.3   # 🆕 Zoom mínimo
CAMERA_ZOOM_MAX = 1.3   # 🆕 Zoom máximo
CAMERA_ZOOM_SPEED = 0.06  # 🆕 Velocidad de cambio de zoom

# ✨ CONFIGURACIÓN DE PARTÍCULAS
PARTICLE_LIFETIME = 30  # Frames que vive una partícula
PARTICLE_SIZE = 4  # Radio de una partícula
PARTICLE_FRICTION = 0.9  # Fricción de partículas (0-1)

# 🎮 CONFIGURACIÓN DE IA
AI_COUNT = 5  # Número de bots en el juego
AI_AGGRESSIVENESS = 0.6  # 🆕 Probabilidad de comportamiento agresivo (0-1)
AI_BOOST_THRESHOLD = 1.2  # 🆕 Multiplier de masa para decidir boost
AI_VISION_RANGE = 500  # 🆕 Rango de visión de IA

# 📊 CONFIGURACIÓN DE UI/HUD
HUD_FONT_SIZE = 28  # Tamaño de fuente principal
HUD_SMALL_FONT_SIZE = 20  # Tamaño de fuente pequeño
MINIMAP_SIZE = 200  # Tamaño del minimapa en píxeles
MINIMAP_POSITION = (WIDTH - MINIMAP_SIZE - 10, 10)  # 🆕 Posición del minimapa

# 🏆 CONFIGURACIÓN DE RANKING
RANKING_FILE = "ranking.json"
TOP_SCORES = 10  # 🆕 Número de scores a guardar
MIN_SCORE_SAVE = 0  # ���� Puntuación mínima para guardar

# 🎛️ BALANCE Y DIFICULTAD
# Ajusta estos valores para cambiar la dificultad
DIFFICULTY = "normal"  # 🆕 "easy", "normal", "hard"

if DIFFICULTY == "easy":
    INITIAL_MASS = 50
    FOOD_COUNT = 500
    SNAKE_SPEED = 3.0
    AI_AGGRESSIVENESS = 0.3
    THREAT_DISTANCE = 150

elif DIFFICULTY == "hard":
    INITIAL_MASS = 15
    FOOD_COUNT = 150
    SNAKE_SPEED = 2.0
    AI_AGGRESSIVENESS = 0.9
    THREAT_DISTANCE = 400
    AI_BOOST_THRESHOLD = 1.0

# 🆕 CONSTANTES DERIVADAS (calculadas automáticamente)
ASPECT_RATIO = WIDTH / HEIGHT
CAMERA_MIN_ZOOM = 1 / (WORLD_SIZE / WIDTH)