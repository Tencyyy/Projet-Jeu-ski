"""
Mode Biathlon pour JO d'hiver 2026
Le joueur doit tirer sur des cibles avec un arc
"""

import pygame
import random
import math
from .config import *
from .audio import play_sfx


class Target:
    """Cible de tir"""
    
    def __init__(self, x, y, size=40):
        self.x = x
        self.y = y
        self.size = size
        self.hit = False
        self.hit_animation = 0
        self.vx = random.choice([-1, 1]) * random.uniform(30, 60)
        self.vy = random.choice([-1, 1]) * random.uniform(20, 40)
        
    def draw(self, screen, fonts):
        """Dessine la cible"""
        if self.hit:
            # Animation de touché
            if self.hit_animation < 0.3:
                # Flash blanc
                pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.size)
            else:
                # Cible touchée (vert)
                pygame.draw.circle(screen, (50, 200, 50), (int(self.x), int(self.y)), self.size)
                pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.size, 3)
                # X au centre
                offset = self.size // 2
                pygame.draw.line(screen, (255, 255, 255),
                               (self.x - offset//2, self.y - offset//2),
                               (self.x + offset//2, self.y + offset//2), 4)
                pygame.draw.line(screen, (255, 255, 255),
                               (self.x + offset//2, self.y - offset//2),
                               (self.x - offset//2, self.y + offset//2), 4)
        else:
            # Cible non touchée (cercles concentriques)
            pygame.draw.circle(screen, (200, 50, 50), (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), int(self.size * 0.7))
            pygame.draw.circle(screen, (200, 50, 50), (int(self.x), int(self.y)), int(self.size * 0.4))
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), int(self.size * 0.2))
            
    def update(self, dt, bounds):
        """Met à jour l'animation"""
        if self.hit:
            self.hit_animation += dt
            return
        # Mouvement simple dans une zone bornée
        x_min, x_max, y_min, y_max = bounds
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x < x_min or self.x > x_max:
            self.vx *= -1
            self.x = max(x_min, min(x_max, self.x))
        if self.y < y_min or self.y > y_max:
            self.vy *= -1
            self.y = max(y_min, min(y_max, self.y))


class Arrow:
    """Flèche tirée"""
    
    def __init__(self, x, y, angle, power):
        self.x = x
        self.y = y
        self.angle = angle
        self.power = power
        self.speed = power * 8
        self.active = True
        
        # Vitesse
        angle_rad = math.radians(angle)
        self.vx = self.speed * math.cos(angle_rad)
        self.vy = self.speed * math.sin(angle_rad)
        
    def update(self, dt):
        """Met à jour la position de la flèche"""
        if self.active:
            self.x += self.vx * dt
            self.y += self.vy * dt
            
            # Désactiver si sort de l'écran
            if self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT:
                self.active = False
                
    def draw(self, screen):
        """Dessine la flèche"""
        if self.active:
            # Corps de la flèche
            length = 25
            angle_rad = math.radians(self.angle)
            end_x = self.x + length * math.cos(angle_rad)
            end_y = self.y + length * math.sin(angle_rad)
            
            pygame.draw.line(screen, (150, 100, 50), 
                           (int(self.x), int(self.y)), 
                           (int(end_x), int(end_y)), 3)
            
            # Pointe
            pygame.draw.circle(screen, (180, 180, 180), (int(end_x), int(end_y)), 4)


class BiathlonGame:
    """Gestionnaire du mode Biathlon"""
    
    def __init__(self, screen, fonts, audio):
        self.screen = screen
        self.fonts = fonts
        self.audio = audio
        self.reset()
        
    def reset(self):
        """Réinitialise le jeu"""
        self.targets = []
        self.arrows = []
        self.crosshair_x = SCREEN_WIDTH // 2
        self.crosshair_y = SCREEN_HEIGHT // 2
        self.active_target = None
        self.power = 0
        self.power_increasing = True
        self.charging = False
        self.shots_left = 5
        self.hits = 0
        self.game_over = False
        self.time_left = BIATHLON_TIME_LIMIT
        self.target_bounds = None
        
        # Créer les cibles
        self.create_targets()
        self.select_next_target()

    def select_next_target(self):
        """Préselectionne la prochaine cible non touchée"""
        self.active_target = None
        for target in self.targets:
            if not target.hit:
                self.active_target = target
                # Placer la visée sur la cible pour aider le joueur
                self.crosshair_x = target.x
                self.crosshair_y = target.y
                return
        
    def create_targets(self):
        """Crée les cibles aléatoirement"""
        self.targets = []
        target_zone_x = (200, SCREEN_WIDTH - 200)
        target_zone_y = (100, 350)
        self.target_bounds = (target_zone_x[0] + 20, target_zone_x[1] - 20, target_zone_y[0] + 20, target_zone_y[1] - 20)
        
        for i in range(5):
            x = random.randint(target_zone_x[0], target_zone_x[1])
            y = random.randint(target_zone_y[0], target_zone_y[1])
            size = random.randint(30, 45)
            
            # Éviter les chevauchements
            overlap = True
            attempts = 0
            while overlap and attempts < 20:
                overlap = False
                for target in self.targets:
                    dist = math.sqrt((x - target.x)**2 + (y - target.y)**2)
                    if dist < (size + target.size + 20):
                        overlap = True
                        x = random.randint(target_zone_x[0], target_zone_x[1])
                        y = random.randint(target_zone_y[0], target_zone_y[1])
                        break
                attempts += 1
                
            self.targets.append(Target(x, y, size))
            
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
            
        # Déplacement de la visée
        speed = 300
        if keys[pygame.K_LEFT]:
            self.crosshair_x = max(50, self.crosshair_x - speed * dt)
        if keys[pygame.K_RIGHT]:
            self.crosshair_x = min(SCREEN_WIDTH - 50, self.crosshair_x + speed * dt)
        if keys[pygame.K_UP]:
            self.crosshair_y = max(50, self.crosshair_y - speed * dt)
        if keys[pygame.K_DOWN]:
            self.crosshair_y = min(SCREEN_HEIGHT - 50, self.crosshair_y + speed * dt)
            
        # Jauge de puissance
        if self.charging:
            if self.power_increasing:
                self.power += 200 * dt
                if self.power >= 100:
                    self.power = 100
                    self.power_increasing = False
            else:
                self.power -= 200 * dt
                if self.power <= 0:
                    self.power = 0
                    self.power_increasing = True
                    
        # Mise à jour des flèches
        for arrow in self.arrows[:]:
            arrow.update(dt)
            
            # Vérifier les collisions avec les cibles
            if arrow.active:
                for target in self.targets:
                    if not target.hit:
                        dist = math.sqrt((arrow.x - target.x)**2 + (arrow.y - target.y)**2)
                        if dist < target.size + 6:
                            # Touché !
                            target.hit = True
                            target.hit_animation = 0
                            arrow.active = False
                            self.hits += 1
                            play_sfx(self.audio["sfx"], "bonus")
                            self.select_next_target()
                            break
                            
            # Retirer les flèches inactives
            if not arrow.active:
                self.arrows.remove(arrow)
                
        # Mise à jour des cibles
        for target in self.targets:
            target.update(dt, self.target_bounds)
            
        # Vérifier fin de jeu
        if self.shots_left == 0 and len(self.arrows) == 0:
            self.game_over = True
            
    def handle_input(self, event):
        """Gère les entrées clavier"""
        if event.type == pygame.KEYDOWN:
            if not self.game_over:
                if event.key == pygame.K_SPACE:
                    if self.shots_left > 0:
                        if not self.charging:
                            # Commencer à charger
                            self.charging = True
                            self.power = 0
                            self.power_increasing = True
                        else:
                            # Tirer !
                            self.shoot()
                            
            # Recommencer
            if self.game_over and event.key == pygame.K_r:
                self.reset()
                
    def shoot(self):
        """Tire une flèche"""
        if self.shots_left > 0 and self.charging:
            # Position du tireur (en bas au centre)
            shooter_x = SCREEN_WIDTH // 2
            shooter_y = SCREEN_HEIGHT - 80
            
            # Calculer l'angle vers le réticule
            dx = self.crosshair_x - shooter_x
            dy = self.crosshair_y - shooter_y
            angle = math.degrees(math.atan2(dy, dx))
            
            # Créer la flèche
            arrow = Arrow(shooter_x, shooter_y, angle, self.power)
            self.arrows.append(arrow)
            
            self.shots_left -= 1
            self.charging = False
            self.power = 0
            
            # Son de tir
            play_sfx(self.audio["sfx"], "arrow_shot")
            
    def draw(self):
        """Dessine le jeu"""
        # Fond (montagne enneigée)
        for i in range(SCREEN_HEIGHT):
            shade = 228 + int(18 * (i / SCREEN_HEIGHT))
            self.screen.fill((shade, shade + 6, 255), rect=pygame.Rect(0, i, SCREEN_WIDTH, 1))
            
        # Zone de tir
        zone_rect = pygame.Rect(100, 80, SCREEN_WIDTH - 200, 300)
        pygame.draw.rect(self.screen, (245, 250, 255, 100), zone_rect)
        pygame.draw.rect(self.screen, (180, 200, 220), zone_rect, 2)

        # Mise en évidence de la cible préselectionnée
        if self.active_target and not self.active_target.hit:
            pygame.draw.circle(
                self.screen,
                (255, 215, 0),
                (int(self.active_target.x), int(self.active_target.y)),
                self.active_target.size + 8,
                3
            )
        
        # Cibles
        for target in self.targets:
            target.draw(self.screen, self.fonts)
            
        # Flèches
        for arrow in self.arrows:
            arrow.draw(self.screen)
            
        # Tireur (en bas)
        shooter_x = SCREEN_WIDTH // 2
        shooter_y = SCREEN_HEIGHT - 80
        
        # Corps
        pygame.draw.circle(self.screen, (50, 100, 150), (shooter_x, shooter_y - 20), 15)
        # Arc
        pygame.draw.arc(self.screen, (139, 69, 19), 
                       (shooter_x - 25, shooter_y - 10, 50, 40), 
                       math.radians(200), math.radians(340), 4)
        
        # Réticule
        if not self.game_over:
            crosshair_size = 20
            # Croix
            pygame.draw.line(self.screen, (255, 0, 0),
                           (self.crosshair_x - crosshair_size, self.crosshair_y),
                           (self.crosshair_x + crosshair_size, self.crosshair_y), 2)
            pygame.draw.line(self.screen, (255, 0, 0),
                           (self.crosshair_x, self.crosshair_y - crosshair_size),
                           (self.crosshair_x, self.crosshair_y + crosshair_size), 2)
            # Cercle
            pygame.draw.circle(self.screen, (255, 0, 0), 
                             (int(self.crosshair_x), int(self.crosshair_y)), 
                             crosshair_size, 2)
        
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
        accuracy = (self.hits / (5 - self.shots_left) * 100) if (5 - self.shots_left) > 0 else 0
        info_text = f"Tirs: {self.shots_left}  |  Cibles: {self.hits}/5  |  Précision: {accuracy:.0f}%  |  Temps: {self.time_left:.1f}s"
        info = self.fonts["small"].render(info_text, True, COLOR_TEXT_DARK)
        self.screen.blit(info, (20, 14))
        
        # Jauge de puissance (si en train de charger)
        if self.charging:
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
        if not self.charging and not self.game_over:
            hint = self.fonts["small"].render("Flèches : Viser | ESPACE : Charger et tirer", True, (100, 120, 140))
            self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))
        elif self.charging:
            hint = self.fonts["small"].render("ESPACE : Tirer !", True, (255, 100, 0))
            self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))
            
    def draw_game_over(self):
        """Dessine l'écran de fin"""
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((15, 20, 30, 140))
        self.screen.blit(overlay, (0, 0))
        
        # Panel
        panel_w, panel_h = 460, 300
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2
        
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((250, 252, 255, 240))
        pygame.draw.rect(panel, (200, 220, 235), (0, 0, panel_w, panel_h), 3, border_radius=10)
        self.screen.blit(panel, (panel_x, panel_y))
        
        # Titre
        title_text = "🎯 BIATHLON TERMINÉ !"
        title = self.fonts["big"].render(title_text, True, COLOR_TEXT_DARK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, panel_y + 30))
        
        # Statistiques
        total_shots = 5
        accuracy = (self.hits / total_shots * 100) if total_shots > 0 else 0
        
        hits_text = f"Cibles touchées: {self.hits}/5"
        hits = self.fonts["medium"].render(hits_text, True, COLOR_TEXT_DARK)
        self.screen.blit(hits, (SCREEN_WIDTH // 2 - hits.get_width() // 2, panel_y + 90))
        
        acc_text = f"Précision: {accuracy:.0f}%"
        acc = self.fonts["small"].render(acc_text, True, COLOR_BUTTON_PRIMARY)
        self.screen.blit(acc, (SCREEN_WIDTH // 2 - acc.get_width() // 2, panel_y + 140))
        
        # Évaluation
        if self.hits == 5:
            eval_text = "🏆 SANS FAUTE ! Tireur d'élite !"
            eval_color = (255, 215, 0)
        elif self.hits >= 4:
            eval_text = "🥈 Excellent tir !"
            eval_color = (50, 200, 50)
        elif self.hits >= 3:
            eval_text = "🥉 Bon tir !"
            eval_color = (100, 150, 200)
        else:
            eval_text = "Continuez à vous entraîner !"
            eval_color = (150, 150, 150)
            
        evaluation = self.fonts["small"].render(eval_text, True, eval_color)
        self.screen.blit(evaluation, (SCREEN_WIDTH // 2 - evaluation.get_width() // 2, panel_y + 180))
        
        # Instructions
        hint = self.fonts["small"].render("R : Rejouer  |  ECHAP : Menu", True, COLOR_TEXT_DARK)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, panel_y + 240))
