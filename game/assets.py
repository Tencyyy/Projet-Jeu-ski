import os
import math
import random
import pygame

ASSET_VERSION = "v4"


def _asset_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")


def ensure_assets():
    asset_dir = _asset_dir()
    os.makedirs(asset_dir, exist_ok=True)

    def save_asset(name, surf):
        path = os.path.join(asset_dir, name)
        pygame.image.save(surf, path)
        return path

    # Skier frames
    skier_paths = []
    colors = [(220, 40, 40), (235, 70, 70), (200, 30, 30), (245, 90, 90)]
    for i, c in enumerate(colors):
        surf = pygame.Surface((44, 54), pygame.SRCALPHA)
        ski_offset = (i % 2) * 2
        # skis avec ombre
        pygame.draw.line(surf, (20, 20, 20), (2, 46 + ski_offset), (42, 44 - ski_offset), 5)
        pygame.draw.line(surf, (90, 90, 90), (4, 48 + ski_offset), (40, 46 - ski_offset), 2)
        # corps
        pygame.draw.ellipse(surf, c, (12, 14, 20, 24))
        pygame.draw.ellipse(surf, (170, 20, 20), (13, 16, 18, 10))
        pygame.draw.rect(surf, (250, 200, 40), (14, 24, 16, 4))
        pygame.draw.rect(surf, (250, 200, 40), (12, 26, 5, 8))
        # tete + masque
        pygame.draw.circle(surf, (255, 224, 200), (22, 12), 6)
        pygame.draw.arc(surf, (30, 30, 30), (15, 6, 14, 12), math.pi, 2 * math.pi, 3)
        pygame.draw.rect(surf, (40, 80, 120), (16, 10, 12, 6), border_radius=2)
        pygame.draw.line(surf, (120, 160, 200), (17, 12), (27, 12), 1)
        # batons
        pygame.draw.line(surf, (100, 80, 40), (8, 20), (4, 42), 2)
        pygame.draw.line(surf, (100, 80, 40), (36, 20), (40, 42), 2)
        skier_paths.append(save_asset(f"skier_{i}_{ASSET_VERSION}.png", surf))

    # Rock
    rock = pygame.Surface((34, 28), pygame.SRCALPHA)
    pygame.draw.ellipse(rock, (70, 70, 80), (1, 6, 32, 20))
    pygame.draw.ellipse(rock, (95, 95, 105), (6, 10, 14, 8))
    pygame.draw.ellipse(rock, (55, 55, 65), (16, 12, 12, 7))
    pygame.draw.ellipse(rock, (120, 120, 130), (18, 8, 10, 6))
    rock_path = save_asset(f"rock_{ASSET_VERSION}.png", rock)

    # Bonus (moonwalk)
    bonus = pygame.Surface((26, 26), pygame.SRCALPHA)
    pygame.draw.circle(bonus, (255, 210, 60), (13, 13), 12)
    pygame.draw.circle(bonus, (255, 240, 200), (10, 10), 4)
    pygame.draw.circle(bonus, (220, 170, 40), (16, 16), 7, 2)
    pygame.draw.arc(bonus, (150, 110, 20), (6, 6, 14, 14), math.pi, 2 * math.pi, 2)
    bonus_path = save_asset(f"bonus_{ASSET_VERSION}.png", bonus)

    # Speed boost (anneaux olympiques)
    speed_boost = pygame.Surface((48, 28), pygame.SRCALPHA)
    ring_colors = [
        (0, 133, 199),  # blue
        (0, 0, 0),      # black
        (227, 24, 55),  # red
        (244, 195, 0),  # yellow
        (0, 159, 61),   # green
    ]
    ring_centers = [(12, 10), (24, 10), (36, 10), (18, 18), (30, 18)]
    for color, center in zip(ring_colors, ring_centers):
        # petit contour clair pour mieux ressortir sur la neige
        pygame.draw.circle(speed_boost, (245, 245, 245), center, 7, 4)
        pygame.draw.circle(speed_boost, color, center, 7, 3)
    speed_boost_path = save_asset(f"speed_boost_{ASSET_VERSION}.png", speed_boost)

    # Drone
    drone = pygame.Surface((44, 20), pygame.SRCALPHA)
    pygame.draw.circle(drone, (35, 35, 35), (22, 10), 8)
    pygame.draw.circle(drone, (70, 70, 70), (22, 10), 8, 2)
    pygame.draw.line(drone, (110, 110, 110), (2, 10), (42, 10), 3)
    pygame.draw.circle(drone, (140, 140, 140), (6, 10), 3, 1)
    pygame.draw.circle(drone, (140, 140, 140), (38, 10), 3, 1)
    pygame.draw.circle(drone, (200, 40, 40), (22, 10), 2)
    drone_path = save_asset(f"drone_{ASSET_VERSION}.png", drone)

    # Drone drop
    drop = pygame.Surface((24, 24), pygame.SRCALPHA)
    pygame.draw.rect(drop, (50, 50, 50), (3, 5, 18, 14), border_radius=3)
    pygame.draw.rect(drop, (120, 120, 120), (6, 8, 12, 6), border_radius=2)
    pygame.draw.rect(drop, (30, 30, 30), (3, 5, 18, 14), 1, border_radius=3)
    drop_path = save_asset(f"drone_drop_{ASSET_VERSION}.png", drop)

    # Tree
    tree = pygame.Surface((52, 78), pygame.SRCALPHA)
    pygame.draw.rect(tree, (90, 60, 30), (22, 56, 8, 16))
    pygame.draw.polygon(tree, (15, 105, 45), [(26, 6), (4, 44), (48, 44)])
    pygame.draw.polygon(tree, (25, 125, 55), [(26, 20), (2, 58), (50, 58)])
    pygame.draw.polygon(tree, (35, 145, 65), [(26, 36), (0, 72), (52, 72)])
    pygame.draw.circle(tree, (230, 240, 245), (18, 24), 3)
    pygame.draw.circle(tree, (230, 240, 245), (36, 32), 2)
    tree_path = save_asset(f"tree_{ASSET_VERSION}.png", tree)

    # Yeti
    yeti = pygame.Surface((54, 72), pygame.SRCALPHA)
    pygame.draw.ellipse(yeti, (235, 235, 240), (4, 14, 46, 52))  # body
    pygame.draw.ellipse(yeti, (210, 210, 220), (10, 20, 34, 38))  # chest
    pygame.draw.circle(yeti, (235, 235, 240), (27, 12), 10)  # head
    pygame.draw.circle(yeti, (200, 200, 210), (22, 12), 4)  # left eye bg
    pygame.draw.circle(yeti, (200, 200, 210), (32, 12), 4)  # right eye bg
    pygame.draw.circle(yeti, (40, 40, 40), (22, 12), 2)  # left eye
    pygame.draw.circle(yeti, (40, 40, 40), (32, 12), 2)  # right eye
    pygame.draw.arc(yeti, (60, 60, 60), (20, 16, 14, 8), 0, math.pi, 2)  # mouth
    pygame.draw.rect(yeti, (180, 180, 190), (14, 46, 12, 18))  # legs
    pygame.draw.rect(yeti, (180, 180, 190), (28, 46, 12, 18))
    yeti_path = save_asset(f"yeti_{ASSET_VERSION}.png", yeti)

    # Background tile
    bg = pygame.Surface((200, 200))
    for i in range(200):
        shade = 228 + int(16 * (i / 200))
        bg.fill((shade, shade + 6, 255), rect=pygame.Rect(0, i, 200, 1))
    for i in range(0, 200, 14):
        shade = 235 + (i % 20)
        line_col = (shade, min(255, shade + 6), 255)
        pygame.draw.line(bg, line_col, (0, i), (200, i), 2)
    random.seed(4)
    for _ in range(90):
        x = random.randint(0, 199)
        y = random.randint(0, 199)
        pygame.draw.circle(bg, (245, 250, 255), (x, y), random.randint(1, 2))
    bg_path = save_asset(f"bg_tile_{ASSET_VERSION}.png", bg)

    return {
        "skier": skier_paths,
        "rock": rock_path,
        "bonus": bonus_path,
        "speed_boost": speed_boost_path,
        "drone": drone_path,
        "drop": drop_path,
        "tree": tree_path,
        "yeti": yeti_path,
        "bg_tile": bg_path,
    }


def load_images(asset_paths):
    return {
        "skier": [pygame.image.load(p).convert_alpha() for p in asset_paths["skier"]],
        "rock": pygame.image.load(asset_paths["rock"]).convert_alpha(),
        "bonus": pygame.image.load(asset_paths["bonus"]).convert_alpha(),
        "speed_boost": pygame.image.load(asset_paths["speed_boost"]).convert_alpha(),
        "drone": pygame.image.load(asset_paths["drone"]).convert_alpha(),
        "drop": pygame.image.load(asset_paths["drop"]).convert_alpha(),
        "tree": pygame.image.load(asset_paths["tree"]).convert_alpha(),
        "yeti": pygame.image.load(asset_paths["yeti"]).convert_alpha(),
        "bg_tile": pygame.image.load(asset_paths["bg_tile"]).convert(),
    }
