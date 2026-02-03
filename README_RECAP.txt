# Jeu Ski Runner - recap

Ce depot contient 2 versions:

1) Version complete (dossier `game/` + lanceur `winter_runner.py`)
- Gameplay: runner de ski avec obstacles, portes de sapins a traverser, bonus, drone et yeti.
- Score + niveaux + vitesse qui augmente.
- Ecrans: splash, menu, jeu, pause, game over, saisie de prenom + classement.
- Audio: musiques + effets.
- Assets: images/sons dans `assets/` charges par `game/assets.py`.

Fichiers principaux:
- `winter_runner.py`: lance le jeu complet.
- `game/main.py`: boucle principale + logique des etats.
- `game/entities.py`: classes joueur/obstacles/portes/bonus/drone/yeti.
- `game/assets.py`: prepare/charge les assets.
- `game/audio.py`: sons + musiques.

2) Version prototype (dossier `v1/`)
- Menu ultra basique + bonhomme baton qui bouge aux fleches.
- Pas d'assets, pas de vraie logique de jeu.
- Score bidon + game over bidon.

Fichiers prototype:
- `v1/main.py`: proto minimal.
- `v1/README.txt`: mini fiche prototype.

Lancer:
- Version complete: `python winter_runner.py`
- Version prototype: `python v1/main.py`
