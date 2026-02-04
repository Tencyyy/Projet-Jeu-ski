import os
import math
import random
import pygame

ASSET_VERSION = "v9"


def _asset_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")


def ensure_assets():
    asset_dir = _asset_dir()
    os.makedirs(asset_dir, exist_ok=True)

    def save_asset(name, surf):
        path = os.path.join(asset_dir, name)
        pygame.image.save(surf, path)
        return path

    tile_dir = _asset_dir()

    # Skier frames (design plus clean)
    skier_paths = []
    suit_colors = [(210, 30, 30), (230, 50, 50), (200, 20, 20), (240, 70, 70)]
    for i, c in enumerate(suit_colors):
        surf = pygame.Surface((52, 64), pygame.SRCALPHA)
        ski_offset = (i % 2) * 2
        # skis (deux skis bien separes)
        pygame.draw.line(surf, (20, 20, 20), (4, 52 + ski_offset), (32, 52 + ski_offset), 5)
        pygame.draw.line(surf, (20, 20, 20), (28, 58 + ski_offset), (50, 58 + ski_offset), 5)
        pygame.draw.line(surf, (120, 120, 120), (6, 54 + ski_offset), (30, 54 + ski_offset), 2)
        pygame.draw.line(surf, (120, 120, 120), (30, 60 + ski_offset), (48, 60 + ski_offset), 2)
        # ombre
        pygame.draw.ellipse(surf, (0, 0, 0, 45), (12, 44, 30, 12))
        # corps / veste
        pygame.draw.ellipse(surf, c, (14, 18, 24, 30))
        pygame.draw.ellipse(surf, (180, 25, 25), (16, 20, 20, 12))
        pygame.draw.rect(surf, (255, 210, 60), (16, 32, 20, 5))
        # jambes
        pygame.draw.rect(surf, (30, 30, 40), (18, 42, 8, 8))
        pygame.draw.rect(surf, (30, 30, 40), (28, 42, 8, 8))
        # tete + casque
        pygame.draw.circle(surf, (255, 224, 200), (26, 14), 7)
        pygame.draw.rect(surf, (20, 40, 70), (19, 8, 14, 6), border_radius=2)
        pygame.draw.line(surf, (150, 190, 230), (20, 11), (32, 11), 1)
        pygame.draw.arc(surf, (30, 30, 30), (18, 6, 16, 14), math.pi, 2 * math.pi, 3)
        # batons (pousse vers l'arriere)
        pygame.draw.line(surf, (110, 90, 50), (16, 26), (6, 54), 2)
        pygame.draw.line(surf, (110, 90, 50), (36, 26), (46, 56), 2)
        pygame.draw.circle(surf, (60, 60, 60), (16, 26), 2)
        pygame.draw.circle(surf, (60, 60, 60), (36, 26), 2)
        skier_paths.append(save_asset(f"skier_{i}_{ASSET_VERSION}.png", surf))

    # Rock (3 variantes anguleuses)
    rock_paths = []
    rock_shapes = [
        [(4, 22), (10, 10), (24, 6), (38, 10), (42, 20), (32, 28), (18, 30), (8, 28)],
        [(6, 24), (14, 8), (28, 6), (40, 14), (40, 24), (30, 30), (16, 30), (6, 26)],
        [(4, 20), (12, 8), (26, 8), (38, 16), (42, 26), (28, 32), (12, 30), (6, 26)],
    ]
    for idx, main_poly in enumerate(rock_shapes):
        rock = pygame.Surface((46, 36), pygame.SRCALPHA)
        pygame.draw.polygon(rock, (60, 60, 70), main_poly)
        pygame.draw.polygon(rock, (40, 40, 50), [(main_poly[0][0] + 4, main_poly[0][1] - 2),
                                                 (main_poly[1][0] + 4, main_poly[1][1] + 2),
                                                 (main_poly[2][0] - 2, main_poly[2][1] + 4),
                                                 (main_poly[3][0] - 6, main_poly[3][1] + 6),
                                                 (main_poly[4][0] - 10, main_poly[4][1] + 4)])
        pygame.draw.polygon(rock, (110, 110, 120), [(main_poly[1][0] + 6, main_poly[1][1] + 2),
                                                    (main_poly[2][0] + 2, main_poly[2][1] + 6),
                                                    (main_poly[3][0] - 4, main_poly[3][1] + 6),
                                                    (main_poly[2][0] - 2, main_poly[2][1] + 2)])
        pygame.draw.polygon(rock, (30, 30, 40), main_poly, 1)
        rock_paths.append(save_asset(f"rock_{idx}_{ASSET_VERSION}.png", rock))

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

    # Drone drop (bloc de glace) plus gros
    drop = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.rect(drop, (180, 220, 255), (4, 6, 24, 18), border_radius=4)
    pygame.draw.rect(drop, (120, 180, 230), (8, 10, 16, 8), border_radius=3)
    pygame.draw.line(drop, (220, 240, 255), (8, 12), (22, 12), 1)
    pygame.draw.rect(drop, (80, 120, 170), (4, 6, 24, 18), 1, border_radius=4)
    drop_path = save_asset(f"drone_drop_{ASSET_VERSION}.png", drop)

    # Tree (plus details)
    tree = pygame.Surface((56, 84), pygame.SRCALPHA)
    pygame.draw.rect(tree, (90, 60, 30), (24, 60, 8, 18))
    pygame.draw.polygon(tree, (15, 105, 45), [(28, 8), (4, 46), (52, 46)])
    pygame.draw.polygon(tree, (25, 125, 55), [(28, 22), (2, 60), (54, 60)])
    pygame.draw.polygon(tree, (35, 145, 65), [(28, 38), (0, 76), (56, 76)])
    pygame.draw.circle(tree, (230, 240, 245), (20, 26), 3)
    pygame.draw.circle(tree, (230, 240, 245), (38, 34), 2)
    pygame.draw.line(tree, (10, 80, 35), (28, 12), (12, 42), 2)
    pygame.draw.line(tree, (20, 100, 45), (28, 26), (16, 58), 2)
    tree_path = save_asset(f"tree_{ASSET_VERSION}.png", tree)

    # Yeti (tiles)
    yeti_paths = []
    tile_yeti = ["tile_0078.png", "tile_0079.png", "tile_0080.png"]
    if all(os.path.exists(os.path.join(tile_dir, t)) for t in tile_yeti):
        yeti_paths = [os.path.join(tile_dir, t) for t in tile_yeti]
    else:
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
        yeti_paths = [save_asset(f"yeti_{ASSET_VERSION}.png", yeti)]

    # Background tile (piste de ski plus propre)
    bg = pygame.Surface((200, 200))
    for i in range(200):
        shade = 228 + int(18 * (i / 200))
        bg.fill((shade, shade + 6, 255), rect=pygame.Rect(0, i, 200, 1))

    # bandes damier plus fines
    for i in range(0, 200, 20):
        col = (236, 244, 255) if (i // 20) % 2 == 0 else (222, 232, 248)
        pygame.draw.rect(bg, col, (0, i, 200, 10))

    # traces de ski en S leger
    for x in range(-30, 230, 35):
        pygame.draw.line(bg, (210, 222, 238), (x, 0), (x + 70, 200), 2)
        pygame.draw.line(bg, (240, 248, 255), (x + 4, 0), (x + 74, 200), 1)

    random.seed(4)
    for _ in range(60):
        x = random.randint(0, 199)
        y = random.randint(0, 199)
        pygame.draw.circle(bg, (245, 250, 255), (x, y), random.randint(1, 2))
    bg_path = save_asset(f"bg_tile_{ASSET_VERSION}.png", bg)

    return {
        "skier": skier_paths,
        "rock": rock_paths,
        "bonus": bonus_path,
        "speed_boost": speed_boost_path,
        "drone": drone_path,
        "drop": drop_path,
        "tree": tree_path,
        "yeti": yeti_paths,
        "bg_tile": bg_path,
    }


def load_images(asset_paths):
    return {
        "skier": [pygame.image.load(p).convert_alpha() for p in asset_paths["skier"]],
        "rock": [pygame.image.load(p).convert_alpha() for p in asset_paths["rock"]],
        "bonus": pygame.image.load(asset_paths["bonus"]).convert_alpha(),
        "speed_boost": pygame.image.load(asset_paths["speed_boost"]).convert_alpha(),
        "drone": pygame.image.load(asset_paths["drone"]).convert_alpha(),
        "drop": pygame.image.load(asset_paths["drop"]).convert_alpha(),
        "tree": pygame.image.load(asset_paths["tree"]).convert_alpha(),
        "yeti": [pygame.image.load(p).convert_alpha() for p in asset_paths["yeti"]],
        "bg_tile": pygame.image.load(asset_paths["bg_tile"]).convert(),
    }
