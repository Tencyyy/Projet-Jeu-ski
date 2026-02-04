import random
import os
import math
import pygame

# support execution as script (python game/main.py)
try:
    from .assets import ensure_assets, load_images
    from .audio import build_audio, play_sfx
    from .entities import Player, Obstacle, Gate, Bonus, Drone, Yeti
except ImportError:  # fallback when not run as a package
    from assets import ensure_assets, load_images
    from audio import build_audio, play_sfx
    from entities import Player, Obstacle, Gate, Bonus, Drone, Yeti


def reset_game(screen_w, screen_h, images, level=1):
    # ca c'est pour remettre tout a zero quand on recommence
    player = Player(0, screen_h // 2, images["skier"])
    player.x = screen_w // 2 - player.w // 2
    drone = Drone(screen_w // 2, images["drone"])
    yeti_count = 0
    if level >= 2:
        yeti_count = 1
    if level >= 3:
        yeti_count = 2
    yetis = []
    for i in range(yeti_count):
        x = (screen_w // 2) + (i * 80) - (40 * (yeti_count - 1))
        yetis.append(Yeti(x, screen_h + 140 + i * 60, images["yeti"]))

    return {
        "player": player,
        "drone": drone,
        "yetis": yetis,
        "yeti_active": level >= 2,
        "obstacles": [],
        "gates": [],
        "bonuses": [],
        "bg_offset": 0.0,
        "score": 0,
        "level": level,
        "speed": 130,
        "max_speed": 260,
        "spawn_timer": 0.0,
        "bonus_timer": 2.5,
        "gate_timer": 1.8,
        "race_time": 0.0,
        "finish_time": 25.0,
        "finish_score": 100,
        "distance_left": 0.0,
        "distance_total": 0.0,
        "distance_scale": 0.0,
        "race_time_end": None,
        "final_done": False,
        "finish_passed": False,
        "finish_line": None,
        "win": False,
        "particles": [],
        "snowflakes": [],
    }


def draw_background(screen, bg_tile, offset):
    # ca fonction est de dessiner le fond qui defile en boucle
    screen_w, screen_h = screen.get_size()
    tile_w = bg_tile.get_width()
    tile_h = bg_tile.get_height()
    y = -tile_h + int(offset % tile_h)
    while y < screen_h:
        x = 0
        while x < screen_w:
            screen.blit(bg_tile, (x, y))
            x += tile_w
        y += tile_h


def main():
    # ca c'est pour initialiser pygame + la fenetre
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    screen_w, screen_h = 960, 640
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("JO d'hiver 2026 - Ski Runner")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("arial", 20)
    big_font = pygame.font.SysFont("arial", 36)
    title_font = pygame.font.SysFont("arial", 42, bold=True)
    curling_time_limit = 12.0
    biathlon_time_limit = 20.0

    # ca c'est pour charger images et sons
    asset_paths = ensure_assets()
    images = load_images(asset_paths)
    audio = build_audio()

    state = "splash"
    paused = False
    game_over = False
    name_input = ""
    leaderboard = []
    pending_score = None
    pending_time = None
    mode = "jo"
    resume_available = False
    splash_timer = 0.0
    splash_image = None
    curling_data = None
    biathlon_data = None
    menu_choice = 0  # 0 triathlon, 1 entrainement
    training_choice = 0  # 0 course, 1 curling, 2 biathlon, 3 retour

    splash_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "24.10.24-Milano-Cortina-1.webp")
    if os.path.exists(splash_path):
        try:
            splash_image = pygame.image.load(splash_path).convert()
            splash_image = pygame.transform.smoothscale(splash_image, (screen_w, screen_h))
        except pygame.error:
            splash_image = None

    level_settings = {
        1: {"speed_base": 130, "max_speed": 230, "min_gap": 1.8, "gate_range": (1.7, 2.6), "extra_gate": 0.0, "bonus_range": (4.2, 6.5), "finish_score": 100, "finish_time": 25.0, "distance_m": 100},
        2: {"speed_base": 140, "max_speed": 245, "min_gap": 1.6, "gate_range": (1.6, 2.3), "extra_gate": 0.1, "bonus_range": (3.8, 6.0), "finish_score": 140, "finish_time": 24.0, "distance_m": 120},
        3: {"speed_base": 150, "max_speed": 260, "min_gap": 1.45, "gate_range": (1.4, 2.1), "extra_gate": 0.2, "bonus_range": (3.3, 5.5), "finish_score": 180, "finish_time": 23.0, "distance_m": 140},
        4: {"speed_base": 160, "max_speed": 275, "min_gap": 1.3, "gate_range": (1.3, 2.0), "extra_gate": 0.3, "bonus_range": (2.9, 5.0), "finish_score": 220, "finish_time": 22.0, "distance_m": 160},
        5: {"speed_base": 170, "max_speed": 295, "min_gap": 1.15, "gate_range": (1.2, 1.8), "extra_gate": 0.4, "bonus_range": (2.5, 4.6), "finish_score": 260, "finish_time": 21.0, "distance_m": 180},
    }

    def apply_level_settings(current):
        level_cfg = level_settings.get(current["level"], level_settings[5])
        current["max_speed"] = level_cfg["max_speed"]
        current["speed"] = min(current["max_speed"], level_cfg["speed_base"])
        gate_min, gate_max = level_cfg["gate_range"]
        current["gate_timer"] = random.uniform(gate_min, gate_max)
        current["bonus_timer"] = random.uniform(*level_cfg["bonus_range"])
        current["finish_score"] = level_cfg["finish_score"]
        current["finish_time"] = level_cfg["finish_time"]
        current["distance_total"] = level_cfg["distance_m"]
        denom = max(1.0, level_cfg["finish_time"] * level_cfg["speed_base"])
        current["distance_scale"] = level_cfg["distance_m"] / denom
        current["distance_left"] = level_cfg["distance_m"]

    def format_time(seconds):
        if seconds is None:
            return "-"
        total = max(0.0, float(seconds))
        minutes = int(total // 60)
        secs = total - minutes * 60
        return f"{minutes}:{secs:04.1f}"

    def add_leaderboard(score, time_val):
        # ca c'est pour enregistrer le classement seulement a la fin du mode JO
        nonlocal pending_score, pending_time
        if mode != "jo" or not data.get("final_done"):
            return
        if name_input.strip() == "":
            pending_score = score
            pending_time = time_val
            return
        leaderboard.append((score, name_input.strip(), time_val))
        leaderboard.sort(key=lambda x: x[0], reverse=True)
        leaderboard[:] = leaderboard[:5]
        pending_score = None
        pending_time = None

    data = reset_game(screen_w, screen_h, images, 1)
    apply_level_settings(data)

    # decor: montagnes + vignette (cache un peu le cote "cheap")
    mountain_layer = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    pygame.draw.polygon(mountain_layer, (200, 215, 230, 140), [(0, 420), (120, 260), (260, 420)])
    pygame.draw.polygon(mountain_layer, (190, 205, 220, 120), [(200, 430), (360, 240), (520, 430)])
    pygame.draw.polygon(mountain_layer, (180, 195, 210, 110), [(420, 440), (600, 260), (780, 440)])
    pygame.draw.circle(mountain_layer, (255, 245, 210, 120), (680, 120), 50)

    vignette = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    pygame.draw.rect(vignette, (0, 0, 0, 0), (0, 0, screen_w, screen_h))
    pygame.draw.rect(vignette, (10, 20, 30, 70), (0, 0, screen_w, screen_h), 40)

    # neige fine en overlay
    grain = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    random.seed(7)
    for _ in range(240):
        x = random.randint(0, screen_w - 1)
        y = random.randint(0, screen_h - 1)
        r = random.choice([1, 1, 2])
        alpha = random.randint(30, 80)
        pygame.draw.circle(grain, (255, 255, 255, alpha), (x, y), r)

    # ca c'est pour la boucle principale du jeu
    while True:
        dt = clock.tick(60) / 1000.0
        # boutons (positions calculees au rendu)
        btn_triathlon = pygame.Rect(0, 0, 0, 0)
        btn_training = pygame.Rect(0, 0, 0, 0)
        btn_train_course = pygame.Rect(0, 0, 0, 0)
        btn_train_curling = pygame.Rect(0, 0, 0, 0)
        btn_train_biathlon = pygame.Rect(0, 0, 0, 0)
        btn_train_back = pygame.Rect(0, 0, 0, 0)

        # ca c'est pour gerer les evenements clavier / fermer la fenetre
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if state == "splash":
                    state = "menu"
                elif state == "menu":
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        menu_choice = 1 - menu_choice
                    if event.key == pygame.K_RETURN:
                        if menu_choice == 0:
                            if name_input.strip() == "":
                                mode = "jo"
                                state = "name_entry"
                            else:
                                mode = "jo"
                                state = "playing"
                                paused = False
                                game_over = False
                                pending_score = None
                                pending_time = None
                                data = reset_game(screen_w, screen_h, images, 1)
                                apply_level_settings(data)
                                resume_available = False
                                if audio["menu_music"]:
                                    audio["menu_music"].stop()
                                if audio["game_music"]:
                                    audio["game_music"].play(loops=-1)
                        else:
                            mode = "training"
                            state = "training_menu"
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    else:
                        nav_keys = {
                            pygame.K_LEFT,
                            pygame.K_RIGHT,
                            pygame.K_UP,
                            pygame.K_DOWN,
                            pygame.K_RETURN,
                            pygame.K_ESCAPE,
                            pygame.K_SPACE,
                        }
                        if event.key not in nav_keys and event.unicode.isprintable() and len(name_input) < 12:
                            name_input += event.unicode
                            state = "name_entry"
                elif state == "playing":
                    if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                        paused = not paused
                        play_sfx(audio["sfx"], "pause" if paused else "resume")
                    if event.key == pygame.K_ESCAPE:
                        state = "menu"
                        paused = False
                        game_over = False
                        data = reset_game(screen_w, screen_h, images, 1)
                        apply_level_settings(data)
                        resume_available = False
                        if audio["game_music"]:
                            audio["game_music"].stop()
                        if audio["menu_music"]:
                            audio["menu_music"].play(loops=-1)
                elif state == "game_over":
                    if event.key == pygame.K_r:
                        state = "playing"
                        paused = False
                        game_over = False
                        pending_score = None
                        pending_time = None
                        data = reset_game(screen_w, screen_h, images, data["level"])
                        apply_level_settings(data)
                        resume_available = False
                        if audio["menu_music"]:
                            audio["menu_music"].stop()
                        if audio["game_music"]:
                            audio["game_music"].play(loops=-1)
                    if event.key == pygame.K_RETURN:
                        if mode == "jo" and data.get("final_done") and pending_score is not None and name_input.strip() == "":
                            state = "name_entry"
                        else:
                            if not data.get("win"):
                                state = "playing"
                                paused = False
                                game_over = False
                                pending_score = None
                                pending_time = None
                                data = reset_game(screen_w, screen_h, images, data["level"])
                                apply_level_settings(data)
                                resume_available = False
                                if audio["menu_music"]:
                                    audio["menu_music"].stop()
                                if audio["game_music"]:
                                    audio["game_music"].play(loops=-1)
                            elif data.get("win") and data["level"] < 5:
                                state = "playing"
                                paused = False
                                game_over = False
                                pending_score = None
                                pending_time = None
                                data = reset_game(screen_w, screen_h, images, data["level"] + 1)
                                apply_level_settings(data)
                                resume_available = False
                                if audio["menu_music"]:
                                    audio["menu_music"].stop()
                                if audio["game_music"]:
                                    audio["game_music"].play(loops=-1)
                            else:
                                state = "menu"
                                if audio["game_music"]:
                                    audio["game_music"].stop()
                                if audio["menu_music"]:
                                    audio["menu_music"].play(loops=-1)
                elif state == "name_entry":
                    if event.key == pygame.K_RETURN:
                        if name_input.strip() != "":
                            if pending_score is not None:
                                add_leaderboard(pending_score, pending_time)
                                state = "game_over"
                            else:
                                state = "playing"
                                paused = False
                                game_over = False
                                pending_score = None
                                pending_time = None
                                data = reset_game(screen_w, screen_h, images, 1)
                                apply_level_settings(data)
                                resume_available = False
                                if audio["menu_music"]:
                                    audio["menu_music"].stop()
                                if audio["game_music"]:
                                    audio["game_music"].play(loops=-1)
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    else:
                        if event.unicode.isprintable() and len(name_input) < 12:
                            name_input += event.unicode
                elif state == "curling":
                    if event.key == pygame.K_SPACE and curling_data and not curling_data["shot"]:
                        curling_data["shot"] = True
                        curling_data["vx"] = 0.0
                        power = curling_data.get("power", 50)
                        curling_data["vy"] = -(220.0 + power * 1.2)
                        curling_data["throw_t"] = 0.0
                        play_sfx(audio["sfx"], "curling_slide")
                    if event.key == pygame.K_RETURN and curling_data and curling_data["done"]:
                        if curling_data["round"] < curling_data["max_rounds"]:
                            curling_data["round"] += 1
                            curling_data["shot"] = False
                            curling_data["done"] = False
                            curling_data["x"] = screen_w // 2
                            curling_data["y"] = screen_h - 120
                            curling_data["vy"] = 0.0
                            curling_data["power"] = 0.0
                            curling_data["p_dir"] = 1.0
                            curling_data["throw_t"] = 0.0
                            curling_data["time_left"] = curling_data.get("time_limit", curling_time_limit)
                        else:
                            state = "playing"
                            paused = False
                            game_over = False
                            pending_score = None
                            pending_time = None
                            data = reset_game(screen_w, screen_h, images, 5)
                            apply_level_settings(data)
                            if audio["menu_music"]:
                                audio["menu_music"].stop()
                            if audio["game_music"]:
                                audio["game_music"].play(loops=-1)
                elif state == "biathlon":
                    if biathlon_data is None or "phase" not in biathlon_data:
                        biathlon_data = {
                            "phase": "aim",
                            "shots": 0,
                            "shots_total": 3,
                            "hits": 0,
                            "total_hits": 0,
                            "scored": False,
                            "power": 0.0,
                            "p_dir": 1.0,
                            "round": 1,
                            "max_rounds": 2,
                            "done": False,
                            "target_x": 560.0,
                            "target_y": 230.0,
                            "t_dirx": 1.0,
                            "t_diry": 1.0,
                            "wind": random.uniform(-12.0, 12.0),
                            "aim_x": None,
                            "aim_y": None,
                            "shot_fx": 0.0,
                            "shot_x": None,
                            "shot_y": None,
                            "shot_hit": False,
                            "shot_from": (310, 356),
                            "shot_marks": [],
                            "time_left": biathlon_time_limit,
                            "time_limit": biathlon_time_limit,
                        }
                    if event.key == pygame.K_SPACE and biathlon_data and not biathlon_data["done"]:
                        if biathlon_data["phase"] == "aim":
                            biathlon_data["phase"] = "power"
                            biathlon_data["aim_x"] = biathlon_data["target_x"]
                            biathlon_data["aim_y"] = biathlon_data["target_y"]
                        else:
                            aim_x = biathlon_data.get("aim_x", screen_w // 2)
                            aim_y = biathlon_data.get("aim_y", 320)
                            power = biathlon_data.get("power", 50)
                            wind = biathlon_data.get("wind", 0.0)
                            dx = (biathlon_data["target_x"] - (aim_x + wind * 0.8))
                            dy = (biathlon_data["target_y"] - aim_y)
                            dist = (dx * dx + dy * dy) ** 0.5
                            tol = 18 + int(power * 0.08)
                            hit = dist < tol
                            if hit:
                                biathlon_data["hits"] += 1
                            play_sfx(audio["sfx"], "arrow_shot")
                            shot_x = aim_x + wind * 0.8
                            shot_y = aim_y
                            biathlon_data["shot_fx"] = 0.25
                            biathlon_data["shot_x"] = shot_x
                            biathlon_data["shot_y"] = shot_y
                            biathlon_data["shot_hit"] = hit
                            marks = biathlon_data.get("shot_marks", [])
                            marks.append((shot_x, shot_y, hit))
                            if len(marks) > biathlon_data["shots_total"]:
                                marks = marks[-biathlon_data["shots_total"] :]
                            biathlon_data["shot_marks"] = marks
                            biathlon_data["shots"] += 1
                            biathlon_data["phase"] = "aim"
                            biathlon_data["power"] = 0.0
                            biathlon_data["p_dir"] = 1.0
                            biathlon_data["wind"] = random.uniform(-12.0, 12.0)
                            biathlon_data["aim_x"] = None
                            biathlon_data["aim_y"] = None
                            if biathlon_data["shots"] >= biathlon_data["shots_total"]:
                                biathlon_data["done"] = True
                    if event.key == pygame.K_RETURN and biathlon_data and biathlon_data["done"]:
                        if biathlon_data["round"] < biathlon_data["max_rounds"]:
                            biathlon_data["round"] += 1
                            biathlon_data["done"] = False
                            biathlon_data["scored"] = False
                            biathlon_data["hits"] = 0
                            biathlon_data["power"] = 0.0
                            biathlon_data["p_dir"] = 1.0
                            biathlon_data["phase"] = "aim"
                            biathlon_data["shots"] = 0
                            biathlon_data["wind"] = random.uniform(-12.0, 12.0)
                            biathlon_data["shot_fx"] = 0.0
                            biathlon_data["shot_x"] = None
                            biathlon_data["shot_y"] = None
                            biathlon_data["shot_hit"] = False
                            biathlon_data["shot_marks"] = []
                            biathlon_data["time_left"] = biathlon_data.get("time_limit", biathlon_time_limit)
                        else:
                            game_over = True
                            state = "game_over"
                            data["win"] = True
                            data["final_done"] = True
                            add_leaderboard(data["score"], data.get("race_time_end"))
                elif state == "training_menu":
                    if event.key == pygame.K_UP:
                        training_choice = (training_choice - 1) % 4
                    if event.key == pygame.K_DOWN:
                        training_choice = (training_choice + 1) % 4
                    if event.key == pygame.K_RETURN:
                        if training_choice == 0:
                            mode = "training"
                            state = "playing"
                            paused = False
                            game_over = False
                            pending_score = None
                            pending_time = None
                            data = reset_game(screen_w, screen_h, images, 1)
                            apply_level_settings(data)
                            if audio["menu_music"]:
                                audio["menu_music"].stop()
                            if audio["game_music"]:
                                audio["game_music"].play(loops=-1)
                        elif training_choice == 1:
                            mode = "training"
                            state = "curling"
                            curling_data = {
                                "x": screen_w // 2,
                                "y": screen_h - 120,
                                "vx": 0.0,
                                "vy": 0.0,
                                "shot": False,
                                "done": False,
                                "power": 0.0,
                                "p_dir": 1.0,
                                "round": 1,
                                "max_rounds": 2,
                                "bonus_total": 0,
                                "throw_t": 0.0,
                                "time_left": curling_time_limit,
                                "time_limit": curling_time_limit,
                            }
                        elif training_choice == 2:
                            mode = "training"
                            state = "biathlon"
                            biathlon_data = {
                                "cross_x": 120.0,
                                "dir": 1.0,
                                "idx": 0,
                                "hits": 0,
                                "total_hits": 0,
                                "targets": [200, 320, 440],
                                "scored": False,
                                "power": 0.0,
                                "p_dir": 1.0,
                                "round": 1,
                                "max_rounds": 2,
                                "done": False,
                            }
                        else:
                            state = "menu"
                    if event.key == pygame.K_ESCAPE:
                        state = "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if state == "menu":
                    if btn_triathlon.collidepoint(mx, my):
                        if name_input.strip() == "":
                            mode = "jo"
                            state = "name_entry"
                        else:
                            mode = "jo"
                            state = "playing"
                            paused = False
                            game_over = False
                            pending_score = None
                            pending_time = None
                            data = reset_game(screen_w, screen_h, images, 1)
                            apply_level_settings(data)
                            if audio["menu_music"]:
                                audio["menu_music"].stop()
                            if audio["game_music"]:
                                audio["game_music"].play(loops=-1)
                    if btn_training.collidepoint(mx, my):
                        mode = "training"
                        state = "training_menu"
                elif state == "training_menu":
                    if btn_train_course.collidepoint(mx, my):
                        mode = "training"
                        state = "playing"
                        paused = False
                        game_over = False
                        pending_score = None
                        pending_time = None
                        data = reset_game(screen_w, screen_h, images, 1)
                        apply_level_settings(data)
                        if audio["menu_music"]:
                            audio["menu_music"].stop()
                        if audio["game_music"]:
                            audio["game_music"].play(loops=-1)
                    if btn_train_curling.collidepoint(mx, my):
                        mode = "training"
                        state = "curling"
                        curling_data = {
                            "x": screen_w // 2,
                            "y": screen_h - 120,
                            "vx": 0.0,
                            "vy": 0.0,
                            "shot": False,
                            "done": False,
                            "power": 0.0,
                            "p_dir": 1.0,
                            "round": 1,
                            "max_rounds": 2,
                            "bonus_total": 0,
                            "throw_t": 0.0,
                            "time_left": curling_time_limit,
                            "time_limit": curling_time_limit,
                        }
                    if btn_train_biathlon.collidepoint(mx, my):
                        mode = "training"
                        state = "biathlon"
                        biathlon_data = {
                            "phase": "aim",
                            "shots": 0,
                            "shots_total": 3,
                            "hits": 0,
                            "total_hits": 0,
                            "scored": False,
                            "power": 0.0,
                            "p_dir": 1.0,
                            "round": 1,
                            "max_rounds": 2,
                            "done": False,
                            "target_x": 560.0,
                            "target_y": 230.0,
                            "t_dirx": 1.0,
                            "t_diry": 1.0,
                            "wind": random.uniform(-12.0, 12.0),
                            "aim_x": None,
                            "aim_y": None,
                            "shot_fx": 0.0,
                            "shot_x": None,
                            "shot_y": None,
                            "shot_hit": False,
                            "shot_from": (310, 356),
                            "shot_marks": [],
                            "time_left": biathlon_time_limit,
                            "time_limit": biathlon_time_limit,
                        }
                    if btn_train_back.collidepoint(mx, my):
                        state = "menu"

        keys = pygame.key.get_pressed()

        # ca c'est pour mettre a jour la logique quand on joue
        if state == "splash":
            splash_timer += dt
            if splash_timer >= 2.5:
                state = "menu"

        if state == "playing" and not paused and not game_over:
            player = data["player"]
            drone = data["drone"]
            yetis = data["yetis"]

            if not data["finish_passed"]:
                data["race_time"] += dt
            player.update(dt, keys, screen_w, screen_h)
            drone.update(dt)
            if not data["finish_passed"]:
                data["distance_left"] = max(0.0, data["distance_left"] - data["speed"] * dt * data["distance_scale"])

            # camera: si le joueur monte, on decale le monde vers le bas
            cam_threshold = screen_h * 0.4
            if keys[pygame.K_UP] and player.y < cam_threshold:
                delta = (cam_threshold - player.y) * 0.2
                player.y = cam_threshold
                data["bg_offset"] -= delta
                drone.y += delta
                for ob in data["obstacles"]:
                    ob.y += delta
                for gate in data["gates"]:
                    gate.y += delta
                for b in data["bonuses"]:
                    b.y += delta
                for y in yetis:
                    y.y += delta
                if data["finish_line"] is not None:
                    data["finish_line"]["y"] += delta
                for p in data["particles"]:
                    p["y"] += delta
                for f in data["snowflakes"]:
                    f["y"] += delta
            if data["yeti_active"]:
                speed_bonus = (data["score"] // 100) * 6
                for idx, yeti in enumerate(yetis):
                    offset = (idx * 50) - (25 * (len(yetis) - 1))
                    yeti.update(dt, player.x + player.w / 2 + offset, player.y, data["speed"], speed_bonus, screen_h, screen_w)

            # ca c'est pour la vitesse du fond (impression de bouger)
            data["bg_offset"] += data["speed"] * dt * 0.6

            target_particles = 70 + int(data["speed"] / 7)
            while len(data["particles"]) < target_particles:
                data["particles"].append({
                    "x": random.randint(0, screen_w),
                    "y": random.randint(-screen_h, screen_h),
                    "len": random.randint(8, 24),
                    "spd": random.uniform(0.8, 1.6),
                })
            for p in data["particles"]:
                p["y"] += data["speed"] * dt * p["spd"]
                if p["y"] > screen_h + 30:
                    p["y"] = random.randint(-200, -20)
                    p["x"] = random.randint(0, screen_w)
                    p["len"] = random.randint(8, 24)
                    p["spd"] = random.uniform(0.8, 1.6)

            # flocons (mix petits + gros)
            target_flakes = 90
            while len(data["snowflakes"]) < target_flakes:
                size = random.choice([2, 2, 2, 3, 3, 4])
                data["snowflakes"].append({
                    "x": random.randint(0, screen_w),
                    "y": random.randint(-screen_h, screen_h),
                    "r": size,
                    "spd": random.uniform(20, 60) if size >= 3 else random.uniform(35, 80),
                    "drift": random.uniform(-20, 20),
                })
            for f in data["snowflakes"]:
                f["y"] += f["spd"] * dt
                f["x"] += f["drift"] * dt
                if f["x"] < -10:
                    f["x"] = screen_w + 10
                if f["x"] > screen_w + 10:
                    f["x"] = -10
                if f["y"] > screen_h + 10:
                    f["y"] = random.randint(-200, -20)
                    f["x"] = random.randint(0, screen_w)
                    f["r"] = random.choice([2, 2, 2, 3, 3, 4])
                    f["spd"] = random.uniform(20, 60) if f["r"] >= 3 else random.uniform(35, 80)
                    f["drift"] = random.uniform(-20, 20)

            # ca c'est pour faire apparaitre des rochers de temps en temps
            data["spawn_timer"] += dt
            level_cfg = level_settings.get(data["level"], level_settings[5])
            min_gap = max(0.85, level_cfg["min_gap"] - data["speed"] / 700.0)
            if data["spawn_timer"] >= min_gap:
                data["spawn_timer"] = 0.0
                ox = random.randint(20, screen_w - 50)
                rock_img = random.choice(images["rock"]) if isinstance(images["rock"], list) else images["rock"]
                data["obstacles"].append(
                    Obstacle(ox, -40, "rock", data["speed"], rock_img)
                )

            drone.try_drop(data["obstacles"], data["speed"], images["drop"])

            for ob in data["obstacles"][:]:
                ob.update(dt)
                if ob.y > screen_h + 50:
                    data["obstacles"].remove(ob)

            # ca c'est pour les portes de sapins (avec trou pour passer)
            data["gate_timer"] -= dt
            if data["gate_timer"] <= 0:
                gate_min, gate_max = level_cfg["gate_range"]
                data["gate_timer"] = random.uniform(gate_min, gate_max)
                gap_w = max(150, 220 - int(data["speed"] / 4))
                gap_x = random.randint(60, screen_w - 60 - gap_w)
                data["gates"].append(
                    Gate(-60, gap_x, gap_w, data["speed"], images["tree"], screen_w)
                )
                if data["level"] == 3:
                    gap_x2 = random.randint(60, screen_w - 60 - gap_w)
                    data["gates"].append(
                        Gate(-60, gap_x2, gap_w, data["speed"], images["tree"], screen_w)
                    )
                elif data["level"] > 3 and random.random() < level_cfg["extra_gate"]:
                    gap_x2 = random.randint(60, screen_w - 60 - gap_w)
                    data["gates"].append(
                        Gate(-140, gap_x2, gap_w, data["speed"], images["tree"], screen_w)
                    )

            for gate in data["gates"][:]:
                gate.update(dt)
                if gate.y > screen_h + 60:
                    data["gates"].remove(gate)

            # ca c'est pour les bonus aleatoires (danse ou boost)
            data["bonus_timer"] -= dt
            if data["bonus_timer"] <= 0:
                data["bonus_timer"] = random.uniform(*level_cfg["bonus_range"])
                bx = random.randint(30, screen_w - 50)
                if data["score"] >= 100:
                    data["bonuses"].append(Bonus(bx, -30, images["bonus"], data["speed"] * 0.85, "dance"))
                elif random.random() < 0.55:
                    data["bonuses"].append(Bonus(bx, -30, images["speed_boost"], data["speed"] * 0.85, "speed"))
                else:
                    data["bonuses"].append(Bonus(bx, -30, images["bonus"], data["speed"] * 0.85, "dance"))

            for b in data["bonuses"][:]:
                b.update(dt)
                if b.y > screen_h + 40:
                    data["bonuses"].remove(b)

            # ca c'est pour gerer les collisions
            pr = player.rect()
            for ob in data["obstacles"][:]:
                if pr.colliderect(ob.rect()):
                    data["obstacles"].remove(ob)
                    if ob.kind == "drone_drop":
                        player.freeze_timer = 1.5
                        play_sfx(audio["sfx"], "rock")
                    else:
                        player.slow_timer = 2.0
                        for y in yetis:
                            y.slow_timer = 2.2
                        data["score"] = max(0, data["score"] - 5)
                        play_sfx(audio["sfx"], "rock")

            if not game_over:
                for gate in data["gates"]:
                    if any(pr.colliderect(r) for r in gate.tree_rects()):
                        game_over = True
                        state = "game_over"
                        add_leaderboard(data["score"], None)
                        play_sfx(audio["sfx"], "game_over")
                        if audio["game_music"]:
                            audio["game_music"].stop()
                        break
                    if not gate.passed and gate.y + gate.tree_h >= player.y:
                        center_x = player.x + player.w / 2
                        if gate.gap_x <= center_x <= gate.gap_x + gate.gap_w:
                            gate.passed = True
                            data["score"] += 10
                            play_sfx(audio["sfx"], "gate")
                            # petit boost de vitesse du joueur a chaque porte
                            player.base_speed = min(7.0, player.base_speed + 0.08)
                        else:
                            game_over = True
                            state = "game_over"
                            add_leaderboard(data["score"], None)
                            play_sfx(audio["sfx"], "game_over")
                            if audio["game_music"]:
                                audio["game_music"].stop()
                            break

            if data["yeti_active"] and not game_over:
                for y in yetis:
                    if pr.colliderect(y.rect()):
                        game_over = True
                        state = "game_over"
                        add_leaderboard(data["score"], None)
                        play_sfx(audio["sfx"], "game_over")
                        if audio["game_music"]:
                            audio["game_music"].stop()
                        break

            for b in data["bonuses"][:]:
                if pr.colliderect(b.rect()):
                    data["bonuses"].remove(b)
                    if b.kind == "speed":
                        player.boost_timer = 5.0
                        data["score"] += 20
                        for y in yetis:
                            y.knockback = 1.5
                            y.y += 120
                        play_sfx(audio["sfx"], "speed")
                    else:
                        player.moonwalk = 3.0
                        data["score"] += 20
                        for y in yetis:
                            y.moonwalk_timer = 3.0
                        play_sfx(audio["sfx"], "bonus")

            # ca c'est pour augmenter le score avec le temps
            data["score"] += int(10 * dt)
            # petite accel progressive a chaque avancee du score
            data["speed"] = min(data["max_speed"], data["speed"] + 0.6 * dt)
            # ligne d'arrivee JO 2026 quand on approche du score cible
            if data["distance_left"] <= 24.0 and data["finish_line"] is None:
                gap_w = 200
                gap_x = random.randint(80, screen_w - 80 - gap_w)
                data["finish_line"] = {"y": -90, "gap_x": gap_x, "gap_w": gap_w, "passed": False}

            if data["finish_line"] is not None and not game_over:
                data["finish_line"]["y"] += data["speed"] * dt
                fy = data["finish_line"]["y"]
                gap_x = data["finish_line"]["gap_x"]
                gap_w = data["finish_line"]["gap_w"]
                left_flag = pygame.Rect(6, fy - 8, 18, 90)
                right_flag = pygame.Rect(screen_w - 24, fy - 8, 18, 90)
                if pr.colliderect(left_flag) or pr.colliderect(right_flag):
                    game_over = True
                    state = "game_over"
                    data["win"] = False
                    add_leaderboard(data["score"], None)
                    play_sfx(audio["sfx"], "game_over")
                    if audio["game_music"]:
                        audio["game_music"].stop()
                elif fy + 50 >= player.y and gap_x <= (player.x + player.w / 2) <= gap_x + gap_w:
                    data["finish_line"]["passed"] = True
                    data["finish_passed"] = True
                    data["win"] = True
                    if data.get("race_time_end") is None:
                        data["race_time_end"] = data["race_time"]
                    if data["level"] == 4:
                        state = "curling"
                        curling_data = {
                            "x": screen_w // 2,
                            "y": screen_h - 120,
                            "vx": 0.0,
                            "vy": 0.0,
                            "shot": False,
                            "done": False,
                            "power": 0.0,
                            "p_dir": 1.0,
                            "round": 1,
                            "max_rounds": 2,
                            "bonus_total": 0,
                            "throw_t": 0.0,
                            "time_left": curling_time_limit,
                            "time_limit": curling_time_limit,
                        }
                    elif data["level"] == 5:
                        state = "biathlon"
                        biathlon_data = {
                            "phase": "aim",
                            "shots": 0,
                            "shots_total": 3,
                            "hits": 0,
                            "total_hits": 0,
                            "scored": False,
                            "power": 0.0,
                            "p_dir": 1.0,
                            "round": 1,
                            "max_rounds": 2,
                            "done": False,
                            "target_x": 560.0,
                            "target_y": 230.0,
                            "t_dirx": 1.0,
                            "t_diry": 1.0,
                            "wind": random.uniform(-12.0, 12.0),
                            "aim_x": None,
                            "aim_y": None,
                            "shot_fx": 0.0,
                            "shot_x": None,
                            "shot_y": None,
                            "shot_hit": False,
                            "shot_from": (310, 356),
                            "shot_marks": [],
                            "time_left": biathlon_time_limit,
                            "time_limit": biathlon_time_limit,
                        }
                    else:
                        game_over = True
                        state = "game_over"
                    if data["race_time"] <= data["finish_time"]:
                        bonus = int((data["finish_time"] - data["race_time"]) * 5)
                        data["score"] += max(10, bonus)
                    add_leaderboard(data["score"], data.get("race_time_end"))
                    play_sfx(audio["sfx"], "gate")
                    if audio["game_music"]:
                        audio["game_music"].stop()
                elif fy > screen_h + 80:
                    game_over = True
                    state = "game_over"
                    data["win"] = False
                    add_leaderboard(data["score"], None)
                    play_sfx(audio["sfx"], "game_over")
                    if audio["game_music"]:
                        audio["game_music"].stop()
            # limite de temps
            if data["race_time"] >= data["finish_time"] and not game_over:
                game_over = True
                state = "game_over"
                data["win"] = False
                add_leaderboard(data["score"], None)
                play_sfx(audio["sfx"], "game_over")
                if audio["game_music"]:
                    audio["game_music"].stop()

        # ecran curling
        if state == "curling":
            draw_background(screen, images["bg_tile"], data["bg_offset"])
            screen.blit(mountain_layer, (0, 0))
            rink = pygame.Rect(160, 60, 480, 520)
            pygame.draw.rect(screen, (230, 240, 255), rink, border_radius=12)
            pygame.draw.rect(screen, (200, 220, 240), rink, 2, border_radius=12)
            target = (screen_w // 2, 100)
            pygame.draw.circle(screen, (200, 60, 60), target, 44, 4)
            pygame.draw.circle(screen, (60, 120, 200), target, 30, 4)
            pygame.draw.circle(screen, (240, 240, 240), target, 14, 0)

            title = big_font.render("Curling", True, (30, 40, 60))
            screen.blit(title, (screen_w // 2 - title.get_width() // 2, 60))
            hint = font.render("ESPACE pour lancer", True, (20, 30, 40))
            screen.blit(hint, (screen_w // 2 - hint.get_width() // 2, 90))
            if curling_data:
                time_txt = font.render(f"Temps: {format_time(curling_data.get('time_left', 0.0))}", True, (20, 30, 40))
                screen.blit(time_txt, (screen_w - time_txt.get_width() - 30, 92))

            if curling_data and not curling_data["done"]:
                time_left = curling_data.get("time_left", curling_time_limit)
                time_left = max(0.0, time_left - dt)
                curling_data["time_left"] = time_left
                if time_left <= 0.0 and not curling_data["shot"]:
                    curling_data["shot"] = True
                    curling_data["vx"] = 0.0
                    power = curling_data.get("power", 50)
                    curling_data["vy"] = -(220.0 + power * 1.2)
                    curling_data["throw_t"] = 0.0
                    play_sfx(audio["sfx"], "curling_slide")

                # jauge de puissance
                power = curling_data.get("power", 0.0)
                power += curling_data.get("p_dir", 1.0) * 120 * dt
                if power > 100:
                    power = 100
                    curling_data["p_dir"] = -1.0
                if power < 0:
                    power = 0
                    curling_data["p_dir"] = 1.0
                curling_data["power"] = power

                if curling_data["shot"]:
                    curling_data["y"] += curling_data["vy"] * dt
                    curling_data["vy"] *= 0.985
                    target_y = 100
                    if curling_data["y"] <= target_y:
                        hit_y = curling_data["y"]
                        curling_data["y"] = target_y
                        curling_data["done"] = True
                        dist = abs(hit_y - target_y)
                        bonus = max(0, int(140 - dist))
                        data["score"] += bonus
                        curling_data["bonus"] = bonus
                    elif abs(curling_data["vy"]) < 4:
                        curling_data["done"] = True
                        dist = abs(curling_data["y"] - target_y)
                        bonus = max(0, int(140 - dist))
                        data["score"] += bonus
                        curling_data["bonus"] = bonus

                # animation du lancer: le joueur reste fixe, seul le manche bouge
                throw_t = curling_data.get("throw_t", 0.0)
                if curling_data["shot"]:
                    throw_t = min(0.5, throw_t + dt)
                else:
                    throw_t = 0.0
                curling_data["throw_t"] = throw_t
                throw_phase = min(1.0, throw_t / 0.5) if curling_data["shot"] else 0.0

                # joueur de curling (fixe)
                curler_x = screen_w // 2 - 110
                curler_y = screen_h - 180
                pygame.draw.circle(screen, (255, 224, 200), (curler_x + 32, curler_y + 16), 10)
                pygame.draw.rect(screen, (80, 90, 140), (curler_x + 24, curler_y + 26, 20, 26), border_radius=4)
                pygame.draw.rect(screen, (60, 70, 90), (curler_x + 18, curler_y + 52, 42, 12), border_radius=4)
                pygame.draw.rect(screen, (50, 60, 80), (curler_x + 10, curler_y + 62, 18, 8), border_radius=3)
                pygame.draw.rect(screen, (50, 60, 80), (curler_x + 36, curler_y + 62, 18, 8), border_radius=3)

                # manche/balai avec mouvement de tir
                hand_x = curler_x + 50
                hand_y = curler_y + 34
                angle = 0.65 - 0.45 * throw_phase
                length = 75
                end_x = hand_x + math.cos(angle) * length
                end_y = hand_y + math.sin(angle) * length
                pygame.draw.line(screen, (120, 90, 60), (hand_x, hand_y), (end_x, end_y), 4)
                head_dx = math.cos(angle) * 10
                head_dy = math.sin(angle) * 10
                pygame.draw.line(screen, (180, 60, 60), (end_x - head_dx, end_y - head_dy), (end_x + head_dx, end_y + head_dy), 6)

                # pierre qui glisse (pas le joueur)
                pygame.draw.circle(screen, (180, 180, 190), (int(curling_data["x"]), int(curling_data["y"])), 16)
                pygame.draw.circle(screen, (140, 140, 150), (int(curling_data["x"]), int(curling_data["y"])), 16, 2)

            if curling_data and curling_data["done"]:
                bonus = curling_data.get("bonus", 0)
                info = font.render(f"Bonus: +{bonus}  Manche {curling_data['round']}/{curling_data['max_rounds']}", True, (20, 30, 40))
                screen.blit(info, (screen_w // 2 - info.get_width() // 2, 520))
                cont_text = "ENTREE pour manche suivante" if curling_data["round"] < curling_data["max_rounds"] else "ENTREE pour continuer"
                cont = font.render(cont_text, True, (20, 30, 40))
                screen.blit(cont, (screen_w // 2 - cont.get_width() // 2, 548))
            if curling_data:
                bar_x, bar_y = 240, 480
                pygame.draw.rect(screen, (200, 220, 240), (bar_x, bar_y, 320, 16), border_radius=4)
                p = curling_data.get("power", 0)
                if p < 50:
                    col = (80, 180, 90)
                elif p < 80:
                    col = (220, 190, 40)
                else:
                    col = (200, 60, 60)
                pygame.draw.rect(screen, col, (bar_x, bar_y, int(3.2 * p), 16), border_radius=4)
                p_txt = font.render(f"Puissance: {int(curling_data.get('power', 0))}", True, (20, 30, 40))
                screen.blit(p_txt, (bar_x, bar_y - 22))

            pygame.display.flip()
            continue

        # ecran biathlon (tir)
        if state == "biathlon":
            if biathlon_data is None or "phase" not in biathlon_data:
                biathlon_data = {
                    "phase": "aim",
                    "shots": 0,
                    "shots_total": 3,
                    "hits": 0,
                    "total_hits": 0,
                    "scored": False,
                    "power": 0.0,
                    "p_dir": 1.0,
                    "round": 1,
                    "max_rounds": 2,
                    "done": False,
                    "target_x": 560.0,
                    "target_y": 230.0,
                    "t_dirx": 1.0,
                    "t_diry": 1.0,
                    "wind": random.uniform(-12.0, 12.0),
                    "aim_x": None,
                    "aim_y": None,
                    "shot_fx": 0.0,
                    "shot_x": None,
                    "shot_y": None,
                    "shot_hit": False,
                    "shot_from": (310, 356),
                    "shot_marks": [],
                    "time_left": biathlon_time_limit,
                    "time_limit": biathlon_time_limit,
                }
            draw_background(screen, images["bg_tile"], data["bg_offset"])
            screen.blit(mountain_layer, (0, 0))
            title = big_font.render("Biathlon (tir)", True, (30, 40, 60))
            screen.blit(title, (screen_w // 2 - title.get_width() // 2, 60))
            hint = font.render("ESPACE: viser puis tirer", True, (20, 30, 40))
            screen.blit(hint, (screen_w // 2 - hint.get_width() // 2, 90))
            if biathlon_data and not biathlon_data["done"]:
                time_left = biathlon_data.get("time_left", biathlon_time_limit)
                time_left = max(0.0, time_left - dt)
                biathlon_data["time_left"] = time_left
                if time_left <= 0.0:
                    biathlon_data["done"] = True
            if biathlon_data:
                time_txt = font.render(f"Temps: {format_time(biathlon_data.get('time_left', 0.0))}", True, (20, 30, 40))
                screen.blit(time_txt, (screen_w - time_txt.get_width() - 30, 92))

            range_rect = pygame.Rect(70, 150, 660, 330)
            pygame.draw.rect(screen, (235, 245, 255), range_rect, border_radius=14)
            pygame.draw.rect(screen, (205, 220, 235), range_rect, 2, border_radius=14)
            for i in range(5):
                ly = range_rect.y + 40 + i * 55
                pygame.draw.line(screen, (210, 225, 240), (range_rect.x + 24, ly), (range_rect.right - 24, ly), 1)
            firing_y = range_rect.y + range_rect.h - 90
            pygame.draw.line(screen, (180, 200, 220), (range_rect.x + 20, firing_y), (range_rect.right - 20, firing_y), 2)
            panel = pygame.Rect(range_rect.x + 18, range_rect.y + 16, 160, 60)
            pygame.draw.rect(screen, (245, 250, 255), panel, border_radius=8)
            pygame.draw.rect(screen, (190, 210, 230), panel, 2, border_radius=8)
            panel_title = font.render("STAND 04", True, (30, 50, 70))
            screen.blit(panel_title, (panel.x + 10, panel.y + 6))
            shots_txt = font.render(f"Tirs: {biathlon_data['shots']}/{biathlon_data['shots_total']}", True, (30, 50, 70))
            screen.blit(shots_txt, (panel.x + 10, panel.y + 30))
            for i in range(biathlon_data["shots_total"]):
                dot_x = panel.x + 102 + i * 14
                dot_y = panel.y + 40
                if i < len(biathlon_data.get("shot_marks", [])):
                    hit = biathlon_data["shot_marks"][i][2]
                    col = (80, 180, 100) if hit else (200, 70, 60)
                    pygame.draw.circle(screen, col, (dot_x, dot_y), 5)
                pygame.draw.circle(screen, (30, 40, 50), (dot_x, dot_y), 5, 1)

            # cible fixe (style stand officiel)
            biathlon_data["target_x"] = 560.0
            biathlon_data["target_y"] = 230.0
            target_x = biathlon_data["target_x"]
            target_y = biathlon_data["target_y"]
            board_w, board_h = 200, 92
            board = pygame.Rect(int(target_x - board_w / 2), int(target_y - board_h / 2), board_w, board_h)
            pygame.draw.rect(screen, (130, 100, 75), board, border_radius=8)
            pygame.draw.rect(screen, (90, 70, 50), board, 3, border_radius=8)
            inner = board.inflate(-14, -14)
            pygame.draw.rect(screen, (230, 235, 240), inner, border_radius=6)
            for off in [-64, -32, 0, 32, 64]:
                c = (int(target_x + off), int(target_y))
                pygame.draw.circle(screen, (35, 35, 35), c, 12)
                pygame.draw.circle(screen, (235, 235, 235), c, 6)
            pygame.draw.line(screen, (110, 90, 70), (board.left + 24, board.bottom), (board.left + 10, board.bottom + 26), 3)
            pygame.draw.line(screen, (110, 90, 70), (board.right - 24, board.bottom), (board.right - 10, board.bottom + 26), 3)

            for shot_x, shot_y, hit in biathlon_data.get("shot_marks", []):
                col = (80, 180, 100) if hit else (200, 70, 60)
                pygame.draw.circle(screen, col, (int(shot_x), int(shot_y)), 4)
                pygame.draw.circle(screen, (20, 20, 20), (int(shot_x), int(shot_y)), 4, 1)

            wind = biathlon_data.get("wind", 0.0)
            flag_x = int(board.right + 18)
            flag_y = int(board.top - 6)
            pygame.draw.line(screen, (90, 90, 90), (flag_x, flag_y), (flag_x, flag_y + 36), 2)
            flag_dir = -1 if wind < 0 else 1
            pygame.draw.polygon(
                screen,
                (200, 60, 60),
                [(flag_x, flag_y + 6), (flag_x + 18 * flag_dir, flag_y + 12), (flag_x, flag_y + 18)],
            )

            power = biathlon_data.get("power", 0.0)
            if biathlon_data and not biathlon_data["done"] and biathlon_data["phase"] == "power":
                power += biathlon_data.get("p_dir", 1.0) * 140 * dt
                if power > 100:
                    power = 100
                    biathlon_data["p_dir"] = -1.0
                if power < 0:
                    power = 0
                    biathlon_data["p_dir"] = 1.0
                biathlon_data["power"] = power

            bar_x, bar_y = 180, 500
            pygame.draw.rect(screen, (200, 220, 240), (bar_x, bar_y, 440, 16), border_radius=4)
            pygame.draw.rect(screen, (80, 140, 200), (bar_x, bar_y, int(4.4 * power), 16), border_radius=4)
            p_txt = font.render(f"Puissance: {int(power)}", True, (20, 30, 40))
            screen.blit(p_txt, (bar_x, bar_y - 22))

            # viseur qui tremble legerement autour de la cible
            tremble = math.sin(pygame.time.get_ticks() * 0.02) * 6
            if biathlon_data.get("phase") == "power" and biathlon_data.get("aim_x") is not None:
                aim_x = biathlon_data["aim_x"]
                aim_y = biathlon_data["aim_y"]
            else:
                aim_x = biathlon_data["target_x"] + tremble + wind * 0.6
                aim_y = biathlon_data["target_y"] + tremble * 0.4
            pygame.draw.circle(screen, (20, 40, 60), (int(aim_x), int(aim_y)), 12, 2)
            pygame.draw.line(screen, (20, 40, 60), (aim_x - 12, aim_y), (aim_x + 12, aim_y), 2)
            pygame.draw.line(screen, (20, 40, 60), (aim_x, aim_y - 12), (aim_x, aim_y + 12), 2)
            wind_txt = font.render(f"Vent: {wind:+.1f}", True, (60, 80, 110))
            screen.blit(wind_txt, (bar_x + 280, bar_y - 22))

            shot_fx = biathlon_data.get("shot_fx", 0.0)
            if shot_fx > 0:
                biathlon_data["shot_fx"] = max(0.0, shot_fx - dt)
                strength = max(0.0, min(1.0, shot_fx / 0.25))
                intensity = int(140 + 90 * strength)
                if biathlon_data.get("shot_hit"):
                    col = (70, intensity, 90)
                else:
                    col = (intensity, 80, 70)
                shot_x = biathlon_data.get("shot_x")
                shot_y = biathlon_data.get("shot_y")
                shot_from = biathlon_data.get("shot_from", (310, 356))
                if shot_x is not None and shot_y is not None:
                    pygame.draw.line(screen, col, shot_from, (shot_x, shot_y), 2)
                    pygame.draw.circle(screen, col, (int(shot_x), int(shot_y)), 7, 2)

            # biathlete en position couchee + carabine
            shooter_x, shooter_y = 120, 380
            mat = pygame.Rect(shooter_x - 10, shooter_y + 18, 180, 22)
            pygame.draw.rect(screen, (70, 110, 160), mat, border_radius=6)
            pygame.draw.circle(screen, (255, 224, 200), (shooter_x + 20, shooter_y + 10), 8)
            pygame.draw.rect(screen, (50, 70, 110), (shooter_x + 30, shooter_y + 8, 70, 14), border_radius=4)
            pygame.draw.rect(screen, (40, 60, 90), (shooter_x + 90, shooter_y + 10, 50, 10), border_radius=4)
            pygame.draw.line(screen, (255, 224, 200), (shooter_x + 28, shooter_y + 12), (shooter_x + 50, shooter_y + 6), 3)
            pygame.draw.line(screen, (40, 40, 40), (shooter_x + 50, shooter_y + 6), (shooter_x + 190, shooter_y - 24), 3)
            pygame.draw.line(screen, (60, 60, 60), (shooter_x + 120, shooter_y - 10), (shooter_x + 150, shooter_y - 20), 4)

            if biathlon_data and biathlon_data["done"]:
                bonus = biathlon_data["hits"] * 40
                if not biathlon_data["scored"]:
                    data["score"] += bonus
                    biathlon_data["total_hits"] += biathlon_data["hits"]
                    biathlon_data["scored"] = True
                info = font.render(f"Touches: {biathlon_data['hits']}/3  (+{bonus})  Manche {biathlon_data['round']}/{biathlon_data['max_rounds']}", True, (20, 30, 40))
                screen.blit(info, (screen_w // 2 - info.get_width() // 2, 520))
                cont_text = "ENTREE pour manche suivante" if biathlon_data["round"] < biathlon_data["max_rounds"] else "ENTREE pour terminer"
                cont = font.render(cont_text, True, (20, 30, 40))
                screen.blit(cont, (screen_w // 2 - cont.get_width() // 2, 548))

            pygame.display.flip()
            continue

        # ca c'est pour dessiner le fond puis les elements
        draw_background(screen, images["bg_tile"], data["bg_offset"])
        screen.blit(mountain_layer, (0, 0))

        for p in data["particles"]:
            x = int(p["x"])
            y = int(p["y"])
            pygame.draw.line(screen, (230, 240, 250), (x, y), (x, y + p["len"]), 2)

        for f in data["snowflakes"]:
            pygame.draw.circle(screen, (245, 250, 255), (int(f["x"]), int(f["y"])), int(f["r"]))

        for gate in data["gates"]:
            gate.draw(screen)
        for ob in data["obstacles"]:
            ob.draw(screen)
        for b in data["bonuses"]:
            b.draw(screen)

        if data["yeti_active"]:
            for y in data["yetis"]:
                y.draw(screen)
        data["drone"].draw(screen)
        data["player"].draw(screen)

        # HUD sur bandeau translucide
        hud_panel = pygame.Surface((screen_w, 56), pygame.SRCALPHA)
        hud_panel.fill((245, 250, 255, 185))
        pygame.draw.line(hud_panel, (210, 225, 235, 200), (0, 54), (screen_w, 54), 2)
        screen.blit(hud_panel, (0, 0))

        time_left = max(0.0, data["finish_time"] - data["race_time"])

        # compteur + temps (gauche)
        clock_x, clock_y = 18, 14
        pygame.draw.circle(screen, (30, 60, 90), (clock_x, clock_y), 10, 2)
        pygame.draw.line(screen, (30, 60, 90), (clock_x, clock_y), (clock_x, clock_y - 5), 2)
        pygame.draw.line(screen, (30, 60, 90), (clock_x, clock_y), (clock_x + 4, clock_y + 2), 2)
        time_txt = font.render(f"{format_time(time_left)}", True, (20, 30, 40))
        screen.blit(time_txt, (clock_x + 14, clock_y - 8))

        dist_txt = font.render(f"{int(data['distance_left'])} m", True, (20, 30, 40))
        screen.blit(dist_txt, (screen_w - dist_txt.get_width() - 18, clock_y - 8))

        # score au centre
        score_txt = font.render(f"Score: {data['score']}", True, (20, 30, 40))
        screen.blit(score_txt, (screen_w // 2 - score_txt.get_width() // 2, 12))

        # vitesse + niveau (droite)
        vn_txt = font.render(f"Vitesse: {int(data['speed'])}  Niveau: {data['level']}", True, (20, 30, 40))
        screen.blit(vn_txt, (screen_w - vn_txt.get_width() - 16, 12))

        title = title_font.render("Milan-Cortina 2026 - Ski Runner", True, (30, 40, 60))
        screen.blit(title, (14, 34))

        if data["player"].moonwalk > 0:
            mw = font.render("MALUS : ski-danse (inverse)", True, (200, 40, 40))
            screen.blit(mw, (screen_w - 260, 10))
        if data["player"].boost_timer > 0:
            bs = font.render("Boost !", True, (40, 150, 80))
            screen.blit(bs, (screen_w - 120, 34))

        # ca c'est pour afficher les ecrans selon l'etat du jeu
        if state == "splash":
            if splash_image:
                screen.blit(splash_image, (0, 0))
            else:
                fallback = big_font.render("MILANO CORTINA 2026", True, (10, 10, 10))
                screen.blit(fallback, (screen_w // 2 - 200, screen_h // 2 - 20))

        if state == "menu":
            # Menu plus propre: panneau central + ombre + details
            panel_w, panel_h = 560, 340
            panel_x = screen_w // 2 - panel_w // 2
            panel_y = screen_h // 2 - panel_h // 2

            shadow = pygame.Surface((panel_w + 14, panel_h + 14), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 110))
            screen.blit(shadow, (panel_x - 7, panel_y - 4))

            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            for i in range(panel_h):
                shade = 242 + int(8 * (i / panel_h))
                panel.fill((shade, shade + 4, 255, 230), rect=pygame.Rect(0, i, panel_w, 1))
            pygame.draw.rect(panel, (210, 225, 240, 200), (0, 0, panel_w, panel_h), 2)
            pygame.draw.rect(panel, (255, 255, 255, 120), (6, 6, panel_w - 12, panel_h - 12), 1)

            # bandeau titre
            pygame.draw.rect(panel, (220, 235, 248, 220), (0, 0, panel_w, 78))
            pygame.draw.line(panel, (170, 195, 215, 200), (24, 74), (panel_w - 24, 74), 2)

            # petits flocons decoratifs
            for i in range(18):
                fx = 24 + (i * 28) % (panel_w - 48)
                fy = 100 + (i * 17) % (panel_h - 120)
                pygame.draw.circle(panel, (255, 255, 255, 140), (fx, fy), 2)

            screen.blit(panel, (panel_x, panel_y))

            title_shadow = big_font.render("MILANO-CORTINA 2026", True, (210, 220, 230))
            title = big_font.render("MILANO-CORTINA 2026", True, (30, 40, 60))
            subtitle = font.render("Ski Runner", True, (60, 80, 110))
            screen.blit(title_shadow, (screen_w // 2 - title_shadow.get_width() // 2 + 2, panel_y + 18))
            screen.blit(title, (screen_w // 2 - title.get_width() // 2, panel_y + 16))
            screen.blit(subtitle, (screen_w // 2 - subtitle.get_width() // 2, panel_y + 58))

            # perso de ski anime (style "gif")
            if images.get("skier"):
                anim_idx = (pygame.time.get_ticks() // 120) % len(images["skier"])
                frame = images["skier"][anim_idx]
                fx = panel_x + panel_w - 150
                fy = panel_y + 110
                pygame.draw.ellipse(screen, (210, 220, 235), (fx - 6, fy + 54, 70, 16))
                screen.blit(frame, (fx, fy))

            lines = [
                "Clique un mode pour jouer",
                "Fleches : bouger",
                "Espace / P : pause",
                "Score cible + arrivee JO 2026",
                "Gagne le niveau pour passer",
                "Bonus vitesse < 100 / Malus danse >= 100",
            ]
            ly = panel_y + 105
            for line in lines:
                txt = font.render(line, True, (20, 30, 40))
                screen.blit(txt, (panel_x + 36, ly))
                ly += 26

            name_line = font.render(f"Prenom: {name_input or '_'}", True, (30, 90, 120))
            screen.blit(name_line, (panel_x + 36, panel_y + panel_h - 40))

            # boutons modes
            btn_triathlon = pygame.Rect(panel_x + 30, panel_y + panel_h - 80, 170, 34)
            btn_training = pygame.Rect(panel_x + panel_w - 200, panel_y + panel_h - 80, 170, 34)
            tri_col = (20, 120, 200) if menu_choice == 0 else (70, 90, 110)
            trn_col = (20, 120, 200) if menu_choice == 1 else (70, 90, 110)
            pygame.draw.rect(screen, tri_col, btn_triathlon, border_radius=6)
            pygame.draw.rect(screen, trn_col, btn_training, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255), btn_triathlon, 2 if menu_choice == 0 else 1, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255), btn_training, 2 if menu_choice == 1 else 1, border_radius=6)
            t_txt = font.render("MODE JO", True, (235, 245, 255))
            e_txt = font.render("ENTRAINEMENT", True, (235, 245, 255))
            screen.blit(t_txt, (btn_triathlon.centerx - t_txt.get_width() // 2, btn_triathlon.centery - t_txt.get_height() // 2))
            screen.blit(e_txt, (btn_training.centerx - e_txt.get_width() // 2, btn_training.centery - e_txt.get_height() // 2))
            sel_txt = "Selection: MODE JO" if menu_choice == 0 else "Selection: ENTRAINEMENT"
            sel = font.render(sel_txt, True, (30, 60, 90))
            screen.blit(sel, (panel_x + 30, panel_y + panel_h - 112))

            if audio["menu_music"] and not pygame.mixer.get_busy():
                audio["menu_music"].play(loops=-1)
            # neige qui tombe sur le menu
            for f in data["snowflakes"]:
                f["y"] += f["spd"] * dt
                f["x"] += f["drift"] * dt
                if f["x"] < -10:
                    f["x"] = screen_w + 10
                if f["x"] > screen_w + 10:
                    f["x"] = -10
                if f["y"] > screen_h + 10:
                    f["y"] = random.randint(-200, -20)
                    f["x"] = random.randint(0, screen_w)

        if state == "training_menu":
            panel_w, panel_h = 520, 300
            panel_x = screen_w // 2 - panel_w // 2
            panel_y = screen_h // 2 - panel_h // 2
            shadow = pygame.Surface((panel_w + 14, panel_h + 14), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 110))
            screen.blit(shadow, (panel_x - 7, panel_y - 4))

            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            for i in range(panel_h):
                shade = 242 + int(8 * (i / panel_h))
                panel.fill((shade, shade + 4, 255, 230), rect=pygame.Rect(0, i, panel_w, 1))
            pygame.draw.rect(panel, (210, 225, 240, 200), (0, 0, panel_w, panel_h), 2)
            screen.blit(panel, (panel_x, panel_y))

            title = big_font.render("ENTRAINEMENT", True, (30, 40, 60))
            screen.blit(title, (screen_w // 2 - title.get_width() // 2, panel_y + 18))
            sel_txt = ["COURSE", "CURLING", "BIATHLON", "RETOUR"][training_choice]
            sel = font.render(f"Selection: {sel_txt}", True, (30, 60, 90))
            screen.blit(sel, (panel_x + 40, panel_y + 62))

            btn_train_course = pygame.Rect(panel_x + 40, panel_y + 90, 200, 36)
            btn_train_curling = pygame.Rect(panel_x + 40, panel_y + 140, 200, 36)
            btn_train_biathlon = pygame.Rect(panel_x + 40, panel_y + 190, 200, 36)
            btn_train_back = pygame.Rect(panel_x + panel_w - 160, panel_y + panel_h - 60, 120, 30)

            for idx, (rect, label) in enumerate([
                (btn_train_course, "COURSE"),
                (btn_train_curling, "CURLING"),
                (btn_train_biathlon, "BIATHLON"),
            ]):
                col = (20, 120, 200) if training_choice == idx else (70, 90, 110)
                pygame.draw.rect(screen, col, rect, border_radius=6)
                pygame.draw.rect(screen, (255, 255, 255), rect, 2 if training_choice == idx else 1, border_radius=6)
                txt = font.render(label, True, (235, 245, 255))
                screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

            back_col = (20, 120, 200) if training_choice == 3 else (80, 90, 110)
            pygame.draw.rect(screen, back_col, btn_train_back, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255), btn_train_back, 2 if training_choice == 3 else 1, border_radius=6)
            back_txt = font.render("RETOUR", True, (235, 245, 255))
            screen.blit(back_txt, (btn_train_back.centerx - back_txt.get_width() // 2, btn_train_back.centery - back_txt.get_height() // 2))

        # dessin de la ligne d'arrivee (drapeaux)
        if data["finish_line"] is not None and state == "playing" and not game_over:
            fy = int(data["finish_line"]["y"])
            gap_x = data["finish_line"]["gap_x"]
            gap_w = data["finish_line"]["gap_w"]
            # banderole longue
            pygame.draw.rect(screen, (245, 245, 245), (0, fy - 14, screen_w, 20))
            for i in range(0, screen_w, 26):
                col = (20, 20, 20) if ((i // 26) % 2 == 0) else (230, 230, 230)
                pygame.draw.rect(screen, col, (i, fy - 14, 26, 20))
            # drapeaux
            left_x = 6
            right_x = screen_w - 24
            pygame.draw.rect(screen, (120, 120, 120), (left_x + 6, fy - 6, 4, 90))
            pygame.draw.rect(screen, (120, 120, 120), (right_x + 6, fy - 6, 4, 90))
            pygame.draw.polygon(screen, (200, 30, 30), [(left_x + 10, fy + 6), (left_x + 40, fy + 16), (left_x + 10, fy + 26)])
            pygame.draw.polygon(screen, (200, 30, 30), [(right_x + 10, fy + 6), (right_x + 40, fy + 16), (right_x + 10, fy + 26)])
            banner = font.render(f"ARRIVEE {int(data['distance_total'])} m", True, (200, 30, 30))
            screen.blit(banner, (screen_w // 2 - banner.get_width() // 2, fy - 38))

        if paused and state == "playing":
            overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            overlay.fill((20, 30, 40, 120))
            screen.blit(overlay, (0, 0))
            p = big_font.render("PAUSE", True, (245, 250, 255))
            screen.blit(p, (screen_w // 2 - 70, screen_h // 2 - 40))
            hint = font.render("Espace / P pour reprendre", True, (230, 240, 250))
            hint2 = font.render("Echap : quitter", True, (230, 240, 250))
            screen.blit(hint, (screen_w // 2 - hint.get_width() // 2, screen_h // 2 + 10))
            screen.blit(hint2, (screen_w // 2 - hint2.get_width() // 2, screen_h // 2 + 36))

        if state == "game_over":
            overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            overlay.fill((15, 20, 30, 140))
            screen.blit(overlay, (0, 0))
            panel_w, panel_h = 420, 280
            panel_x = screen_w // 2 - panel_w // 2
            panel_y = screen_h // 2 - panel_h // 2
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((250, 252, 255, 235))
            pygame.draw.rect(panel, (200, 220, 235, 220), (0, 0, panel_w, panel_h), 2)
            screen.blit(panel, (panel_x, panel_y))

            title_text = "ARRIVEE !" if data.get("win") else "FIN !"
            over = big_font.render(title_text, True, (200, 30, 30))
            screen.blit(over, (screen_w // 2 - over.get_width() // 2, panel_y + 20))
            if data.get("win"):
                final_time = data.get("race_time_end", data["race_time"])
                time_line = font.render(f"Temps: {format_time(final_time)}", True, (20, 30, 40))
                screen.blit(time_line, (screen_w // 2 - time_line.get_width() // 2, panel_y + 54))
            if data.get("win") and data["level"] < 5:
                back = font.render("R : rejouer niveau  |  Entree : niveau suivant", True, (20, 30, 40))
            elif data.get("win"):
                back = font.render("R : rejouer niveau  |  Entree : menu", True, (20, 30, 40))
            else:
                back = font.render("R : rejouer niveau  |  Entree : rejouer niveau", True, (20, 30, 40))
            screen.blit(back, (screen_w // 2 - back.get_width() // 2, panel_y + 90))
            if leaderboard and mode == "jo" and data.get("final_done"):
                ly = panel_y + 125
                title = font.render("Classement:", True, (10, 10, 10))
                screen.blit(title, (screen_w // 2 - title.get_width() // 2, ly))
                ly += 24
                medals = {1: "Or", 2: "Argent", 3: "Bronze"}
                for i, (sc, nm, tm) in enumerate(leaderboard, start=1):
                    time_txt = format_time(tm)
                    medal = medals.get(i, f"{i}e")
                    line = font.render(f"{medal} - {nm} - {sc} pts - {time_txt}", True, (10, 10, 10))
                    screen.blit(line, (screen_w // 2 - line.get_width() // 2, ly))
                    ly += 20

        if state == "name_entry":
            overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            overlay.fill((15, 20, 30, 120))
            screen.blit(overlay, (0, 0))
            panel_w, panel_h = 440, 200
            panel_x = screen_w // 2 - panel_w // 2
            panel_y = screen_h // 2 - panel_h // 2
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((250, 252, 255, 235))
            pygame.draw.rect(panel, (200, 220, 235, 220), (0, 0, panel_w, panel_h), 2)
            screen.blit(panel, (panel_x, panel_y))

            prompt = big_font.render("Entre ton prenom", True, (10, 10, 10))
            val = font.render(name_input or "_", True, (10, 10, 10))
            hint = font.render("ENTRER pour valider", True, (10, 10, 10))
            screen.blit(prompt, (screen_w // 2 - prompt.get_width() // 2, panel_y + 24))
            screen.blit(val, (screen_w // 2 - val.get_width() // 2, panel_y + 90))
            screen.blit(hint, (screen_w // 2 - hint.get_width() // 2, panel_y + 130))

        # vignette douce
        screen.blit(vignette, (0, 0))
        # grain neigeux
        screen.blit(grain, (0, 0))

        pygame.display.flip()


if __name__ == "__main__":
    main()
