import math
import os
from array import array
import pygame


# ca c'est pour creer un son simple (je debute, c'est pas parfait mais ca marche).
# ca fonction est de generer un son avec une frequence et une duree.
def _tone(seconds, freq, volume=0.3):
    sample_rate = 44100
    total = int(sample_rate * seconds)
    buf = array("h")
    for i in range(total):
        t = i / sample_rate
        sample = int(32767 * volume * math.sin(2 * math.pi * freq * t))
        buf.append(sample)
    return pygame.mixer.Sound(buffer=buf)


def _load_custom_music(filename):
    """
    Charge un fichier audio personnalisé depuis le dossier assets/music/
    Formats supportés: .mp3, .ogg, .wav
    """
    music_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "music")
    music_path = os.path.join(music_dir, filename)
    
    if os.path.exists(music_path):
        try:
            return music_path  # Retourne le chemin pour pygame.mixer.music
        except pygame.error as e:
            print(f"Erreur lors du chargement de {filename}: {e}")
            return None
    return None


def _load_custom_sound(filename):
    """
    Charge un fichier son personnalisé depuis le dossier assets/sounds/
    Formats supportés: .wav, .ogg
    """
    sounds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sounds")
    sound_path = os.path.join(sounds_dir, filename)
    
    if os.path.exists(sound_path):
        try:
            return pygame.mixer.Sound(sound_path)
        except pygame.error as e:
            print(f"Erreur lors du chargement de {filename}: {e}")
            return None
    return None


def build_audio():
    """
    Prépare les musiques et effets sonores.
    
    MUSIQUES PERSONNALISÉES:
    - Placez vos fichiers dans assets/music/
    - menu_music.mp3 ou menu_music.ogg pour la musique du menu
    - game_music.mp3 ou game_music.ogg pour la musique du jeu
    
    SONS PERSONNALISÉS:
    - Placez vos fichiers dans assets/sounds/
    - gate.wav, bonus.wav, speed.wav, rock.wav, etc.
    
    Si les fichiers n'existent pas, des sons générés seront utilisés.
    """
    try:
        # Tentative de chargement de musiques personnalisées
        menu_music_path = None
        game_music_path = None
        
        # Essayer différents formats pour la musique de menu
        for ext in ['.mp3', '.ogg', '.wav']:
            path = _load_custom_music(f'menu_music{ext}')
            if path:
                menu_music_path = path
                print(f"✓ Musique de menu chargée: menu_music{ext}")
                break
        
        # Essayer différents formats pour la musique de jeu
        for ext in ['.mp3', '.ogg', '.wav']:
            path = _load_custom_music(f'game_music{ext}')
            if path:
                game_music_path = path
                print(f"✓ Musique de jeu chargée: game_music{ext}")
                break
        
        # Si pas de musiques personnalisées, utiliser les sons générés
        if not menu_music_path:
            menu_music_sound = _tone(2.5, 440, 0.25)
            print("⚠ Musique de menu générée (pas de fichier trouvé)")
        else:
            menu_music_sound = None  # Sera géré par pygame.mixer.music
        
        if not game_music_path:
            game_music_sound = _tone(2.5, 330, 0.25)
            print("⚠ Musique de jeu générée (pas de fichier trouvé)")
        else:
            game_music_sound = None  # Sera géré par pygame.mixer.music
        
        # Effets sonores - essayer de charger des fichiers personnalisés d'abord
        sfx = {}
        sfx_names = ["gate", "bonus", "speed", "rock", "curling_slide", "arrow_shot", "game_over", "pause", "resume"]
        sfx_defaults = {
            "gate": (0.12, 660, 0.35),
            "bonus": (0.18, 520, 0.35),
            "speed": (0.18, 740, 0.35),
            "rock": (0.12, 220, 0.35),
            "curling_slide": (0.35, 260, 0.25),
            "arrow_shot": (0.12, 880, 0.3),
            "game_over": (0.5, 180, 0.4),
            "pause": (0.1, 300, 0.25),
            "resume": (0.1, 500, 0.25),
        }
        
        for name in sfx_names:
            # Essayer de charger un fichier personnalisé
            custom_sound = _load_custom_sound(f'{name}.wav')
            if not custom_sound:
                custom_sound = _load_custom_sound(f'{name}.ogg')
            
            if custom_sound:
                sfx[name] = custom_sound
                print(f"✓ Son personnalisé chargé: {name}")
            else:
                # Utiliser le son généré par défaut
                seconds, freq, volume = sfx_defaults[name]
                sfx[name] = _tone(seconds, freq, volume)
        
    except pygame.error:
        menu_music_path = None
        game_music_path = None
        menu_music_sound = None
        game_music_sound = None
        sfx = {}
        print("⚠ Erreur lors de l'initialisation audio")

    return {
        "menu_music": menu_music_sound,  # Son généré ou None
        "game_music": game_music_sound,  # Son généré ou None
        "menu_music_path": menu_music_path,  # Chemin fichier ou None
        "game_music_path": game_music_path,  # Chemin fichier ou None
        "sfx": sfx,
        "volume": 1.0,
    }


def play_music(audio, music_type, loops=-1):
    """
    Joue une musique (menu ou game).
    Utilise pygame.mixer.music pour les fichiers, ou Sound.play() pour les sons générés.
    
    Args:
        audio: Dictionnaire retourné par build_audio()
        music_type: "menu" ou "game"
        loops: -1 pour boucle infinie, 0 pour une seule fois
    """
    try:
        path_key = f"{music_type}_music_path"
        sound_key = f"{music_type}_music"
        
        # Arrêter toute musique en cours
        pygame.mixer.music.stop()
        
        volume = audio.get("volume", 1.0)
        if audio.get(path_key):
            # Utiliser pygame.mixer.music pour les fichiers
            pygame.mixer.music.load(audio[path_key])
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
        elif audio.get(sound_key):
            # Utiliser Sound.play() pour les sons générés
            audio[sound_key].set_volume(volume)
            audio[sound_key].play(loops=loops)
    except pygame.error as e:
        print(f"Erreur lors de la lecture de la musique: {e}")


def stop_music():
    """Arrête la musique en cours"""
    try:
        pygame.mixer.music.stop()
    except:
        pass


def play_sfx(sfx, name):
    """Joue un effet sonore"""
    sound = sfx.get(name)
    if sound:
        sound.play()


def set_master_volume(audio, volume):
    """Applique un volume global (0.0 à 1.0)"""
    volume = max(0.0, min(1.0, float(volume)))
    audio["volume"] = volume
    try:
        pygame.mixer.music.set_volume(volume)
    except pygame.error:
        pass
    if audio.get("menu_music"):
        audio["menu_music"].set_volume(volume)
    if audio.get("game_music"):
        audio["game_music"].set_volume(volume)
    for snd in audio.get("sfx", {}).values():
        try:
            snd.set_volume(volume)
        except pygame.error:
            pass
    return volume
