import math
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


def build_audio():
    # ca fonction est de preparer les musiques et effets
    try:
        menu_music = _tone(2.5, 440, 0.25)
        game_music = _tone(2.5, 330, 0.25)
        sfx = {
            "gate": _tone(0.12, 660, 0.35),
            "bonus": _tone(0.18, 520, 0.35),
            "speed": _tone(0.18, 740, 0.35),
            "rock": _tone(0.12, 220, 0.35),
            "game_over": _tone(0.5, 180, 0.4),
            "pause": _tone(0.1, 300, 0.25),
            "resume": _tone(0.1, 500, 0.25),
        }
    except pygame.error:
        menu_music = None
        game_music = None
        sfx = {}

    return {
        "menu_music": menu_music,
        "game_music": game_music,
        "sfx": sfx,
    }


def play_sfx(sfx, name):
    # ca c'est pour jouer un effet sonore si il existe
    sound = sfx.get(name)
    if sound:
        sound.play()
