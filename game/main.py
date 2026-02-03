import random
import os
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
    screen_w, screen_h = 800, 600
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("JO d'hiver 2026 - Ski Runner")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("arial", 20)
    big_font = pygame.font.SysFont("arial", 36)

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
    splash_timer = 0.0
    splash_image = None

    splash_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "24.10.24-Milano-Cortina-1.webp")
    if os.path.exists(splash_path):
        try:
            splash_image = pygame.image.load(splash_path).convert()
            splash_image = pygame.transform.smoothscale(splash_image, (screen_w, screen_h))
        except pygame.error:
            splash_image = None

    level_settings = {
        1: {"speed_base": 130, "max_speed": 230, "min_gap": 1.8, "gate_range": (1.7, 2.6), "extra_gate": 0.0, "bonus_range": (4.2, 6.5)},
        2: {"speed_base": 140, "max_speed": 245, "min_gap": 1.6, "gate_range": (1.6, 2.3), "extra_gate": 0.1, "bonus_range": (3.8, 6.0)},
        3: {"speed_base": 150, "max_speed": 260, "min_gap": 1.45, "gate_range": (1.4, 2.1), "extra_gate": 0.2, "bonus_range": (3.3, 5.5)},
        4: {"speed_base": 160, "max_speed": 275, "min_gap": 1.3, "gate_range": (1.3, 2.0), "extra_gate": 0.3, "bonus_range": (2.9, 5.0)},
        5: {"speed_base": 170, "max_speed": 295, "min_gap": 1.15, "gate_range": (1.2, 1.8), "extra_gate": 0.4, "bonus_range": (2.5, 4.6)},
    }

    def apply_level_settings(current):
        level_cfg = level_settings.get(current["level"], level_settings[5])
        current["max_speed"] = level_cfg["max_speed"]
        current["speed"] = min(current["max_speed"], level_cfg["speed_base"])
        gate_min, gate_max = level_cfg["gate_range"]
        current["gate_timer"] = random.uniform(gate_min, gate_max)
        current["bonus_timer"] = random.uniform(*level_cfg["bonus_range"])

    data = reset_game(screen_w, screen_h, images, 1)
    apply_level_settings(data)

    # ca c'est pour la boucle principale du jeu
    while True:
        dt = clock.tick(60) / 1000.0

        # ca c'est pour gerer les evenements clavier / fermer la fenetre
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if state == "splash":
                    state = "menu"
                elif state == "menu":
                    if event.key == pygame.K_RETURN:
                        if name_input.strip() == "":
                            state = "name_entry"
                        else:
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
                elif state == "playing":
                    if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                        paused = not paused
                        play_sfx(audio["sfx"], "pause" if paused else "resume")
                elif state == "game_over":
                    if event.key == pygame.K_r:
                        state = "playing"
                        paused = False
                        game_over = False
                        pending_score = None
                        pending_time = None
                        data = reset_game(screen_w, screen_h, images, data["level"])
                        apply_level_settings(data)
                        if audio["menu_music"]:
                            audio["menu_music"].stop()
                        if audio["game_music"]:
                            audio["game_music"].play(loops=-1)
                    if event.key == pygame.K_RETURN:
                        if pending_score is not None and name_input.strip() == "":
                            state = "name_entry"
                        else:
                            if data.get("win") and data["level"] < 5:
                                state = "playing"
                                paused = False
                                game_over = False
                                pending_score = None
                                pending_time = None
                                data = reset_game(screen_w, screen_h, images, data["level"] + 1)
                                apply_level_settings(data)
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
                                leaderboard.append((pending_score, name_input.strip(), pending_time))
                                leaderboard.sort(key=lambda x: x[0], reverse=True)
                                leaderboard = leaderboard[:5]
                                pending_score = None
                                pending_time = None
                                state = "game_over"
                            else:
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
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    else:
                        if event.unicode.isprintable() and len(name_input) < 12:
                            name_input += event.unicode

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

            data["race_time"] += dt
            player.update(dt, keys, screen_w, screen_h)
            drone.update(dt, player.x + player.w / 2)
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
                data["obstacles"].append(
                    Obstacle(ox, -40, "rock", data["speed"], images["rock"])
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
                if random.random() < level_cfg["extra_gate"]:
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
                elif random.random() < 0.35:
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
                        pending_score = data["score"]
                        pending_time = None
                        if name_input.strip() != "":
                            leaderboard.append((pending_score, name_input.strip(), pending_time))
                            leaderboard.sort(key=lambda x: x[0], reverse=True)
                            leaderboard = leaderboard[:5]
                            pending_score = None
                            pending_time = None
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
                            pending_score = data["score"]
                            pending_time = None
                            if name_input.strip() != "":
                                leaderboard.append((pending_score, name_input.strip(), pending_time))
                                leaderboard.sort(key=lambda x: x[0], reverse=True)
                                leaderboard = leaderboard[:5]
                                pending_score = None
                                pending_time = None
                            play_sfx(audio["sfx"], "game_over")
                            if audio["game_music"]:
                                audio["game_music"].stop()
                            break

            if data["yeti_active"] and not game_over:
                for y in yetis:
                    if pr.colliderect(y.rect()):
                        game_over = True
                        state = "game_over"
                        pending_score = data["score"]
                        pending_time = None
                        if name_input.strip() != "":
                            leaderboard.append((pending_score, name_input.strip(), pending_time))
                            leaderboard.sort(key=lambda x: x[0], reverse=True)
                            leaderboard = leaderboard[:5]
                            pending_score = None
                            pending_time = None
                        play_sfx(audio["sfx"], "game_over")
                        if audio["game_music"]:
                            audio["game_music"].stop()
                        break

            for b in data["bonuses"][:]:
                if pr.colliderect(b.rect()):
                    data["bonuses"].remove(b)
                    if b.kind == "speed":
                        player.boost_timer = 5.0
                        data["score"] += 15
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
            # ligne d'arrivee JO 2026 sur timer
            if data["race_time"] >= data["finish_time"] - 4.0 and data["finish_line"] is None:
                gap_w = 200
                gap_x = random.randint(80, screen_w - 80 - gap_w)
                data["finish_line"] = {"y": -90, "gap_x": gap_x, "gap_w": gap_w, "passed": False}

            if data["finish_line"] is not None and not game_over:
                data["finish_line"]["y"] += data["speed"] * dt
                fy = data["finish_line"]["y"]
                gap_x = data["finish_line"]["gap_x"]
                gap_w = data["finish_line"]["gap_w"]
                left_flag = pygame.Rect(gap_x - 22, fy - 8, 18, 90)
                right_flag = pygame.Rect(gap_x + gap_w + 4, fy - 8, 18, 90)
                if pr.colliderect(left_flag) or pr.colliderect(right_flag):
                    game_over = True
                    state = "game_over"
                    data["win"] = False
                    pending_score = data["score"]
                    pending_time = None
                    if name_input.strip() != "":
                        leaderboard.append((pending_score, name_input.strip(), pending_time))
                        leaderboard.sort(key=lambda x: x[0], reverse=True)
                        leaderboard = leaderboard[:5]
                        pending_score = None
                        pending_time = None
                    play_sfx(audio["sfx"], "game_over")
                    if audio["game_music"]:
                        audio["game_music"].stop()
                elif fy + 50 >= player.y and gap_x <= (player.x + player.w / 2) <= gap_x + gap_w:
                    data["finish_line"]["passed"] = True
                    data["finish_passed"] = True
                    data["win"] = True
                    game_over = True
                    state = "game_over"
                    pending_score = data["score"]
                    pending_time = data["race_time"]
                    if name_input.strip() != "":
                        leaderboard.append((pending_score, name_input.strip(), pending_time))
                        leaderboard.sort(key=lambda x: x[0], reverse=True)
                        leaderboard = leaderboard[:5]
                        pending_score = None
                        pending_time = None
                    play_sfx(audio["sfx"], "gate")
                    if audio["game_music"]:
                        audio["game_music"].stop()
                elif fy > screen_h + 80:
                    game_over = True
                    state = "game_over"
                    data["win"] = False
                    pending_score = data["score"]
                    pending_time = None
                    if name_input.strip() != "":
                        leaderboard.append((pending_score, name_input.strip(), pending_time))
                        leaderboard.sort(key=lambda x: x[0], reverse=True)
                        leaderboard = leaderboard[:5]
                        pending_score = None
                        pending_time = None
                    play_sfx(audio["sfx"], "game_over")
                    if audio["game_music"]:
                        audio["game_music"].stop()

        # ca c'est pour dessiner le fond puis les elements
        draw_background(screen, images["bg_tile"], data["bg_offset"])

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

        time_left = max(0, int(data["finish_time"] - data["race_time"]))
        hud = font.render(
            f"Score: {data['score']}  Vitesse: {int(data['speed'])}  Niveau: {data['level']}  Timer: {time_left}s",
            True,
            (20, 30, 40),
        )
        screen.blit(hud, (14, 12))

        title = font.render("Milan-Cortina 2026 - Ski Runner", True, (30, 40, 60))
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

            lines = [
                "ENTRER : demarrer",
                "Fleches : bouger",
                "Espace / P : pause",
                "Timer 25s + arrivee JO 2026",
                "Gagne le niveau pour passer",
                "Bonus vitesse < 100 / Malus danse >= 100",
            ]
            ly = panel_y + 105
            for line in lines:
                txt = font.render(line, True, (20, 30, 40))
                screen.blit(txt, (panel_x + 36, ly))
                ly += 26

            # faux bouton "ENTRER"
            btn_w, btn_h = 170, 34
            btn_x = panel_x + panel_w - btn_w - 30
            btn_y = panel_y + panel_h - btn_h - 22
            pygame.draw.rect(screen, (30, 60, 90), (btn_x, btn_y, btn_w, btn_h), border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255), (btn_x + 2, btn_y + 2, btn_w - 4, btn_h - 4), 1, border_radius=6)
            btn_text = font.render("ENTRER", True, (235, 245, 255))
            screen.blit(btn_text, (btn_x + btn_w // 2 - btn_text.get_width() // 2, btn_y + 7))

            name_line = font.render(f"Prenom: {name_input or '_'}", True, (30, 90, 120))
            screen.blit(name_line, (panel_x + 36, panel_y + panel_h - 40))

            if audio["menu_music"] and not pygame.mixer.get_busy():
                audio["menu_music"].play(loops=-1)

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
            left_x = gap_x - 22
            right_x = gap_x + gap_w + 4
            pygame.draw.rect(screen, (120, 120, 120), (left_x + 6, fy - 6, 4, 90))
            pygame.draw.rect(screen, (120, 120, 120), (right_x + 6, fy - 6, 4, 90))
            pygame.draw.polygon(screen, (200, 30, 30), [(left_x + 10, fy + 6), (left_x + 40, fy + 16), (left_x + 10, fy + 26)])
            pygame.draw.polygon(screen, (200, 30, 30), [(right_x + 10, fy + 6), (right_x + 40, fy + 16), (right_x + 10, fy + 26)])
            banner = font.render("ARRIVEE JO 2026", True, (200, 30, 30))
            screen.blit(banner, (screen_w // 2 - banner.get_width() // 2, fy - 38))

        if paused and state == "playing":
            overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            overlay.fill((20, 30, 40, 120))
            screen.blit(overlay, (0, 0))
            p = big_font.render("PAUSE", True, (245, 250, 255))
            screen.blit(p, (screen_w // 2 - 70, screen_h // 2 - 40))
            hint = font.render("Espace / P pour reprendre", True, (230, 240, 250))
            screen.blit(hint, (screen_w // 2 - hint.get_width() // 2, screen_h // 2 + 10))

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
                time_line = font.render(f"Temps: {data['race_time']:.1f}s", True, (20, 30, 40))
                screen.blit(time_line, (screen_w // 2 - time_line.get_width() // 2, panel_y + 54))
            if data.get("win") and data["level"] < 5:
                back = font.render("R : rejouer niveau  |  Entree : niveau suivant", True, (20, 30, 40))
            else:
                back = font.render("R : rejouer niveau  |  Entree : menu", True, (20, 30, 40))
            screen.blit(back, (screen_w // 2 - back.get_width() // 2, panel_y + 90))
            if leaderboard:
                ly = panel_y + 125
                title = font.render("Classement:", True, (10, 10, 10))
                screen.blit(title, (screen_w // 2 - title.get_width() // 2, ly))
                ly += 24
                for i, (sc, nm, tm) in enumerate(leaderboard, start=1):
                    time_txt = f"{tm:.1f}s" if tm is not None else "-"
                    line = font.render(f"{i}. {nm} - {sc} pts - {time_txt}", True, (10, 10, 10))
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

        pygame.display.flip()


if __name__ == "__main__":
    main()
