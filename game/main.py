"""
JO d'hiver 2026 - Ski Runner
Jeu de ski olympique par le Groupe 1

Contrôles:
- Flèches: Déplacer le skieur
- P / Espace: Pause
- R: Rejouer (après game over)
- ENTREE: Valider les choix
- ECHAP: Quitter
"""

import pygame
import sys
from game.config import *
from game.assets import ensure_assets, load_images
from game.audio import build_audio, play_music, stop_music, set_master_volume
from game.menu import Menu
from game.game_manager import GameManager
from game.curling import CurlingGame
from game.biathlon import BiathlonGame


def create_visual_effects(screen_w, screen_h):
    """Crée les effets visuels (vignette, grain)"""
    # Vignette douce sur les bords
    vignette = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    pygame.draw.rect(vignette, (0, 0, 0, 0), (0, 0, screen_w, screen_h))
    pygame.draw.rect(vignette, (10, 20, 30, 70), (0, 0, screen_w, screen_h), 40)
    
    # Grain neigeux
    import random
    grain = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    random.seed(7)
    for _ in range(240):
        x = random.randint(0, screen_w - 1)
        y = random.randint(0, screen_h - 1)
        r = random.choice([1, 1, 2])
        alpha = random.randint(30, 80)
        pygame.draw.circle(grain, (255, 255, 255, alpha), (x, y), r)
    
    return vignette, grain


def init_display(mode_index):
    """Initialise l'affichage et les infos de mise a l'echelle"""
    label, size = WINDOW_PRESETS[mode_index]
    if label == "PLEIN ECRAN":
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        actual_width, actual_height = screen.get_size()
    else:
        screen = pygame.display.set_mode(size)
        actual_width, actual_height = size


    virtual_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    scale_x = actual_width / SCREEN_WIDTH
    scale_y = actual_height / SCREEN_HEIGHT
    scale = min(scale_x, scale_y)
    scaled_width = int(SCREEN_WIDTH * scale)
    scaled_height = int(SCREEN_HEIGHT * scale)
    offset_x = (actual_width - scaled_width) // 2
    offset_y = (actual_height - scaled_height) // 2

    return {
        "label": label,
        "screen": screen,
        "virtual": virtual_screen,
        "actual_width": actual_width,
        "actual_height": actual_height,
        "scale": scale,
        "scaled_width": scaled_width,
        "scaled_height": scaled_height,
        "offset_x": offset_x,
        "offset_y": offset_y,
    }


def map_mouse(pos, display):
    """Convertit la souris ecran -> coordonnees de la surface virtuelle"""
    mx, my = pos
    scale = display["scale"]
    if scale <= 0:
        return pos
    mx = int((mx - display["offset_x"]) / scale)
    my = int((my - display["offset_y"]) / scale)
    mx = max(0, min(SCREEN_WIDTH - 1, mx))
    my = max(0, min(SCREEN_HEIGHT - 1, my))
    return mx, my


