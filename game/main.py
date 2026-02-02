import random
import os
import pygame

from .assets import ensure_assets, load_images
from .audio import build_audio, play_sfx
from .entities import Player, Obstacle, Gate, Bonus, Drone, Yeti


def reset_game(screen_w, screen_h, images):
    # ca c'est pour remettre tout a zero quand on recommence
    player = Player(0, screen_h // 2, images["skier"])
    player.x = screen_w // 2 - player.w // 2
    drone = Drone(screen_w // 2, images["drone"])
    yeti = Yeti(screen_w // 2, screen_h + 140, images["yeti"])

    return {
        "player": player,
        "drone": drone,
        "yeti": yeti,
        "yeti_active": False,
        "obstacles": [],
        "gates": [],
        "bonuses": [],
        "bg_offset": 0.0,
        "score": 0,
        "level": 1,
        "speed": 130,
        "max_speed": 260,
        "spawn_timer": 0.0,
        "bonus_timer": 2.5,
        "gate_timer": 1.8,
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
    splash_timer = 0.0
    splash_image = None

    splash_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "24.10.24-Milano-Cortina-1.webp")
    if os.path.exists(splash_path):
        try:
            splash_image = pygame.image.load(splash_path).convert()
            splash_image = pygame.transform.smoothscale(splash_image, (screen_w, screen_h))
        except pygame.error:
            splash_image = None

    data = reset_game(screen_w, screen_h, images)

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
                            data = reset_game(screen_w, screen_h, images)
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
                        data = reset_game(screen_w, screen_h, images)
                        if audio["menu_music"]:
                            audio["menu_music"].stop()
                        if audio["game_music"]:
                            audio["game_music"].play(loops=-1)
                    if event.key == pygame.K_RETURN:
                        if pending_score is not None and name_input.strip() == "":
                            state = "name_entry"
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
                                leaderboard.append((pending_score, name_input.strip()))
                                leaderboard.sort(key=lambda x: x[0], reverse=True)
                                leaderboard = leaderboard[:5]
                                pending_score = None
                                state = "game_over"
                            else:
                                state = "playing"
                                paused = False
                                game_over = False
                                data = reset_game(screen_w, screen_h, images)
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
            yeti = data["yeti"]

            player.update(dt, keys, screen_w)
            drone.update(dt, player.x + player.w / 2)
            if not data["yeti_active"] and data["score"] >= 100:
                data["yeti_active"] = True
                yeti.y = screen_h + 140
                yeti.x = random.randint(0, screen_w - yeti.w)
            if data["yeti_active"]:
                speed_bonus = (data["score"] // 100) * 6
                yeti.update(dt, player.x + player.w / 2, player.y, data["speed"], speed_bonus, screen_h, screen_w)

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
            min_gap = max(0.9, 1.8 - data["speed"] / 500.0)
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
                data["gate_timer"] = random.uniform(1.6, 2.4)
                gap_w = max(150, 220 - int(data["speed"] / 4))
                gap_x = random.randint(60, screen_w - 60 - gap_w)
                data["gates"].append(
                    Gate(-60, gap_x, gap_w, data["speed"], images["tree"], screen_w)
                )

            for gate in data["gates"][:]:
                gate.update(dt)
                if gate.y > screen_h + 60:
                    data["gates"].remove(gate)

            # ca c'est pour les bonus aleatoires (danse ou boost)
            data["bonus_timer"] -= dt
            if data["bonus_timer"] <= 0:
                data["bonus_timer"] = random.uniform(4.0, 7.0)
                bx = random.randint(30, screen_w - 50)
                if random.random() < 0.35:
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
                    yeti.slow_timer = 2.2
                    data["score"] = max(0, data["score"] - 5)
                    play_sfx(audio["sfx"], "rock")

            if not game_over:
                for gate in data["gates"]:
                    if any(pr.colliderect(r) for r in gate.tree_rects()):
                        game_over = True
                        state = "game_over"
                        pending_score = data["score"]
                        if name_input.strip() != "":
                            leaderboard.append((pending_score, name_input.strip()))
                            leaderboard.sort(key=lambda x: x[0], reverse=True)
                            leaderboard = leaderboard[:5]
                            pending_score = None
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
                            if name_input.strip() != "":
                                leaderboard.append((pending_score, name_input.strip()))
                                leaderboard.sort(key=lambda x: x[0], reverse=True)
                                leaderboard = leaderboard[:5]
                                pending_score = None
                            play_sfx(audio["sfx"], "game_over")
                            if audio["game_music"]:
                                audio["game_music"].stop()
                            break

            if data["yeti_active"] and not game_over and pr.colliderect(yeti.rect()):
                game_over = True
                state = "game_over"
                pending_score = data["score"]
                if name_input.strip() != "":
                    leaderboard.append((pending_score, name_input.strip()))
                    leaderboard.sort(key=lambda x: x[0], reverse=True)
                    leaderboard = leaderboard[:5]
                    pending_score = None
                play_sfx(audio["sfx"], "game_over")
                if audio["game_music"]:
                    audio["game_music"].stop()

            for b in data["bonuses"][:]:
                if pr.colliderect(b.rect()):
                    data["bonuses"].remove(b)
                    if b.kind == "speed":
                        player.boost_timer = 5.0
                        data["score"] += 15
                        yeti.knockback = 1.5
                        yeti.y += 120
                        play_sfx(audio["sfx"], "speed")
                    else:
                        player.moonwalk = 3.0
                        data["score"] += 20
                        yeti.moonwalk_timer = 3.0
                        play_sfx(audio["sfx"], "bonus")

            # ca c'est pour augmenter le score avec le temps
            data["score"] += int(10 * dt)
            # petite accel progressive a chaque avancee du score
            data["speed"] = min(data["max_speed"], data["speed"] + 0.6 * dt)
            new_level = max(1, data["score"] // 200 + 1)
            if new_level != data["level"]:
                data["level"] = new_level
                data["speed"] = min(data["max_speed"], 130 + (data["level"] - 1) * 12)
                data["gate_timer"] = max(1.2, 2.0 - data["level"] * 0.08)
                data["bonus_timer"] = max(3.0, 6.0 - data["level"] * 0.2)

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
            data["yeti"].draw(screen)
        data["drone"].draw(screen)
        data["player"].draw(screen)

        hud = font.render(
            f"Score: {data['score']}  Vitesse: {int(data['speed'])}  Niveau: {data['level']}",
            True,
            (20, 20, 20),
        )
        screen.blit(hud, (10, 10))

        title = font.render("Milan-Cortina 2026 - Ski Runner", True, (20, 20, 20))
        screen.blit(title, (10, 34))

        if data["player"].moonwalk > 0:
            mw = font.render("Ski-danse !", True, (200, 40, 40))
            screen.blit(mw, (screen_w - 160, 10))
        if data["player"].boost_timer > 0:
            bs = font.render("Boost !", True, (40, 150, 80))
            screen.blit(bs, (screen_w - 110, 34))

        # ca c'est pour afficher les ecrans selon l'etat du jeu
        if state == "splash":
            if splash_image:
                screen.blit(splash_image, (0, 0))
            else:
                fallback = big_font.render("MILANO CORTINA 2026", True, (10, 10, 10))
                screen.blit(fallback, (screen_w // 2 - 200, screen_h // 2 - 20))

        if state == "menu":
            # Menu plus propre: panneau central + ombre
            panel_w, panel_h = 520, 300
            panel_x = screen_w // 2 - panel_w // 2
            panel_y = screen_h // 2 - panel_h // 2
            shadow = pygame.Surface((panel_w + 8, panel_h + 8), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 90))
            screen.blit(shadow, (panel_x - 4, panel_y - 2))

            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((250, 252, 255, 230))
            screen.blit(panel, (panel_x, panel_y))
            pygame.draw.rect(screen, (200, 220, 235), (panel_x, panel_y, panel_w, panel_h), 2)

            title = big_font.render("MILANO-CORTINA 2026", True, (30, 40, 60))
            subtitle = font.render("Ski Runner", True, (60, 80, 110))
            screen.blit(title, (screen_w // 2 - title.get_width() // 2, panel_y + 18))
            screen.blit(subtitle, (screen_w // 2 - subtitle.get_width() // 2, panel_y + 60))

            lines = [
                "ENTRER : demarrer",
                "Fleches : bouger",
                "Espace / P : pause",
                "Passe entre les sapins",
                "Bonus : danse (inverse) / boost (vitesse)",
            ]
            ly = panel_y + 105
            for line in lines:
                txt = font.render(line, True, (20, 30, 40))
                screen.blit(txt, (panel_x + 30, ly))
                ly += 26

            name_line = font.render(f"Prenom: {name_input or '_'}", True, (30, 90, 120))
            screen.blit(name_line, (panel_x + 30, panel_y + panel_h - 38))

            if audio["menu_music"] and not pygame.mixer.get_busy():
                audio["menu_music"].play(loops=-1)

        if paused and state == "playing":
            p = big_font.render("PAUSE", True, (10, 10, 10))
            screen.blit(p, (screen_w // 2 - 70, screen_h // 2 - 20))

        if state == "game_over":
            over = big_font.render("FIN ! R pour rejouer", True, (200, 20, 20))
            screen.blit(over, (screen_w // 2 - 180, screen_h // 2 - 20))
            back = font.render("Entree: retour menu", True, (20, 20, 20))
            screen.blit(back, (screen_w // 2 - 90, screen_h // 2 + 20))
            if leaderboard:
                ly = screen_h // 2 + 50
                title = font.render("Classement:", True, (10, 10, 10))
                screen.blit(title, (screen_w // 2 - 60, ly))
                ly += 22
                for i, (sc, nm) in enumerate(leaderboard, start=1):
                    line = font.render(f"{i}. {nm} - {sc}", True, (10, 10, 10))
                    screen.blit(line, (screen_w // 2 - 80, ly))
                    ly += 20

        if state == "name_entry":
            prompt = big_font.render("Entre ton prenom", True, (10, 10, 10))
            val = font.render(name_input or "_", True, (10, 10, 10))
            hint = font.render("ENTRER pour valider", True, (10, 10, 10))
            screen.blit(prompt, (screen_w // 2 - 160, screen_h // 2 - 40))
            screen.blit(val, (screen_w // 2 - 80, screen_h // 2))
            screen.blit(hint, (screen_w // 2 - 120, screen_h // 2 + 30))

        pygame.display.flip()


if __name__ == "__main__":
    main()
