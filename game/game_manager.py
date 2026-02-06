import random
import pygame
from .config import *
from .entities import Player, Obstacle, Gate, Bonus, Drone, Yeti
from .audio import play_sfx


class GameManager:
    """Gestion de la logique du jeu"""
    
    def __init__(self, screen, images, audio, fonts):
        self.screen = screen
        self.images = images
        self.audio = audio
        self.fonts = fonts
        self.data = None
        self.paused = False
        self.game_over = False
        self.mode = "jo"  # "jo" ou "training"
        self.curling_data = None
        self.biathlon_data = None
        
    def reset_game(self, level=1):
        """Réinitialise le jeu pour un nouveau niveau"""
        player = Player(0, SCREEN_HEIGHT // 2, self.images["skier"])
        player.x = SCREEN_WIDTH // 2 - player.w // 2
        drone = Drone(SCREEN_WIDTH // 2, self.images["drone"])
        
        yeti_count = 0
        if level >= 2:
            yeti_count = 1
        if level >= 3:
            yeti_count = 2
        
        yetis = []
        for i in range(yeti_count):
            x = (SCREEN_WIDTH // 2) + (i * 80) - (40 * (yeti_count - 1))
            yetis.append(Yeti(x, SCREEN_HEIGHT + 60 + i * 60, self.images["yeti"]))
        
        self.data = {
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
            "snowflakes": self._create_snowflakes(120),
        }
        
        self.apply_level_settings()
        return self.data
    
    def _create_snowflakes(self, count):
        """Crée des flocons de neige"""
        flakes = []
        for _ in range(count):
            r = random.choice([2, 2, 3])
            flakes.append({
                "x": random.randint(0, SCREEN_WIDTH),
                "y": random.randint(0, SCREEN_HEIGHT),
                "r": r,
                "spd": random.uniform(25, 60) if r >= 3 else random.uniform(30, 80),
                "drift": random.uniform(-18, 18),
            })
        return flakes
    
    def apply_level_settings(self):
        """Applique les paramètres du niveau actuel"""
        level_cfg = LEVEL_SETTINGS.get(self.data["level"], LEVEL_SETTINGS[5])
        self.data["max_speed"] = level_cfg["max_speed"]
        self.data["speed"] = min(self.data["max_speed"], level_cfg["speed_base"])
        
        gate_min, gate_max = level_cfg["gate_range"]
        self.data["gate_timer"] = random.uniform(gate_min, gate_max)
        self.data["bonus_timer"] = random.uniform(*level_cfg["bonus_range"])
        self.data["finish_score"] = level_cfg["finish_score"]
        self.data["finish_time"] = level_cfg["finish_time"]
        self.data["distance_total"] = level_cfg["distance_m"]
        
        denom = max(1.0, level_cfg["finish_time"] * level_cfg["speed_base"])
        self.data["distance_scale"] = level_cfg["distance_m"] / denom
        self.data["distance_left"] = level_cfg["distance_m"]
    
    def update(self, dt, keys):
        """Met à jour l'état du jeu"""
        if self.paused or self.game_over:
            return
        
        data = self.data
        level_cfg = LEVEL_SETTINGS.get(data["level"], LEVEL_SETTINGS[5])
        
        # Mise à jour du temps
        data["race_time"] += dt
        
        # Mise à jour du joueur
        data["player"].update(dt, keys, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Mise à jour de la distance
        data["distance_left"] -= data["speed"] * dt * data["distance_scale"]
        if data["distance_left"] <= 0:
            data["distance_left"] = 0
        
        # Vitesse progressive
        if data["speed"] < data["max_speed"]:
            data["speed"] = min(data["max_speed"], data["speed"] + 4.0 * dt)
        
        # Défilement du fond
        data["bg_offset"] += data["speed"] * dt
        
        # Mise à jour des flocons
        for f in data["snowflakes"]:
            f["y"] += f["spd"] * dt
            f["x"] += f["drift"] * dt
            if f["x"] < -10:
                f["x"] = SCREEN_WIDTH + 10
            if f["x"] > SCREEN_WIDTH + 10:
                f["x"] = -10
            if f["y"] > SCREEN_HEIGHT + 10:
                f["y"] = random.randint(-200, -20)
                f["x"] = random.randint(0, SCREEN_WIDTH)
        
        # Spawn obstacles
        data["spawn_timer"] += dt
        if data["spawn_timer"] >= 1.2:
            data["spawn_timer"] = 0.0
            rock_img = random.choice(self.images["rock"])
            x = random.randint(50, SCREEN_WIDTH - 50 - rock_img.get_width())
            data["obstacles"].append(Obstacle(x, -60, "rock", data["speed"] + 30, rock_img))
        
        # Spawn portes
        data["gate_timer"] -= dt
        if data["gate_timer"] <= 0:
            gap_min = max(150, 230 - data["level"] * 15)
            gap_max = min(300, gap_min + 100)
            gap_w = random.randint(gap_min, gap_max)
            gap_x = random.randint(40, SCREEN_WIDTH - gap_w - 40)
            data["gates"].append(Gate(-80, gap_x, gap_w, data["speed"] + 30, self.images["tree"], SCREEN_WIDTH))
            gate_min, gate_max = level_cfg["gate_range"]
            data["gate_timer"] = random.uniform(gate_min, gate_max) + level_cfg["extra_gate"]
        
        # Spawn bonus
        data["bonus_timer"] -= dt
        if data["bonus_timer"] <= 0:
            bonus_kind = random.choice(["moonwalk", "speed"])
            bonus_img = self.images["bonus"] if bonus_kind == "moonwalk" else self.images["speed_boost"]
            x = random.randint(60, SCREEN_WIDTH - 60 - bonus_img.get_width())
            data["bonuses"].append(Bonus(x, -40, bonus_img, data["speed"] + 30, bonus_kind))
            data["bonus_timer"] = random.uniform(*level_cfg["bonus_range"])
        
        # Mise à jour obstacles
        for obs in data["obstacles"][:]:
            obs.update(dt)
            if obs.y > SCREEN_HEIGHT + 60:
                data["obstacles"].remove(obs)
        
        # Mise à jour portes
        for gate in data["gates"][:]:
            gate.update(dt)
            if gate.y > SCREEN_HEIGHT + 100:
                data["gates"].remove(gate)
        
        # Mise à jour bonus
        for bonus in data["bonuses"][:]:
            bonus.update(dt)
            if bonus.y > SCREEN_HEIGHT + 40:
                data["bonuses"].remove(bonus)
        
        # Mise à jour drone
        data["drone"].update(dt)
        data["drone"].try_drop(data["obstacles"], data["speed"], self.images["drop"])
        
        # Mise à jour yetis
        speed_bonus = max(0, data["speed"] - 130)
        for yeti in data["yetis"]:
            yeti.update(dt, data["player"].x, data["player"].y, data["speed"], speed_bonus, SCREEN_HEIGHT, SCREEN_WIDTH)
        
        # Collisions
        self._check_collisions()
        
        # Ligne d'arrivée
        if data["distance_left"] <= 0 and data["finish_line"] is None:
            gap_w = 280
            gap_x = (SCREEN_WIDTH - gap_w) // 2
            data["finish_line"] = {"y": -100, "gap_x": gap_x, "gap_w": gap_w}
        
        if data["finish_line"] is not None:
            data["finish_line"]["y"] += (data["speed"] + 30) * dt
            if data["finish_line"]["y"] > data["player"].y and not data["finish_passed"]:
                gap_x = data["finish_line"]["gap_x"]
                gap_w = data["finish_line"]["gap_w"]
                px = data["player"].x
                pw = data["player"].w
                if px + pw < gap_x or px > gap_x + gap_w:
                    # Raté
                    data["win"] = False
                    data["final_done"] = True
                    self.game_over = True
                    play_sfx(self.audio["sfx"], "game_over")
                else:
                    # Gagné
                    data["win"] = True
                    data["race_time_end"] = data["race_time"]
                    data["final_done"] = True
                    self.game_over = True
                data["finish_passed"] = True
    
    def _check_collisions(self):
        """Vérifie les collisions"""
        data = self.data
        player_rect = data["player"].rect()
        
        # Collision avec obstacles
        for obs in data["obstacles"][:]:
            if player_rect.colliderect(obs.rect()):
                if obs.kind == "rock":
                    data["player"].slow_timer = 1.2
                    play_sfx(self.audio["sfx"], "rock")
                elif obs.kind == "drone_drop":
                    data["player"].freeze_timer = 0.8
                    play_sfx(self.audio["sfx"], "rock")
                data["obstacles"].remove(obs)
        
        # Collision avec portes
        for gate in data["gates"]:
            if abs(gate.y - data["player"].y) < 30:
                for tree_rect in gate.tree_rects():
                    if player_rect.colliderect(tree_rect):
                        data["win"] = False
                        data["final_done"] = True
                        self.game_over = True
                        play_sfx(self.audio["sfx"], "game_over")
                        return
                if not gate.passed and gate.y > data["player"].y:
                    gate.passed = True
                    data["score"] += 10
                    play_sfx(self.audio["sfx"], "gate")
        
        # Collision avec bonus
        for bonus in data["bonuses"][:]:
            if player_rect.colliderect(bonus.rect()):
                if bonus.kind == "moonwalk":
                    data["player"].moonwalk = 3.0
                    for yeti in data["yetis"]:
                        yeti.moonwalk_timer = 3.0
                    play_sfx(self.audio["sfx"], "bonus")
                elif bonus.kind == "speed":
                    data["player"].boost_timer = 2.8
                    for yeti in data["yetis"]:
                        yeti.slow_timer = 2.8
                    play_sfx(self.audio["sfx"], "speed")
                data["bonuses"].remove(bonus)
        
        # Collision avec yeti
        for yeti in data["yetis"]:
            if player_rect.colliderect(yeti.rect()):
                yeti.knockback = 0.6
                data["player"].slow_timer = 1.5
                play_sfx(self.audio["sfx"], "rock")
    
    def draw_background(self):
        """Dessine le fond qui défile"""
        bg_tile = self.images["bg_tile"]
        tile_w = bg_tile.get_width()
        tile_h = bg_tile.get_height()
        y = -tile_h + int(self.data["bg_offset"] % tile_h)
        while y < SCREEN_HEIGHT:
            x = 0
            while x < SCREEN_WIDTH:
                self.screen.blit(bg_tile, (x, y))
                x += tile_w
            y += tile_h
    
    def draw_game(self):
        """Dessine l'état du jeu"""
        data = self.data
        
        # Fond
        self.draw_background()
        
        # Flocons
        for f in data["snowflakes"]:
            pygame.draw.circle(self.screen, COLOR_SNOW, (int(f["x"]), int(f["y"])), int(f["r"]))
        
        # Obstacles
        for obs in data["obstacles"]:
            obs.draw(self.screen)
        
        # Portes
        for gate in data["gates"]:
            gate.draw(self.screen)
        
        # Bonus
        for bonus in data["bonuses"]:
            bonus.draw(self.screen)
        
        # Drone
        data["drone"].draw(self.screen)
        
        # Yetis
        for yeti in data["yetis"]:
            yeti.draw(self.screen)
        
        # Joueur
        data["player"].draw(self.screen)
        
        # Ligne d'arrivée
        if data["finish_line"] is not None:
            self._draw_finish_line()
        
        # HUD
        self._draw_hud()
    
    def _draw_finish_line(self):
        """Dessine la ligne d'arrivée"""
        finish = self.data["finish_line"]
        fy = int(finish["y"])
        gap_x = finish["gap_x"]
        gap_w = finish["gap_w"]
        
        # Banderole
        pygame.draw.rect(self.screen, (245, 245, 245), (0, fy - 14, SCREEN_WIDTH, 20))
        for i in range(0, SCREEN_WIDTH, 26):
            col = (20, 20, 20) if ((i // 26) % 2 == 0) else (230, 230, 230)
            pygame.draw.rect(self.screen, col, (i, fy - 14, 26, 20))
        
        # Drapeaux
        left_x = 6
        right_x = SCREEN_WIDTH - 24
        pygame.draw.rect(self.screen, (120, 120, 120), (left_x + 6, fy - 6, 4, 90))
        pygame.draw.rect(self.screen, (120, 120, 120), (right_x + 6, fy - 6, 4, 90))
        pygame.draw.polygon(self.screen, (200, 30, 30), [(left_x + 10, fy + 6), (left_x + 40, fy + 16), (left_x + 10, fy + 26)])
        pygame.draw.polygon(self.screen, (200, 30, 30), [(right_x + 10, fy + 6), (right_x + 40, fy + 16), (right_x + 10, fy + 26)])
        
        banner = self.fonts["small"].render(f"ARRIVEE {int(self.data['distance_total'])} m", True, (200, 30, 30))
        self.screen.blit(banner, (SCREEN_WIDTH // 2 - banner.get_width() // 2, fy - 38))
    
    def _draw_hud(self):
        """Dessine l'interface de jeu"""
        data = self.data
        
        # Panel HUD
        hud_panel = pygame.Surface((SCREEN_WIDTH, 50), pygame.SRCALPHA)
        hud_panel.fill((245, 250, 255, 200))
        pygame.draw.line(hud_panel, (210, 225, 235, 220), (0, 48), (SCREEN_WIDTH, 48), 2)
        self.screen.blit(hud_panel, (0, 0))
        
        # Informations
        hud_text = f"Score: {data['score']}  |  Niveau: {data['level']}  |  Distance: {int(data['distance_left'])} m"
        hud = self.fonts["small"].render(hud_text, True, COLOR_TEXT_DARK)
        self.screen.blit(hud, (14, 14))
        
        # Indicateurs d'effets
        effect_x = SCREEN_WIDTH - 180
        if data["player"].boost_timer > 0:
            boost_txt = self.fonts["small"].render("⚡ BOOST", True, (255, 200, 0))
            self.screen.blit(boost_txt, (effect_x, 14))
            effect_x -= 100
        
        if data["player"].moonwalk > 0:
            moon_txt = self.fonts["small"].render("🌙 MOONWALK", True, (200, 150, 255))
            self.screen.blit(moon_txt, (effect_x, 14))
    
    def draw_game_over(self, leaderboard):
        """Dessine l'écran de fin"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))
        
        panel_w, panel_h = 500, 380
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2
        
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((250, 252, 255, 240))
        pygame.draw.rect(panel, (200, 220, 235, 230), (0, 0, panel_w, panel_h), 3, border_radius=10)
        self.screen.blit(panel, (panel_x, panel_y))
        
        # Titre
        title_text = "🏁 ARRIVÉE !" if self.data.get("win") else "❌ FIN !"
        title_color = (30, 180, 30) if self.data.get("win") else (200, 30, 30)
        over = self.fonts["big"].render(title_text, True, title_color)
        self.screen.blit(over, (SCREEN_WIDTH // 2 - over.get_width() // 2, panel_y + 20))
        
        # Score
        score_y = panel_y + 80
        score_txt = self.fonts["medium"].render(f"Score: {self.data['score']}", True, COLOR_TEXT_DARK)
        self.screen.blit(score_txt, (SCREEN_WIDTH // 2 - score_txt.get_width() // 2, score_y))
        
        # Temps
        if self.data.get("win"):
            time_val = self.data.get("race_time_end", self.data["race_time"])
            time_txt = self.fonts["small"].render(f"Temps: {self._format_time(time_val)}", True, COLOR_TEXT_DARK)
            self.screen.blit(time_txt, (SCREEN_WIDTH // 2 - time_txt.get_width() // 2, score_y + 40))
        
        # Instructions
        instr_y = panel_y + 160
        if self.data.get("win") and self.data["level"] < 5:
            instr = self.fonts["small"].render("R : rejouer  |  ENTREE : niveau suivant", True, COLOR_TEXT_DARK)
        elif self.data.get("win"):
            instr = self.fonts["small"].render("R : rejouer  |  ENTREE : menu", True, COLOR_TEXT_DARK)
        else:
            instr = self.fonts["small"].render("R : rejouer  |  ENTREE : menu", True, COLOR_TEXT_DARK)
        self.screen.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2, instr_y))
        
        # Classement
        if leaderboard and self.mode == "jo" and self.data.get("final_done"):
            ly = panel_y + 210
            title = self.fonts["small"].render("🏆 Classement:", True, COLOR_TEXT_DARK)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, ly))
            ly += 28
            
            medals = {1: "OR", 2: "ARGENT", 3: "BRONZE"}
            for i, (sc, nm, tm) in enumerate(leaderboard[:3], start=1):
                time_txt = self._format_time(tm)
                medal = medals.get(i, f"{i}.")
                line = self.fonts["small"].render(f"{medal} {nm} - {sc} pts - {time_txt}", True, COLOR_TEXT_DARK)
                self.screen.blit(line, (SCREEN_WIDTH // 2 - line.get_width() // 2, ly))
                ly += 24
    
    def _format_time(self, seconds):
        """Formate le temps en MM:SS.S"""
        if seconds is None:
            return "-"
        total = max(0.0, float(seconds))
        minutes = int(total // 60)
        secs = total - minutes * 60
        return f"{minutes}:{secs:04.1f}"
