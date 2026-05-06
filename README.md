# Slither.io PRO

Juego tipo **Slither.io** hecho con **Python + Pygame**, con estética neon, bots con IA, cámara con zoom dinámico, ranking local y modo multijugador en pantalla dividida.

## Características

- Modo **un jugador vs IA**
- Modo **multijugador local** en pantalla dividida
- **Bots inteligentes** que buscan comida, huyen del peligro y pueden perseguir objetivos
- **Cámara suave** con zoom dinámico y efecto de temblor
- **Minimapa**, HUD, ranking en pantalla y estadísticas de partida
- **Partículas** y efectos visuales
- **Música de fondo**
- **Ranking local** guardado en `ranking.json`

## Requisitos

- Python 3.10 o superior
- `pygame`
- `Pillow` (opcional, mejora la carga de la imagen del menú)

Instalación:

```bash
pip install pygame pillow
```

## Cómo ejecutar

Desde la carpeta del proyecto:

```bash
python main.py
```

El archivo `main.py` abre la pantalla de inicio y desde ahí podés elegir entre jugar contra la IA o en multijugador local.

## Controles

### Un jugador
- **Moverse:** mouse
- **Boost:** click izquierdo

### Multijugador local
- **Jugador 1:** `W A S D`
- **Boost J1:** `Left Shift`
- **Jugador 2:** flechas `↑ ↓ ← →`
- **Boost J2:** `Right Shift`

## Objetivo del juego

Comé comida para crecer, evitá chocar contra otras serpientes y tratá de ser la más grande del mapa.  
Cuando una serpiente muere, suelta comida coloreada con su propio color.

## Estructura del proyecto

```text
main.py                 # punto de entrada del juego
pantalla de inicio.py   # menú principal y selección de modo
snake.py                # lógica de serpientes, jugador y bots
camera.py               # cámara con zoom, suavizado y temblor
food.py                 # generación de comida
ui.py                   # HUD, minimapa, ranking y pantallas auxiliares
particles.py            # sistema de partículas
ranking.py              # guardado y carga del ranking local
constants.py            # constantes globales del juego
musica_fondo.mp3        # música de fondo
imagenes/               # recursos visuales del menú
```

## Archivos de datos

- `ranking.json` se crea automáticamente para guardar los mejores puntajes.

## Notas

- El menú principal se carga desde `pantalla de inicio.py`, aunque el archivo tenga espacios en el nombre.
- Si no se encuentra la música o la imagen de fondo del menú, el juego sigue funcionando.
- El proyecto está pensado para jugarse en pantalla completa de ventana con resolución `1280x720`.

## Capturas y assets

El menú usa una imagen de fondo ubicada en:

```text
imagenes/pantalla de inicio Slither sin botones.png
```

## Licencia

Proyecto personal. Podés adaptar esta sección según lo que necesites.