def main():
    """Fonction principale du jeu"""
    # Initialisation Pygame
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    
    # Création de la fenêtre (plein écran ou fenêtré selon config)
    display_mode_index = 0 if FULLSCREEN else 2
    display = init_display(display_mode_index)
    screen = display["screen"]
    virtual_screen = display["virtual"]
    
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()
    
    # Chargement des polices
    fonts = {
        "small": pygame.font.SysFont(FONT_NAME, FONT_SIZE_SMALL),
        "medium": pygame.font.SysFont(FONT_NAME, FONT_SIZE_MEDIUM),
        "big": pygame.font.SysFont(FONT_NAME, FONT_SIZE_MEDIUM),
        "title": pygame.font.SysFont(FONT_NAME, FONT_SIZE_LARGE, bold=True)
    }
    
    # Chargement des assets
    print("Chargement des ressources...")
    asset_paths = ensure_assets()
    images = load_images(asset_paths)
    audio = build_audio()
    print("Ressources chargées!")

    volume = DEFAULT_VOLUME
    set_master_volume(audio, volume)
    
    # Création des gestionnaires
    menu = Menu(virtual_screen, fonts, audio)
    game = GameManager(virtual_screen, images, audio, fonts)
    curling = CurlingGame(virtual_screen, fonts, audio)
    biathlon = BiathlonGame(virtual_screen, fonts, audio)
    
    # Effets visuels
    vignette, grain = create_visual_effects(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Variables d'état
    state = "splash"  # splash, menu, training_menu, options, leaderboard, playing, game_over, name_entry, curling, biathlon
    name_input = ""
    leaderboard = []
    pending_score = None
    pending_time = None
    jo_pending_score = None
    jo_pending_time = None
    jo_stage = "ski"  # ski -> curling -> biathlon
    jo_transition_timer = 0.0
    splash_ready = False
    
    # Boucle principale
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        # Surface de travail (toujours virtuelle, puis mise a l'echelle si besoin)
        work_surface = virtual_screen

        # Souris ajustee pour la surface virtuelle
        menu.set_mouse_pos(map_mouse(pygame.mouse.get_pos(), display))
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # F11 pour basculer plein écran (bonus!)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                print("Basculement plein ecran: utilisez le menu Options.")
            
            elif event.type == pygame.KEYDOWN:
                # Splash screen
                if state == "splash":
                    if splash_ready and event.key == pygame.K_RETURN:
                        state = "menu"
                
                # Menu principal
                elif state == "menu":
                    result = menu.handle_main_menu_input(event)
                    if result == "start_jo":
                        if name_input.strip() == "":
                            state = "name_entry"
                            game.mode = "jo"
                            jo_stage = "ski"
                            jo_pending_score = None
                            jo_pending_time = None
                        else:
                            game.mode = "jo"
                            game.reset_game(level=1)
                            state = "playing"
                            game.paused = False
                            game.game_over = False
                            jo_stage = "ski"
                            jo_transition_timer = 0.0
                            jo_pending_score = None
                            jo_pending_time = None
                            stop_music()
                            play_music(audio, "game")
                    
                    elif result == "training_menu":
                        state = "training_menu"
                    
                    elif result == "options":
                        state = "options"
                    
                    elif result == "leaderboard":
                        state = "leaderboard"
                    
                    elif result == "quit":
                        running = False
                    
                    elif result == "mouse_click":
                        mx, my = map_mouse(event.pos, display)
                        buttons = menu.draw_main_menu(0)
                        if buttons["btn_triathlon"].collidepoint(mx, my):
                            menu.menu_choice = 0
                        elif buttons["btn_training"].collidepoint(mx, my):
                            menu.menu_choice = 1
                        elif buttons["btn_options"].collidepoint(mx, my):
                            menu.menu_choice = 2
                
                # Menu d'entraînement
                elif state == "training_menu":
                    result = menu.handle_training_menu_input(event)
                    if result == "start_course":
                        game.mode = "training"
                        game.reset_game(level=1)
                        state = "playing"
                        jo_stage = "ski"
                        jo_transition_timer = 0.0
                        stop_music()
                        play_music(audio, "game")
                    
                    elif result == "start_curling":
                        # Lancer le mode curling
                        game.mode = "training"
                        curling.reset()
                        state = "curling"
                        stop_music()
                        play_music(audio, "game")
                    
                    elif result == "start_biathlon":
                        # Lancer le mode biathlon
                        game.mode = "training"
                        biathlon.reset()
                        state = "biathlon"
                        stop_music()
                        play_music(audio, "game")
                    
                    elif result == "back_to_main":
                        state = "menu"
                    
                    elif result == "mouse_click":
                        mx, my = map_mouse(event.pos, display)
                        buttons = menu.draw_training_menu()
                        if buttons["btn_course"].collidepoint(mx, my):
                            menu.training_choice = 0
                        elif buttons["btn_curling"].collidepoint(mx, my):
                            menu.training_choice = 1
                        elif buttons["btn_biathlon"].collidepoint(mx, my):
                            menu.training_choice = 2
                        elif buttons["btn_back"].collidepoint(mx, my):
                            menu.training_choice = 3

                # Options
                elif state == "options":
                    result = menu.handle_options_menu_input(event)
                    if result == "vol_up":
                        volume = min(1.0, volume + 0.05)
                        set_master_volume(audio, volume)
                    elif result == "vol_down":
                        volume = max(0.0, volume - 0.05)
                        set_master_volume(audio, volume)
                    elif result == "window_next":
                        display_mode_index = (display_mode_index + 1) % len(WINDOW_PRESETS)
                        display = init_display(display_mode_index)
                        screen = display["screen"]
                        virtual_screen = display["virtual"]
                        menu.screen = virtual_screen
                        game.screen = virtual_screen
                        curling.screen = virtual_screen
                        biathlon.screen = virtual_screen
                    elif result == "window_prev":
                        display_mode_index = (display_mode_index - 1) % len(WINDOW_PRESETS)
                        display = init_display(display_mode_index)
                        screen = display["screen"]
                        virtual_screen = display["virtual"]
                        menu.screen = virtual_screen
                        game.screen = virtual_screen
                        curling.screen = virtual_screen
                        biathlon.screen = virtual_screen
                    elif result == "back":
                        state = "menu"
                    elif result == "mouse_click":
                        mx, my = map_mouse(event.pos, display)
                        label = WINDOW_PRESETS[display_mode_index][0]
                        buttons = menu.draw_options_menu(volume, label)
                        if buttons["btn_vol_minus"].collidepoint(mx, my):
                            volume = max(0.0, volume - 0.05)
                            set_master_volume(audio, volume)
                        elif buttons["btn_vol_plus"].collidepoint(mx, my):
                            volume = min(1.0, volume + 0.05)
                            set_master_volume(audio, volume)
                        elif buttons["btn_win_prev"].collidepoint(mx, my):
                            display_mode_index = (display_mode_index - 1) % len(WINDOW_PRESETS)
                            display = init_display(display_mode_index)
                            screen = display["screen"]
                            virtual_screen = display["virtual"]
                            menu.screen = virtual_screen
                            game.screen = virtual_screen
                            curling.screen = virtual_screen
                            biathlon.screen = virtual_screen
                        elif buttons["btn_win_next"].collidepoint(mx, my):
                            display_mode_index = (display_mode_index + 1) % len(WINDOW_PRESETS)
                            display = init_display(display_mode_index)
                            screen = display["screen"]
                            virtual_screen = display["virtual"]
                            menu.screen = virtual_screen
                            game.screen = virtual_screen
                            curling.screen = virtual_screen
                            biathlon.screen = virtual_screen
                        elif buttons["btn_back"].collidepoint(mx, my):
                            state = "menu"

                # Classement
                elif state == "leaderboard":
                    result = menu.handle_leaderboard_input(event)
                    if result == "back":
                        state = "menu"
                
                # En jeu
                elif state == "playing":
                    if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                        game.paused = not game.paused
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"
                        game.paused = False
                        game.game_over = False
                        stop_music()
                        play_music(audio, "menu")
                
                # Mode Curling
                elif state == "curling":
                    curling.handle_input(event)
                    if event.key == pygame.K_RETURN and game.mode == "jo" and jo_stage == "curling" and curling.game_over:
                        jo_stage = "biathlon"
                        jo_transition_timer = 0.0
                        biathlon.reset()
                        state = "biathlon"
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu" if game.mode == "jo" else "training_menu"
                        stop_music()
                        play_music(audio, "menu")
                
                # Mode Biathlon
                elif state == "biathlon":
                    biathlon.handle_input(event)
                    if event.key == pygame.K_RETURN and game.mode == "jo" and jo_stage == "biathlon" and biathlon.game_over:
                        jo_stage = "ski"
                        jo_transition_timer = 0.0
                        game.data["final_done"] = True
                        pending_score = jo_pending_score
                        pending_time = jo_pending_time
                        state = "game_over"
                        stop_music()
                        play_music(audio, "menu")
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu" if game.mode == "jo" else "training_menu"
                        stop_music()
                        play_music(audio, "menu")
                
                # Game over
                elif state == "game_over":
                    if event.key == pygame.K_r:
                        # Rejouer le niveau
                        game.reset_game(level=game.data["level"])
                        state = "playing"
                        game.paused = False
                        game.game_over = False
                        stop_music()
                        play_music(audio, "game")
                    
                    elif event.key == pygame.K_RETURN:
                        if game.mode == "jo" and game.data.get("final_done") and pending_score is not None and name_input.strip() == "":
                            state = "name_entry"
                        else:
                            if not game.data.get("win"):
                                # Rejouer le niveau
                                game.reset_game(level=game.data["level"])
                                state = "playing"
                                game.paused = False
                                game.game_over = False
                                stop_music()
                                play_music(audio, "game")
                            elif game.data.get("win") and game.data["level"] < 5:
                                # Niveau suivant
                                game.reset_game(level=game.data["level"] + 1)
                                state = "playing"
                                game.paused = False
                                game.game_over = False
                                stop_music()
                                play_music(audio, "game")
                            else:
                                # Retour au menu
                                state = "menu"
                                stop_music()
                                play_music(audio, "menu")
                
                # Saisie du nom
                elif state == "name_entry":
                    if event.key == pygame.K_RETURN:
                        if name_input.strip() != "":
                            if pending_score is not None:
                                # Ajouter au leaderboard
                                leaderboard.append((pending_score, name_input.strip(), pending_time))
                                leaderboard.sort(key=lambda x: x[0], reverse=True)
                                leaderboard = leaderboard[:5]
                                pending_score = None
                                pending_time = None
                                state = "game_over"
                            else:
                                # Commencer le jeu
                                game.mode = "jo"
                                game.reset_game(level=1)
                                state = "playing"
                                game.paused = False
                                game.game_over = False
                                jo_stage = "ski"
                                jo_transition_timer = 0.0
                                jo_pending_score = None
                                jo_pending_time = None
                                stop_music()
                                play_music(audio, "game")
                    
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"
                    
                    else:
                        # Ajouter le caractère
                        if event.unicode.isprintable() and len(name_input) < 12:
                            name_input += event.unicode

            # Clic souris
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "menu":
                    result = menu.handle_main_menu_input(event)
                    if result == "mouse_click":
                        mx, my = map_mouse(event.pos, display)
                        buttons = menu.draw_main_menu(0)
                        if buttons["btn_triathlon"].collidepoint(mx, my):
                            menu.menu_choice = 0
                        elif buttons["btn_training"].collidepoint(mx, my):
                            menu.menu_choice = 1
                        elif buttons["btn_options"].collidepoint(mx, my):
                            menu.menu_choice = 2
                        elif buttons["btn_leaderboard"].collidepoint(mx, my):
                            menu.menu_choice = 3
                elif state == "training_menu":
                    result = menu.handle_training_menu_input(event)
                    if result == "mouse_click":
                        mx, my = map_mouse(event.pos, display)
                        buttons = menu.draw_training_menu()
                        if buttons["btn_course"].collidepoint(mx, my):
                            menu.training_choice = 0
                        elif buttons["btn_curling"].collidepoint(mx, my):
                            menu.training_choice = 1
                        elif buttons["btn_biathlon"].collidepoint(mx, my):
                            menu.training_choice = 2
                        elif buttons["btn_back"].collidepoint(mx, my):
                            menu.training_choice = 3
                elif state == "options":
                    result = menu.handle_options_menu_input(event)
                    if result == "mouse_click":
                        mx, my = map_mouse(event.pos, display)
                        label = WINDOW_PRESETS[display_mode_index][0]
                        buttons = menu.draw_options_menu(volume, label)
                        if buttons["btn_vol_minus"].collidepoint(mx, my):
                            volume = max(0.0, volume - 0.05)
                            set_master_volume(audio, volume)
                        elif buttons["btn_vol_plus"].collidepoint(mx, my):
                            volume = min(1.0, volume + 0.05)
                            set_master_volume(audio, volume)
                        elif buttons["btn_win_prev"].collidepoint(mx, my):
                            display_mode_index = (display_mode_index - 1) % len(WINDOW_PRESETS)
                            display = init_display(display_mode_index)
                            screen = display["screen"]
                            virtual_screen = display["virtual"]
                            menu.screen = virtual_screen
                            game.screen = virtual_screen
                            curling.screen = virtual_screen
                            biathlon.screen = virtual_screen
                        elif buttons["btn_win_next"].collidepoint(mx, my):
                            display_mode_index = (display_mode_index + 1) % len(WINDOW_PRESETS)
                            display = init_display(display_mode_index)
                            screen = display["screen"]
                            virtual_screen = display["virtual"]
                            menu.screen = virtual_screen
                            game.screen = virtual_screen
                            curling.screen = virtual_screen
                            biathlon.screen = virtual_screen
                        elif buttons["btn_back"].collidepoint(mx, my):
                            state = "menu"
                elif state == "leaderboard":
                    result = menu.handle_leaderboard_input(event)
                    if result == "mouse_click":
                        mx, my = map_mouse(event.pos, display)
                        buttons = menu.draw_leaderboard(leaderboard)
                        if buttons["btn_back"].collidepoint(mx, my):
                            state = "menu"
        
        # Récupérer les touches pressées
        keys = pygame.key.get_pressed()
        
        # Mise à jour
        if state == "playing" and not game.paused:
            game.update(dt, keys)
            # Vérifier si le jeu est terminé
            if game.game_over:
                # Transition JO vers Curling/Biathlon apres le ski (niveau 5)
                if game.mode == "jo" and game.data.get("win") and game.data["level"] >= 5 and jo_stage == "ski":
                    jo_pending_score = game.data["score"]
                    jo_pending_time = game.data.get("race_time_end")
                    game.data["final_done"] = False
                    jo_stage = "curling"
                    jo_transition_timer = 0.0
                    curling.reset()
                    state = "curling"
                    stop_music()
                    play_music(audio, "game")
                else:
                    state = "game_over"
                    stop_music()
                    # Enregistrer le score si mode JO
                    if game.mode == "jo" and game.data.get("final_done"):
                        pending_score = game.data["score"]
                        pending_time = game.data.get("race_time_end")
                        if name_input.strip() != "":
                            leaderboard.append((pending_score, name_input.strip(), pending_time))
                            leaderboard.sort(key=lambda x: x[0], reverse=True)
                            leaderboard = leaderboard[:5]
                            pending_score = None
                            pending_time = None
        
        elif state == "curling":
            curling.update(dt, keys)
            if curling.game_over and game.mode == "jo" and jo_stage == "curling":
                jo_transition_timer += dt
                if jo_transition_timer >= 1.0:
                    jo_stage = "biathlon"
                    jo_transition_timer = 0.0
                    biathlon.reset()
                    state = "biathlon"
        
        elif state == "biathlon":
            biathlon.update(dt, keys)
            if biathlon.game_over and game.mode == "jo" and jo_stage == "biathlon":
                jo_transition_timer += dt
                if jo_transition_timer >= 1.0:
                    jo_stage = "ski"
                    jo_transition_timer = 0.0
                    game.data["final_done"] = True
                    pending_score = jo_pending_score
                    pending_time = jo_pending_time
                    state = "game_over"
                    stop_music()
                    play_music(audio, "menu")
        
        # Affichage
        work_surface.fill(COLOR_BLUE_SKY)
        
        if state == "splash":
            splash_ready = menu.draw_splash(dt)
        
        elif state == "menu":
            menu.draw_main_menu(dt)
        
        elif state == "training_menu":
            menu.draw_training_menu()
        
        elif state == "options":
            label = WINDOW_PRESETS[display_mode_index][0]
            menu.draw_options_menu(volume, label)

        elif state == "leaderboard":
            menu.draw_leaderboard(leaderboard)
        
        elif state == "playing":
            game.draw_game()
            if game.paused:
                menu.draw_pause()
        
        elif state == "curling":
            curling.draw()
        
        elif state == "biathlon":
            biathlon.draw()
        
        elif state == "game_over":
            game.draw_game()
            game.draw_game_over(leaderboard)
        
        elif state == "name_entry":
            # Fond dégradé
            for i in range(SCREEN_HEIGHT):
                shade = 228 + int(18 * (i / SCREEN_HEIGHT))
                work_surface.fill((shade, shade + 6, 255), rect=pygame.Rect(0, i, SCREEN_WIDTH, 1))
            
            # Panel de saisie
            panel_w, panel_h = 500, 240
            panel_x = SCREEN_WIDTH // 2 - panel_w // 2
            panel_y = SCREEN_HEIGHT // 2 - panel_h // 2
            
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((250, 252, 255, 240))
            pygame.draw.rect(panel, (200, 220, 235, 230), (0, 0, panel_w, panel_h), 3, border_radius=10)
            work_surface.blit(panel, (panel_x, panel_y))
            
            prompt = fonts["big"].render("Entre ton prénom", True, COLOR_TEXT_DARK)
            val = fonts["medium"].render(name_input or "_", True, COLOR_BUTTON_PRIMARY)
            hint = fonts["small"].render("ENTRER pour valider | ECHAP pour annuler", True, COLOR_TEXT_DARK)
            
            work_surface.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, panel_y + 30))
            work_surface.blit(val, (SCREEN_WIDTH // 2 - val.get_width() // 2, panel_y + 100))
            work_surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, panel_y + 170))
        
        # Effets visuels
        work_surface.blit(vignette, (0, 0))
        work_surface.blit(grain, (0, 0))
        
        # Mise a l'echelle si necessaire
        if display["scaled_width"] != SCREEN_WIDTH or display["scaled_height"] != SCREEN_HEIGHT or display["offset_x"] != 0 or display["offset_y"] != 0:
            screen.fill((0, 0, 0))
            scaled_surface = pygame.transform.scale(
                virtual_screen,
                (display["scaled_width"], display["scaled_height"])
            )
            screen.blit(scaled_surface, (display["offset_x"], display["offset_y"]))
        else:
            screen.blit(virtual_screen, (0, 0))
        
        # Mise à jour de l'affichage
        pygame.display.flip()
    
    # Fin du jeu
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
