"""
Mode Curling pour JO d'hiver 2026
Le joueur doit lancer une pierre de curling pour atteindre le centre de la cible
"""

import pygame
import math
from .config import *
from .audio import play_sfx


class Stone:
    """Pierre de curling"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 20
        self.friction = 0.992
        self.active = False
        self.stopped = False
        
    def update(self, dt):
        """Met à jour la position de la pierre"""
        if self.active and not self.stopped:
            self.x += self.vx * dt
            self.y += self.vy * dt
            
            # Friction
            self.vx *= self.friction
            self.vy *= self.friction
            
            # Arrêt si vitesse très faible
            speed = math.sqrt(self.vx**2 + self.vy**2)
            if speed < 5:
                self.vx = 0
                self.vy = 0
                self.stopped = True
                
            # Limites de la piste
            if self.y < 100:
                self.y = 100
                self.vy = 0
                self.stopped = True
                
    def draw(self, screen):
        """Dessine la pierre"""
        # Pierre (cercle bleu/rouge)
        color = (200, 50, 50) if self.active else (100, 150, 200)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 3)
        
        # Poignée
        handle_y = int(self.y - 5)
        pygame.draw.rect(screen, (220, 220, 220), 
                        (int(self.x) - 8, handle_y - 10, 16, 20), border_radius=3)


class CurlingGame:
    """Gestionnaire du mode Curling"""
    
    def __init__(self, screen, fonts, audio):
        self.screen = screen
        self.fonts = fonts
        self.audio = audio
        self.reset()
        
    def reset(self):
        """Réinitialise le jeu"""
        self.stones = []
        self.current_stone = None
        self.power = 0
        self.power_increasing = True
        self.charging = False
        self.angle = 0
        self.throws_left = 3
        self.game_over = False
        self.best_score = 0
        self.time_left = CURLING_TIME_LIMIT
        self.state = "aiming"  # aiming, throwing, result
        
        # Créer la première pierre
        self.create_new_stone()
        
    def create_new_stone(self):
        """Crée une nouvelle pierre à lancer"""
        start_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT - 80
        self.current_stone = Stone(start_x, start_y)
        self.power = 0
        self.charging = False
        self.state = "aiming"
        
    def update(self, dt, keys):
        """Met à jour le jeu"""
        if self.game_over:
            return
            
        # Timer
        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            self.game_over = True
            return
            
        if self.state == "aiming":
            # Contrôle de l'angle avec les flèches
            if keys[pygame.K_LEFT]:
                self.angle = max(-45, self.angle - 120 * dt)
            if keys[pygame.K_RIGHT]:
                self.angle = min(45, self.angle + 120 * dt)
                
            # Jauge de puissance
            if self.charging:
                if self.power_increasing:
                    self.power += 150 * dt
                    if self.power >= 100:
                        self.power = 100
                        self.power_increasing = False
                else:
                    self.power -= 150 * dt
                    if self.power <= 0:
                        self.power = 0
                        self.power_increasing = True
                        
        elif self.state == "throwing":
            # Mise à jour de la pierre en mouvement
            self.current_stone.update(dt)
            for stone in self.stones:
                stone.update(dt)
            self._handle_collisions()
            
            # Vérifier si la pierre s'est arrêtée
            if self.current_stone.stopped:
                self.stones.append(self.current_stone)
                score = self.calculate_score(self.current_stone)
                self.best_score = max(self.best_score, score)
                
                self.throws_left -= 1
                if self.throws_left > 0:
                    self.create_new_stone()
                else:
                    self.game_over = True

    def _handle_collisions(self):
        """Gere les collisions entre la pierre actuelle et les precedentes"""
        if not self.current_stone:
            return
        for other in self.stones:
            if other is self.current_stone:
                continue
            dx = other.x - self.current_stone.x
            dy = other.y - self.current_stone.y
            dist = math.sqrt(dx * dx + dy * dy)
            min_dist = self.current_stone.radius + other.radius
            if dist > 0 and dist < min_dist:
                nx = dx / dist
                ny = dy / dist
                overlap = min_dist - dist
                self.current_stone.x -= nx * overlap * 0.5
                self.current_stone.y -= ny * overlap * 0.5
                other.x += nx * overlap * 0.5
                other.y += ny * overlap * 0.5

                transfer = 0.6
                other.vx += self.current_stone.vx * transfer
                other.vy += self.current_stone.vy * transfer
                self.current_stone.vx *= 0.6
                self.current_stone.vy *= 0.6

                other.active = True
                other.stopped = False
                    
    def handle_input(self, event):
        """Gère les entrées clavier"""
        if event.type == pygame.KEYDOWN:
            if self.state == "aiming":
                if event.key == pygame.K_SPACE:
                    if not self.charging:
                        # Commencer à charger
                        self.charging = True
                        self.power = 0
                        self.power_increasing = True
                    else:
                        # Lancer !
                        self.launch_stone()
                        
            elif self.state == "throwing":
                pass  # Attendre que la pierre s'arrête
                
            # Recommencer
            if self.game_over and event.key == pygame.K_r:
                self.reset()
                
    def launch_stone(self):
        """Lance la pierre"""
        if self.current_stone and self.state == "aiming":
            # Calculer la vitesse en fonction de la puissance et de l'angle
            speed = self.power * 5.2
            angle_rad = math.radians(self.angle)
            
            self.current_stone.vx = speed * math.sin(angle_rad)
            self.current_stone.vy = -speed * math.cos(angle_rad)
            self.current_stone.active = True
            
            self.state = "throwing"
            self.charging = False
            
            # Son de lancement
            play_sfx(self.audio["sfx"], "curling_slide")
            
    def calculate_score(self, stone):
        """Calcule le score en fonction de la distance au centre"""
        target_x = SCREEN_WIDTH // 2
        target_y = 150
        
        distance = math.sqrt((stone.x - target_x)**2 + (stone.y - target_y)**2)
        
        # Score basé sur la proximité
        if distance < 30:
            return 100
        elif distance < 60:
            return 80
        elif distance < 90:
            return 60
        elif distance < 120:
            return 40
        elif distance < 150:
            return 20
        else:
            return 0
            
    def draw(self):
        """Dessine le jeu"""
        # Fond
        self.screen.fill((240, 245, 255))
        
        # Piste de curling
        piste_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 50, 400, SCREEN_HEIGHT - 150)
        pygame.draw.rect(self.screen, (220, 235, 245), piste_rect)
        pygame.draw.rect(self.screen, (180, 200, 220), piste_rect, 3)
        
        # Cible (cercles concentriques)
        target_x = SCREEN_WIDTH // 2
        target_y = 150
        
        colors = [(200, 50, 50), (255, 255, 255), (50, 100, 200), (255, 255, 255)]
        radii = [120, 90, 60, 30]
        
        for i, (color, radius) in enumerate(zip(colors, radii)):
            pygame.draw.circle(self.screen, color, (target_x, target_y), radius)
            
        # Centre
        pygame.draw.circle(self.screen, (255, 215, 0), (target_x, target_y), 10)
        
        # Pierres lancées
        for stone in self.stones:
            stone.draw(self.screen)
            
        # Pierre actuelle
        if self.current_stone and not self.game_over:
            self.current_stone.draw(self.screen)
            
            # Flèche de direction (en mode visée)
            if self.state == "aiming":
                arrow_length = 60 + self.power * 0.5
                angle_rad = math.radians(self.angle)
                end_x = self.current_stone.x + arrow_length * math.sin(angle_rad)
                end_y = self.current_stone.y - arrow_length * math.cos(angle_rad)
                
                pygame.draw.line(
                    self.screen,
                    (255, 200, 0),
                    (int(self.current_stone.x), int(self.current_stone.y)),
                    (int(end_x), int(end_y)),
                    4
                )
                
                # Pointe de flèche
                arrow_size = 12
                tip_angle1 = angle_rad + math.radians(150)
                tip_angle2 = angle_rad - math.radians(150)
                
                tip1_x = end_x + arrow_size * math.cos(tip_angle1)
                tip1_y = end_y + arrow_size * math.sin(tip_angle1)
                tip2_x = end_x + arrow_size * math.cos(tip_angle2)
                tip2_y = end_y + arrow_size * math.sin(tip_angle2)
                
                pygame.draw.polygon(
                    self.screen,
                    (255, 200, 0),
                    [(int(end_x), int(end_y)), (int(tip1_x), int(tip1_y)), (int(tip2_x), int(tip2_y))]
                )
        
        # HUD
        self.draw_hud()
        
        # Game Over
        if self.game_over:
            self.draw_game_over()
            
    def draw_hud(self):
        """Dessine l'interface"""
        # Panel HUD
        hud_h = 50
        panel = pygame.Surface((SCREEN_WIDTH, hud_h), pygame.SRCALPHA)
        panel.fill((245, 250, 255, 200))
        pygame.draw.line(panel, (210, 225, 235), (0, hud_h - 2), (SCREEN_WIDTH, hud_h - 2), 2)
        self.screen.blit(panel, (0, 0))
        
        # Infos
        info_text = f"Lancers: {self.throws_left}  |  Meilleur: {self.best_score} pts  |  Temps: {self.time_left:.1f}s"
        info = self.fonts["small"].render(info_text, True, COLOR_TEXT_DARK)
        self.screen.blit(info, (20, 14))
        
        # Jauge de puissance (si en train de charger)
        if self.charging and self.state == "aiming":
            gauge_x = SCREEN_WIDTH - 220
            gauge_y = 12
            gauge_w = 200
            gauge_h = 26
            
            # Fond
            pygame.draw.rect(self.screen, (200, 210, 220), (gauge_x, gauge_y, gauge_w, gauge_h))
            # Remplissage
            fill_w = int((self.power / 100) * gauge_w)
            color = (50, 200, 50) if self.power < 70 else (255, 200, 0) if self.power < 90 else (255, 50, 50)
            pygame.draw.rect(self.screen, color, (gauge_x, gauge_y, fill_w, gauge_h))
            # Bordure
            pygame.draw.rect(self.screen, (100, 120, 140), (gauge_x, gauge_y, gauge_w, gauge_h), 2)
            
            # Texte
            power_txt = self.fonts["small"].render(f"Puissance: {int(self.power)}%", True, COLOR_TEXT_DARK)
            self.screen.blit(power_txt, (gauge_x + 5, gauge_y + 4))
            
        # Instructions
        if self.state == "aiming" and not self.charging:
            hint = self.fonts["small"].render("← → : Angle | ESPACE : Charger", True, (100, 120, 140))
            self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))
        elif self.charging:
            hint = self.fonts["small"].render("ESPACE : Lancer !", True, (255, 100, 0))
            self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))
            
    def draw_game_over(self):
        """Dessine l'écran de fin"""
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((15, 20, 30, 140))
        self.screen.blit(overlay, (0, 0))
        
        # Panel
        panel_w, panel_h = 460, 280
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2
        
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((250, 252, 255, 240))
        pygame.draw.rect(panel, (200, 220, 235), (0, 0, panel_w, panel_h), 3, border_radius=10)
        self.screen.blit(panel, (panel_x, panel_y))
        
        # Titre
        title_text = "🥌 CURLING TERMINÉ !"
        title = self.fonts["big"].render(title_text, True, COLOR_TEXT_DARK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, panel_y + 30))
        
        # Score
        score_text = f"Meilleur score: {self.best_score} pts"
        score = self.fonts["medium"].render(score_text, True, COLOR_BUTTON_PRIMARY)
        self.screen.blit(score, (SCREEN_WIDTH // 2 - score.get_width() // 2, panel_y + 100))
        
        # Évaluation
        if self.best_score >= 100:
            eval_text = "🏆 PARFAIT ! Centre absolu !"
            eval_color = (255, 215, 0)
        elif self.best_score >= 80:
            eval_text = "🥈 Excellent tir !"
            eval_color = (50, 200, 50)
        elif self.best_score >= 60:
            eval_text = "🥉 Bon tir !"
            eval_color = (100, 150, 200)
        else:
            eval_text = "Continuez à vous entraîner !"
            eval_color = (150, 150, 150)
            
        evaluation = self.fonts["small"].render(eval_text, True, eval_color)
        self.screen.blit(evaluation, (SCREEN_WIDTH // 2 - evaluation.get_width() // 2, panel_y + 160))
        
        # Instructions
        hint = self.fonts["small"].render("R : Rejouer  |  ECHAP : Menu", True, COLOR_TEXT_DARK)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, panel_y + 220))
