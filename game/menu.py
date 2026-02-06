import pygame
import random
import os
import math
from .config import *


class Menu:
    """Gestion de tous les menus du jeu"""
    
    def __init__(self, screen, fonts, audio):
        self.screen = screen
        self.fonts = fonts
        self.audio = audio
        self.menu_choice = 0  # 0 = MODE JO, 1 = ENTRAINEMENT, 2 = OPTIONS, 3 = CLASSEMENT
        self.training_choice = 0  # 0 = course, 1 = curling, 2 = biathlon, 3 = retour
        self.options_choice = 0  # 0 = volume, 1 = fenetre, 2 = retour
        self._mouse_pos = None
        self.snowflakes = self._create_snowflakes(110)
        self.splash_image = None
        self.splash_timer = 0.0
        self._load_splash_image()

    def set_mouse_pos(self, pos):
        """Definit une position de souris ajustee (utile si l'ecran est mis a l'echelle)"""
        self._mouse_pos = pos

    def _get_mouse_pos(self):
        return self._mouse_pos if self._mouse_pos is not None else pygame.mouse.get_pos()
        
    def _load_splash_image(self):
        """Charge l'image splash si disponible"""
        splash_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets",
            "24.10.24-Milano-Cortina-1.webp"
        )
        if os.path.exists(splash_path):
            try:
                self.splash_image = pygame.image.load(splash_path).convert()
                self.splash_image = pygame.transform.smoothscale(
                    self.splash_image,
                    (SCREEN_WIDTH, SCREEN_HEIGHT)
                )
            except pygame.error:
                self.splash_image = None
    
    def _create_snowflakes(self, count):
        """Crée des flocons de neige animés"""
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
    
    def update_snowflakes(self, dt):
        """Met à jour l'animation des flocons"""
        for f in self.snowflakes:
            f["y"] += f["spd"] * dt
            f["x"] += f["drift"] * dt
            if f["x"] < -10:
                f["x"] = SCREEN_WIDTH + 10
            if f["x"] > SCREEN_WIDTH + 10:
                f["x"] = -10
            if f["y"] > SCREEN_HEIGHT + 10:
                f["y"] = random.randint(-200, -20)
                f["x"] = random.randint(0, SCREEN_WIDTH)
    
    def draw_snowflakes(self):
        """Dessine les flocons de neige"""
        for f in self.snowflakes:
            pygame.draw.circle(
                self.screen,
                COLOR_SNOW,
                (int(f["x"]), int(f["y"])),
                int(f["r"])
            )
    
    def draw_splash(self, dt):
        """Affiche l'écran splash"""
        self.splash_timer += dt
        if self.splash_image:
            alpha = 255
            if self.splash_timer > 2.0:
                alpha = max(0, int(255 * (1.0 - (self.splash_timer - 2.0) / 0.5)))
            temp_surf = self.splash_image.copy()
            temp_surf.set_alpha(alpha)
            self.screen.blit(temp_surf, (0, 0))
        else:
            self.screen.fill(COLOR_BLUE_SKY)
            title = self.fonts["title"].render(GAME_TITLE, True, COLOR_TEXT_DARK)
            self.screen.blit(
                title,
                (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 50)
            )
        
        if self.splash_timer < 2.5:
            hint_text = "Chargement..."
            hint = self.fonts["small"].render(hint_text, True, COLOR_WHITE)
            self.screen.blit(
                hint,
                (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 100)
            )
        else:
            hint_text = "APPUYEZ SUR ENTREE"
            pulse = 0.6 + 0.4 * math.sin(self.splash_timer * 4.0)
            hint = self.fonts["medium"].render(hint_text, True, COLOR_TEXT_DARK)
            panel_w = hint.get_width() + 50
            panel_h = 46
            panel_x = SCREEN_WIDTH // 2 - panel_w // 2
            panel_y = SCREEN_HEIGHT - 120
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((255, 255, 255, int(170 + 60 * pulse)))
            pygame.draw.rect(panel, (180, 200, 220, 220), (0, 0, panel_w, panel_h), 2, border_radius=8)
            self.screen.blit(panel, (panel_x, panel_y))
            self.screen.blit(
                hint,
                (SCREEN_WIDTH // 2 - hint.get_width() // 2, panel_y + 10)
            )
        
        return self.splash_timer >= 2.5
    
    def draw_main_menu(self, dt):
        """Affiche le menu principal avec animations"""
        # Fond dégradé
        for i in range(SCREEN_HEIGHT):
            shade = 228 + int(18 * (i / SCREEN_HEIGHT))
            self.screen.fill(
                (shade, shade + 6, 255),
                rect=pygame.Rect(0, i, SCREEN_WIDTH, 1)
            )
        
        # Dessiner et animer les flocons
        self.update_snowflakes(dt)
        self.draw_snowflakes()
        
        # Panel principal avec ombre
        panel_w, panel_h = 600, 600
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2
        
        # Ombre portée
        shadow = pygame.Surface((panel_w + 14, panel_h + 14), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 110))
        self.screen.blit(shadow, (panel_x - 7, panel_y - 4))
        
        # Panel avec dégradé
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        for i in range(panel_h):
            shade = 242 + int(8 * (i / panel_h))
            panel.fill(
                (shade, shade + 4, 255, 230),
                rect=pygame.Rect(0, i, panel_w, 1)
            )
        
        # Bordures du panel
        pygame.draw.rect(panel, (210, 225, 240, 200), (0, 0, panel_w, panel_h), 2)
        pygame.draw.rect(panel, (255, 255, 255, 120), (6, 6, panel_w - 12, panel_h - 12), 1)
        
        # En-tête coloré
        pygame.draw.rect(panel, (220, 235, 248, 220), (0, 0, panel_w, 80))
        pygame.draw.line(panel, (170, 195, 215, 200), (24, 76), (panel_w - 24, 76), 2)
        
        self.screen.blit(panel, (panel_x, panel_y))
        
        # Titre principal avec animation
        time_offset = pygame.time.get_ticks() / 1000.0
        title_y_offset = int(2 * pygame.math.Vector2(0, 1).rotate(time_offset * 50).y)
        title = self.fonts["title"].render("JO D'HIVER 2026", True, (30, 60, 120))
        title_shadow = self.fonts["title"].render("JO D'HIVER 2026", True, (180, 190, 210))
        self.screen.blit(
            title_shadow,
            (SCREEN_WIDTH // 2 - title.get_width() // 2 + 2, panel_y + 18 + title_y_offset + 2)
        )
        self.screen.blit(
            title,
            (SCREEN_WIDTH // 2 - title.get_width() // 2, panel_y + 18 + title_y_offset)
        )
        
        # Sous-titre
        subtitle = self.fonts["medium"].render("Ski Runner", True, (60, 80, 110))
        self.screen.blit(
            subtitle,
            (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, panel_y + 50)
        )
        
        # Description
        desc_y = panel_y + 100
        desc_lines = [
            "Dévalez les pistes olympiques !",
            "Évitez les obstacles et franchissez",
            "les portes pour gagner des points."
        ]
        for line in desc_lines:
            desc = self.fonts["small"].render(line, True, COLOR_TEXT_DARK)
            self.screen.blit(
                desc,
                (SCREEN_WIDTH // 2 - desc.get_width() // 2, desc_y)
            )
            desc_y += 26
        
        # Boutons
        btn_y_start = panel_y + 210
        btn_triathlon = pygame.Rect(panel_x + 50, btn_y_start, 500, 50)
        btn_training = pygame.Rect(panel_x + 50, btn_y_start + 70, 500, 50)
        btn_options = pygame.Rect(panel_x + 50, btn_y_start + 140, 500, 50)
        btn_leaderboard = pygame.Rect(panel_x + 50, btn_y_start + 210, 500, 50)
        
        mouse = self._get_mouse_pos()
        
        # Bouton MODE JO
        is_hover_jo = btn_triathlon.collidepoint(mouse)
        jo_color = COLOR_BUTTON_PRIMARY if self.menu_choice == 0 or is_hover_jo else COLOR_BUTTON_SECONDARY
        pygame.draw.rect(self.screen, jo_color, btn_triathlon, border_radius=8)
        pygame.draw.rect(
            self.screen,
            COLOR_WHITE,
            btn_triathlon,
            3 if self.menu_choice == 0 else 1,
            border_radius=8
        )
        jo_txt = self.fonts["medium"].render("MODE JO", True, COLOR_TEXT_LIGHT)
        self.screen.blit(
            jo_txt,
            (btn_triathlon.centerx - jo_txt.get_width() // 2, btn_triathlon.centery - jo_txt.get_height() // 2)
        )
        
        # Bouton ENTRAINEMENT
        is_hover_train = btn_training.collidepoint(mouse)
        train_color = COLOR_BUTTON_PRIMARY if self.menu_choice == 1 or is_hover_train else COLOR_BUTTON_SECONDARY
        pygame.draw.rect(self.screen, train_color, btn_training, border_radius=8)
        pygame.draw.rect(
            self.screen,
            COLOR_WHITE,
            btn_training,
            3 if self.menu_choice == 1 else 1,
            border_radius=8
        )
        train_txt = self.fonts["medium"].render("ENTRAINEMENT", True, COLOR_TEXT_LIGHT)
        self.screen.blit(
            train_txt,
            (btn_training.centerx - train_txt.get_width() // 2, btn_training.centery - train_txt.get_height() // 2)
        )

        # Bouton OPTIONS
        is_hover_opt = btn_options.collidepoint(mouse)
        opt_color = COLOR_BUTTON_PRIMARY if self.menu_choice == 2 or is_hover_opt else COLOR_BUTTON_SECONDARY
        pygame.draw.rect(self.screen, opt_color, btn_options, border_radius=8)
        pygame.draw.rect(
            self.screen,
            COLOR_WHITE,
            btn_options,
            3 if self.menu_choice == 2 else 1,
            border_radius=8
        )
        opt_txt = self.fonts["medium"].render("OPTIONS", True, COLOR_TEXT_LIGHT)
        self.screen.blit(
            opt_txt,
            (btn_options.centerx - opt_txt.get_width() // 2, btn_options.centery - opt_txt.get_height() // 2)
        )

        # Bouton CLASSEMENT
        is_hover_lead = btn_leaderboard.collidepoint(mouse)
        lead_color = COLOR_BUTTON_PRIMARY if self.menu_choice == 3 or is_hover_lead else COLOR_BUTTON_SECONDARY
        pygame.draw.rect(self.screen, lead_color, btn_leaderboard, border_radius=8)
        pygame.draw.rect(
            self.screen,
            COLOR_WHITE,
            btn_leaderboard,
            3 if self.menu_choice == 3 else 1,
            border_radius=8
        )
        lead_txt = self.fonts["medium"].render("CLASSEMENT", True, COLOR_TEXT_LIGHT)
        self.screen.blit(
            lead_txt,
            (btn_leaderboard.centerx - lead_txt.get_width() // 2, btn_leaderboard.centery - lead_txt.get_height() // 2)
        )
        
        # Indication de sélection
        if self.menu_choice == 0:
            sel_txt = "Selection: MODE JO"
        elif self.menu_choice == 1:
            sel_txt = "Selection: ENTRAINEMENT"
        elif self.menu_choice == 2:
            sel_txt = "Selection: OPTIONS"
        else:
            sel_txt = "Selection: CLASSEMENT"
        sel = self.fonts["small"].render(sel_txt, True, COLOR_BUTTON_PRIMARY)
        self.screen.blit(sel, (panel_x + 30, panel_y + panel_h - 80))
        
        # Contrôles
        controls_y = panel_y + panel_h - 50
        controls_lines = [
            "↑/↓ : Choisir | ENTREE : Valider | ECHAP : Quitter"
        ]
        for line in controls_lines:
            ctrl = self.fonts["small"].render(line, True, (100, 120, 140))
            self.screen.blit(
                ctrl,
                (SCREEN_WIDTH // 2 - ctrl.get_width() // 2, controls_y)
            )
            controls_y += 22
        
        # Jouer la musique de menu
        if not pygame.mixer.music.get_busy() and not pygame.mixer.get_busy():
            from .audio import play_music
            play_music(self.audio, "menu")
        
        return {
            "btn_triathlon": btn_triathlon,
            "btn_training": btn_training,
            "btn_options": btn_options,
            "btn_leaderboard": btn_leaderboard
        }
    
    def draw_training_menu(self):
        """Affiche le menu d'entraînement"""
        # Fond
        for i in range(SCREEN_HEIGHT):
            shade = 228 + int(18 * (i / SCREEN_HEIGHT))
            self.screen.fill(
                (shade, shade + 6, 255),
                rect=pygame.Rect(0, i, SCREEN_WIDTH, 1)
            )
        
        # Panel
        panel_w, panel_h = 520, 360
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2
        
        shadow = pygame.Surface((panel_w + 14, panel_h + 14), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 110))
        self.screen.blit(shadow, (panel_x - 7, panel_y - 4))
        
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        for i in range(panel_h):
            shade = 242 + int(8 * (i / panel_h))
            panel.fill(
                (shade, shade + 4, 255, 230),
                rect=pygame.Rect(0, i, panel_w, 1)
            )
        pygame.draw.rect(panel, (210, 225, 240, 200), (0, 0, panel_w, panel_h), 2)
        self.screen.blit(panel, (panel_x, panel_y))
        
        # Titre
        title = self.fonts["big"].render("ENTRAINEMENT", True, COLOR_TEXT_DARK)
        self.screen.blit(
            title,
            (SCREEN_WIDTH // 2 - title.get_width() // 2, panel_y + 18)
        )
        
        # Sélection actuelle
        sel_txt = ["COURSE", "CURLING", "BIATHLON", "RETOUR"][self.training_choice]
        sel = self.fonts["small"].render(f"Sélection: {sel_txt}", True, COLOR_BUTTON_PRIMARY)
        self.screen.blit(sel, (panel_x + 40, panel_y + 62))
        
        # Boutons
        btn_train_course = pygame.Rect(panel_x + 40, panel_y + 100, 440, 46)
        btn_train_curling = pygame.Rect(panel_x + 40, panel_y + 160, 440, 46)
        btn_train_biathlon = pygame.Rect(panel_x + 40, panel_y + 220, 440, 46)
        btn_train_back = pygame.Rect(panel_x + panel_w - 160, panel_y + panel_h - 60, 120, 36)
        
        mouse = self._get_mouse_pos()
        
        for idx, (rect, label, icon_fn) in enumerate([
            (btn_train_course, "COURSE", self._draw_icon_course),
            (btn_train_curling, "CURLING", self._draw_icon_curling),
            (btn_train_biathlon, "BIATHLON", self._draw_icon_biathlon),
        ]):
            is_hover = rect.collidepoint(mouse)
            col = COLOR_BUTTON_PRIMARY if self.training_choice == idx or is_hover else COLOR_BUTTON_SECONDARY
            pygame.draw.rect(self.screen, col, rect, border_radius=6)
            pygame.draw.rect(
                self.screen,
                COLOR_WHITE,
                rect,
                3 if self.training_choice == idx else 1,
                border_radius=6
            )
            icon_fn(rect)
            txt = self.fonts["medium"].render(label, True, COLOR_TEXT_LIGHT)
            self.screen.blit(
                txt,
                (rect.x + 70, rect.centery - txt.get_height() // 2)
            )
        
        # Bouton retour
        is_hover_back = btn_train_back.collidepoint(mouse)
        back_col = COLOR_BUTTON_PRIMARY if self.training_choice == 3 or is_hover_back else COLOR_BUTTON_SECONDARY
        pygame.draw.rect(self.screen, back_col, btn_train_back, border_radius=6)
        pygame.draw.rect(
            self.screen,
            COLOR_WHITE,
            btn_train_back,
            3 if self.training_choice == 3 else 1,
            border_radius=6
        )
        back_txt = self.fonts["small"].render("← RETOUR", True, COLOR_TEXT_LIGHT)
        self.screen.blit(
            back_txt,
            (btn_train_back.centerx - back_txt.get_width() // 2, btn_train_back.centery - back_txt.get_height() // 2)
        )
        
        return {
            "btn_course": btn_train_course,
            "btn_curling": btn_train_curling,
            "btn_biathlon": btn_train_biathlon,
            "btn_back": btn_train_back
        }

    def _draw_icon_course(self, rect):
        """Petit logo 'skieur'"""
        cx = rect.x + 28
        cy = rect.centery
        pygame.draw.circle(self.screen, COLOR_WHITE, (cx, cy - 10), 6, 2)
        pygame.draw.line(self.screen, COLOR_WHITE, (cx, cy - 4), (cx, cy + 8), 2)
        pygame.draw.line(self.screen, COLOR_WHITE, (cx - 8, cy + 2), (cx + 8, cy - 2), 2)
        pygame.draw.line(self.screen, COLOR_WHITE, (cx - 12, cy + 16), (cx + 14, cy + 20), 2)
        pygame.draw.line(self.screen, COLOR_WHITE, (cx - 14, cy + 20), (cx + 10, cy + 26), 2)

    def _draw_icon_curling(self, rect):
        """Petit logo 'pierre de curling'"""
        cx = rect.x + 28
        cy = rect.centery + 2
        pygame.draw.circle(self.screen, COLOR_WHITE, (cx, cy), 9, 2)
        pygame.draw.rect(self.screen, COLOR_WHITE, (cx - 7, cy - 12, 14, 5), 2, border_radius=2)

    def _draw_icon_biathlon(self, rect):
        """Petit logo 'cible'"""
        cx = rect.x + 28
        cy = rect.centery
        pygame.draw.circle(self.screen, COLOR_WHITE, (cx, cy), 10, 2)
        pygame.draw.circle(self.screen, COLOR_WHITE, (cx, cy), 5, 2)
    
    def draw_pause(self):
        """Affiche l'écran de pause"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 30, 40, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Panel de pause
        panel_w, panel_h = 400, 200
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2
        
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((250, 252, 255, 240))
        pygame.draw.rect(panel, (200, 220, 235, 220), (0, 0, panel_w, panel_h), 3, border_radius=10)
        self.screen.blit(panel, (panel_x, panel_y))
        
        # Texte
        p = self.fonts["big"].render("⏸️  PAUSE", True, COLOR_BUTTON_PRIMARY)
        self.screen.blit(
            p,
            (SCREEN_WIDTH // 2 - p.get_width() // 2, panel_y + 30)
        )
        
        hint = self.fonts["small"].render("Espace / P pour reprendre", True, COLOR_TEXT_DARK)
        hint2 = self.fonts["small"].render("Echap : quitter", True, COLOR_TEXT_DARK)
        self.screen.blit(
            hint,
            (SCREEN_WIDTH // 2 - hint.get_width() // 2, panel_y + 100)
        )
        self.screen.blit(
            hint2,
            (SCREEN_WIDTH // 2 - hint2.get_width() // 2, panel_y + 130)
        )

    def draw_options_menu(self, volume, window_label):
        """Affiche le menu Options"""
        # Fond
        for i in range(SCREEN_HEIGHT):
            shade = 228 + int(18 * (i / SCREEN_HEIGHT))
            self.screen.fill(
                (shade, shade + 6, 255),
                rect=pygame.Rect(0, i, SCREEN_WIDTH, 1)
            )

        panel_w, panel_h = 600, 400
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2

        shadow = pygame.Surface((panel_w + 14, panel_h + 14), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 110))
        self.screen.blit(shadow, (panel_x - 7, panel_y - 4))

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        for i in range(panel_h):
            shade = 242 + int(8 * (i / panel_h))
            panel.fill(
                (shade, shade + 4, 255, 230),
                rect=pygame.Rect(0, i, panel_w, 1)
            )
        pygame.draw.rect(panel, (210, 225, 240, 200), (0, 0, panel_w, panel_h), 2)
        self.screen.blit(panel, (panel_x, panel_y))

        title = self.fonts["big"].render("OPTIONS", True, COLOR_TEXT_DARK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, panel_y + 18))

        row_x = panel_x + 40
        row_w = panel_w - 80
        row_h = 70
        vol_row = pygame.Rect(row_x, panel_y + 90, row_w, row_h)
        win_row = pygame.Rect(row_x, panel_y + 180, row_w, row_h)

        # Highlight selection
        for idx, rect in enumerate([vol_row, win_row]):
            if self.options_choice == idx:
                hl = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                hl.fill((255, 255, 255, 80))
                self.screen.blit(hl, (rect.x, rect.y))

        # Volume row
        vol_label = self.fonts["small"].render("VOLUME", True, COLOR_TEXT_DARK)
        self.screen.blit(vol_label, (vol_row.x + 10, vol_row.y + 8))

        gauge_x = vol_row.x + 170
        gauge_y = vol_row.y + 28
        gauge_w = 260
        gauge_h = 18
        pygame.draw.rect(self.screen, (200, 210, 220), (gauge_x, gauge_y, gauge_w, gauge_h))
        fill_w = int(max(0, min(1, volume)) * gauge_w)
        pygame.draw.rect(self.screen, COLOR_BUTTON_PRIMARY, (gauge_x, gauge_y, fill_w, gauge_h))
        pygame.draw.rect(self.screen, (100, 120, 140), (gauge_x, gauge_y, gauge_w, gauge_h), 2)

        vol_value = self.fonts["small"].render(f"{int(volume * 100)}%", True, COLOR_TEXT_DARK)
        self.screen.blit(vol_value, (gauge_x + gauge_w + 18, gauge_y - 2))

        btn_vol_minus = pygame.Rect(gauge_x - 36, gauge_y - 4, 28, 26)
        btn_vol_plus = pygame.Rect(gauge_x + gauge_w + 70, gauge_y - 4, 28, 26)
        for rect, label in [(btn_vol_minus, "-"), (btn_vol_plus, "+")]:
            pygame.draw.rect(self.screen, COLOR_BUTTON_SECONDARY, rect, border_radius=4)
            pygame.draw.rect(self.screen, COLOR_WHITE, rect, 2, border_radius=4)
            txt = self.fonts["small"].render(label, True, COLOR_TEXT_LIGHT)
            self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        # Window row
        win_label = self.fonts["small"].render("FENETRE", True, COLOR_TEXT_DARK)
        self.screen.blit(win_label, (win_row.x + 10, win_row.y + 8))

        value_txt = self.fonts["medium"].render(window_label, True, COLOR_BUTTON_PRIMARY)
        value_x = win_row.x + 170
        value_y = win_row.y + 28
        self.screen.blit(value_txt, (value_x, value_y - value_txt.get_height() // 2))

        btn_win_prev = pygame.Rect(value_x - 40, value_y - 16, 28, 26)
        btn_win_next = pygame.Rect(value_x + value_txt.get_width() + 12, value_y - 16, 28, 26)
        for rect, label in [(btn_win_prev, "<"), (btn_win_next, ">")]:
            pygame.draw.rect(self.screen, COLOR_BUTTON_SECONDARY, rect, border_radius=4)
            pygame.draw.rect(self.screen, COLOR_WHITE, rect, 2, border_radius=4)
            txt = self.fonts["small"].render(label, True, COLOR_TEXT_LIGHT)
            self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        # Retour
        btn_back = pygame.Rect(panel_x + panel_w - 160, panel_y + panel_h - 60, 120, 36)
        is_hover_back = btn_back.collidepoint(self._get_mouse_pos())
        back_col = COLOR_BUTTON_PRIMARY if self.options_choice == 2 or is_hover_back else COLOR_BUTTON_SECONDARY
        pygame.draw.rect(self.screen, back_col, btn_back, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_WHITE, btn_back, 2, border_radius=6)
        back_txt = self.fonts["small"].render("RETOUR", True, COLOR_TEXT_LIGHT)
        self.screen.blit(
            back_txt,
            (btn_back.centerx - back_txt.get_width() // 2, btn_back.centery - back_txt.get_height() // 2)
        )

        hint = self.fonts["small"].render("GAUCHE/DROITE : Ajuster | ENTREE : Retour", True, (100, 120, 140))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, panel_y + panel_h - 90))

        return {
            "btn_vol_minus": btn_vol_minus,
            "btn_vol_plus": btn_vol_plus,
            "btn_win_prev": btn_win_prev,
            "btn_win_next": btn_win_next,
            "btn_back": btn_back,
        }

    def draw_leaderboard(self, leaderboard):
        """Affiche le classement JO"""
        # Fond
        for i in range(SCREEN_HEIGHT):
            shade = 228 + int(18 * (i / SCREEN_HEIGHT))
            self.screen.fill(
                (shade, shade + 6, 255),
                rect=pygame.Rect(0, i, SCREEN_WIDTH, 1)
            )

        panel_w, panel_h = 620, 440
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2

        shadow = pygame.Surface((panel_w + 14, panel_h + 14), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 110))
        self.screen.blit(shadow, (panel_x - 7, panel_y - 4))

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        for i in range(panel_h):
            shade = 242 + int(8 * (i / panel_h))
            panel.fill(
                (shade, shade + 4, 255, 230),
                rect=pygame.Rect(0, i, panel_w, 1)
            )
        pygame.draw.rect(panel, (210, 225, 240, 200), (0, 0, panel_w, panel_h), 2)
        self.screen.blit(panel, (panel_x, panel_y))

        title = self.fonts["big"].render("CLASSEMENT JO", True, COLOR_TEXT_DARK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, panel_y + 18))

        headers = [
            ("RANG", panel_x + 40),
            ("NOM", panel_x + 140),
            ("SCORE", panel_x + 360),
            ("TEMPS", panel_x + 460),
        ]
        for label, hx in headers:
            h = self.fonts["small"].render(label, True, COLOR_TEXT_DARK)
            self.screen.blit(h, (hx, panel_y + 80))

        if not leaderboard:
            empty = self.fonts["medium"].render("Aucun score enregistre", True, COLOR_BUTTON_PRIMARY)
            self.screen.blit(empty, (SCREEN_WIDTH // 2 - empty.get_width() // 2, panel_y + 200))
        else:
            y = panel_y + 120
            for i, (sc, nm, tm) in enumerate(leaderboard[:5], start=1):
                if i == 1:
                    medal = "OR"
                elif i == 2:
                    medal = "ARGENT"
                elif i == 3:
                    medal = "BRONZE"
                else:
                    medal = f"{i}."
                time_txt = self._format_time(tm)
                name_txt = nm[:12]
                row_items = [
                    (medal, panel_x + 40),
                    (name_txt, panel_x + 140),
                    (str(sc), panel_x + 360),
                    (time_txt, panel_x + 460),
                ]
                for text, rx in row_items:
                    row = self.fonts["small"].render(text, True, COLOR_TEXT_DARK)
                    self.screen.blit(row, (rx, y))
                y += 30

        btn_back = pygame.Rect(panel_x + panel_w - 160, panel_y + panel_h - 60, 120, 36)
        is_hover_back = btn_back.collidepoint(self._get_mouse_pos())
        back_col = COLOR_BUTTON_PRIMARY if is_hover_back else COLOR_BUTTON_SECONDARY
        pygame.draw.rect(self.screen, back_col, btn_back, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_WHITE, btn_back, 2, border_radius=6)
        back_txt = self.fonts["small"].render("RETOUR", True, COLOR_TEXT_LIGHT)
        self.screen.blit(
            back_txt,
            (btn_back.centerx - back_txt.get_width() // 2, btn_back.centery - back_txt.get_height() // 2)
        )

        hint = self.fonts["small"].render("ENTREE / ECHAP : Retour", True, (100, 120, 140))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, panel_y + panel_h - 90))

        return {"btn_back": btn_back}

    def _format_time(self, seconds):
        """Formate le temps en MM:SS.S"""
        if seconds is None:
            return "-"
        total = max(0.0, float(seconds))
        minutes = int(total // 60)
        secs = total - minutes * 60
        return f"{minutes}:{secs:04.1f}"

    def handle_options_menu_input(self, event):
        """Gere les entrees du menu Options"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.options_choice = max(0, self.options_choice - 1)
                return "changed"
            if event.key == pygame.K_DOWN:
                self.options_choice = min(2, self.options_choice + 1)
                return "changed"
            if event.key == pygame.K_LEFT:
                if self.options_choice == 0:
                    return "vol_down"
                if self.options_choice == 1:
                    return "window_prev"
            if event.key == pygame.K_RIGHT:
                if self.options_choice == 0:
                    return "vol_up"
                if self.options_choice == 1:
                    return "window_next"
            if event.key == pygame.K_RETURN:
                if self.options_choice == 2:
                    return "back"
            if event.key == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return "mouse_click"
        return None

    def handle_leaderboard_input(self, event):
        """Gere les entrees du classement"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return "back"
            if event.key == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return "mouse_click"
        return None
    
    def handle_main_menu_input(self, event):
        """Gère les entrées du menu principal"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_choice = max(0, self.menu_choice - 1)
                return "changed"
            elif event.key == pygame.K_DOWN:
                self.menu_choice = min(3, self.menu_choice + 1)
                return "changed"
            elif event.key == pygame.K_RETURN:
                if self.menu_choice == 0:
                    return "start_jo"
                elif self.menu_choice == 1:
                    return "training_menu"
                elif self.menu_choice == 2:
                    return "options"
                else:
                    return "leaderboard"
            elif event.key == pygame.K_ESCAPE:
                return "quit"
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return "mouse_click"
        
        return None
    
    def handle_training_menu_input(self, event):
        """Gère les entrées du menu d'entraînement"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.training_choice = max(0, self.training_choice - 1)
                return "changed"
            elif event.key == pygame.K_DOWN:
                self.training_choice = min(3, self.training_choice + 1)
                return "changed"
            elif event.key == pygame.K_RETURN:
                if self.training_choice == 0:
                    return "start_course"
                elif self.training_choice == 1:
                    return "start_curling"
                elif self.training_choice == 2:
                    return "start_biathlon"
                else:
                    return "back_to_main"
            elif event.key == pygame.K_ESCAPE:
                return "back_to_main"
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return "mouse_click"
        
        return None
