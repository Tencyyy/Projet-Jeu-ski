# Configuration globale du jeu
import pygame

# Dimensions de la fenêtre
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60

# Mode d'affichage
FULLSCREEN = True  # Changer en True pour le plein écran
# Si FULLSCREEN = True, le jeu s'adaptera à la résolution de votre écran

# Options d'affichage (utilisées dans le menu Options)
WINDOW_PRESETS = [
    ("PLEIN ECRAN", None),
    ("GRAND", (1440, 960)),
    ("MOYEN", (960, 640)),
    ("PETIT", (720, 480)),
]

# Volume par défaut (0.0 à 1.0)
DEFAULT_VOLUME = 0.6

# Titre du jeu
GAME_TITLE = "JO d'hiver 2026 - Ski Runner"

# Polices
FONT_NAME = "arial"
FONT_SIZE_SMALL = 20
FONT_SIZE_MEDIUM = 36
FONT_SIZE_LARGE = 42

# Couleurs
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_BLUE_SKY = (228, 234, 255)
COLOR_SNOW = (245, 250, 255)
COLOR_MENU_BG = (242, 246, 255)
COLOR_MENU_BORDER = (210, 225, 240)
COLOR_BUTTON_PRIMARY = (20, 120, 200)
COLOR_BUTTON_SECONDARY = (70, 90, 110)
COLOR_TEXT_DARK = (30, 40, 60)
COLOR_TEXT_LIGHT = (235, 245, 255)
COLOR_OVERLAY = (15, 20, 30, 140)

# Temps limites pour les modes
CURLING_TIME_LIMIT = 12.0
BIATHLON_TIME_LIMIT = 20.0

# Configuration des niveaux
LEVEL_SETTINGS = {
    1: {
        "speed_base": 130,
        "max_speed": 230,
        "min_gap": 1.8,
        "gate_range": (1.7, 2.6),
        "extra_gate": 0.0,
        "bonus_range": (4.2, 6.5),
        "finish_score": 100,
        "finish_time": 25.0,
        "distance_m": 100
    },
    2: {
        "speed_base": 140,
        "max_speed": 245,
        "min_gap": 1.6,
        "gate_range": (1.6, 2.3),
        "extra_gate": 0.1,
        "bonus_range": (3.8, 6.0),
        "finish_score": 140,
        "finish_time": 24.0,
        "distance_m": 120
    },
    3: {
        "speed_base": 150,
        "max_speed": 260,
        "min_gap": 1.45,
        "gate_range": (1.4, 2.1),
        "extra_gate": 0.2,
        "bonus_range": (3.3, 5.5),
        "finish_score": 180,
        "finish_time": 23.0,
        "distance_m": 140
    },
    4: {
        "speed_base": 160,
        "max_speed": 275,
        "min_gap": 1.3,
        "gate_range": (1.3, 2.0),
        "extra_gate": 0.3,
        "bonus_range": (2.9, 5.0),
        "finish_score": 220,
        "finish_time": 22.0,
        "distance_m": 160
    },
    5: {
        "speed_base": 170,
        "max_speed": 295,
        "min_gap": 1.15,
        "gate_range": (1.2, 1.8),
        "extra_gate": 0.4,
        "bonus_range": (2.5, 4.6),
        "finish_score": 260,
        "finish_time": 21.0,
        "distance_m": 180
    }
}
