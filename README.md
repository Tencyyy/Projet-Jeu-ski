# 🎿 JO d'Hiver 2026 - Ski Runner

Un jeu de ski olympique développé par le Groupe 1, inspiré des Jeux Olympiques de Milano-Cortina 2026.

## 🎮 Description

Ski Runner est un jeu de course de ski avec plusieurs modes de jeu, incluant un mode Triathlon Olympique avec classement et médailles !

### Fonctionnalités principales
- ✅ **Mode JO (Triathlon)** : 5 niveaux de difficulté croissante avec classement final
- ✅ **Mode Entraînement** : 
  - 🎿 Course de ski (slalom)
  - 🥌 **Curling** (NOUVEAU !)
  - 🎯 **Biathlon** (NOUVEAU !)
- ✅ **Système de classement** : Or 🥇, Argent 🥈, Bronze 🥉
- ✅ **Effets sonores** : Support pour musiques et sons personnalisés
- ✅ **Menu interactif** : Navigation fluide avec animations
- ✅ **Mode plein écran** : S'adapte à votre résolution d'écran

## 📁 Structure du Projet

```
winter_olympics_game_final/
│
├── winter_runner.py          # ⭐ FICHIER PRINCIPAL - Lance le jeu
├── requirements.txt          # Dépendances Python
├── README.md                # Ce fichier
│
├── game/                    # Code source du jeu
│   ├── __init__.py
│   ├── main.py             # Boucle principale
│   ├── config.py           # Configuration (résolution, FPS, etc.)
│   ├── game_manager.py     # Logique du jeu (ski)
│   ├── curling.py          # 🥌 Mode Curling (NOUVEAU !)
│   ├── biathlon.py         # 🎯 Mode Biathlon (NOUVEAU !)
│   ├── menu.py             # Système de menus
│   ├── entities.py         # Entités (joueur, obstacles, etc.)
│   ├── assets.py           # Chargement des ressources
│   └── audio.py            # Système audio
│
└── assets/                 # Ressources du jeu
    ├── music/              # 🎵 Mettez vos musiques ici
    │   ├── menu_music.mp3  # (optionnel) Musique du menu
    │   └── game_music.mp3  # (optionnel) Musique en jeu
    │
    ├── sounds/             # 🔊 Mettez vos effets sonores ici
    │   ├── gate.wav        # (optionnel) Son de porte
    │   ├── bonus.wav       # (optionnel) Son de bonus
    │   ├── speed.wav       # (optionnel) Son de boost
    │   └── rock.wav        # (optionnel) Son de collision
    │
    └── *.png               # Images du jeu (skieur, obstacles, etc.)
```

## 🚀 Installation et Lancement

### Prérequis
- Python 3.8 ou supérieur
- Pygame

### Installation

1. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

2. **Lancer le jeu** :
```bash
python winter_runner.py
```

## 🎯 Comment Jouer

### Contrôles
- **Flèches directionnelles** : Déplacer le skieur
- **P ou Espace** : Mettre en pause
- **R** : Rejouer après Game Over
- **Entrée** : Valider les choix / Niveau suivant
- **Échap** : Retour au menu / Quitter

### Modes de Jeu

#### 🏆 Mode JO (Triathlon)
- Complétez 5 niveaux de difficulté croissante
- Évitez les obstacles (rochers, arbres)
- Passez par les portes pour marquer des points
- Collectez les bonus pour des effets spéciaux
- Attention au Yeti à partir du niveau 2 !
- **Classement final avec médailles** : Or, Argent, Bronze

#### 🏃 Mode Entraînement

##### 🎿 Course de ski
- Entraînez-vous sur un seul niveau
- Même gameplay que le Mode JO
- Pas de classement

##### 🥌 Curling (NOUVEAU !)
- Lancez une pierre de curling vers le centre de la cible
- 3 lancers pour marquer le maximum de points
- Contrôlez l'angle et la puissance
- **Objectif** : Toucher le centre (100 points)
- Temps limite : 12 secondes

##### 🎯 Biathlon (NOUVEAU !)
- Tirez sur 5 cibles avec un arc
- Déplacez le réticule et ajustez la puissance
- 5 tirs maximum
- **Objectif** : Toucher toutes les cibles
- Temps limite : 20 secondes

➡️ **Voir le guide complet** : `GUIDE_CURLING_BIATHLON.md`

### Système de Points
- **Portes réussies** : +20 points
- **Bonus collectés** : +10 points + effet spécial
- **Temps de course** : Bonus si vous terminez rapidement
- **Pénalités** : -15 points par obstacle touché

### Bonus Spéciaux
- ⚡ **Boost de vitesse** : Accélération temporaire
- 🌙 **Moonwalk** : Ralentissement du temps

## ⚙️ Configuration

Éditez le fichier `game/config.py` pour personnaliser :

```python
# Mode d'affichage
FULLSCREEN = True  # True pour plein écran, False pour mode fenêtré

# Résolution (en mode fenêtré)
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640

# Performance
FPS = 60
```

## 🎵 Ajouter vos Musiques et Sons

### Musiques
Placez vos fichiers audio dans `assets/music/` :
- `menu_music.mp3` (ou `.ogg`, `.wav`) : Musique du menu
- `game_music.mp3` (ou `.ogg`, `.wav`) : Musique en jeu

### Effets Sonores
Placez vos fichiers dans `assets/sounds/` :
- `gate.wav` : Son de passage de porte
- `bonus.wav` : Son de collecte de bonus
- `speed.wav` : Son d'activation de boost
- `rock.wav` : Son de collision
- `curling_slide.wav` : Son de curling
- `arrow_shot.wav` : Son de tir
- `game_over.wav` : Son de fin de partie
- `pause.wav` : Son de pause
- `resume.wav` : Son de reprise

**Note** : Si les fichiers n'existent pas, le jeu utilisera des sons générés automatiquement.

## 🏅 Système de Classement

En **Mode JO**, terminez les 5 niveaux pour enregistrer votre score :
1. Entrez votre prénom
2. Votre score et temps sont enregistrés
3. Le classement affiche les 3 meilleurs joueurs avec :
   - 🥇 Médaille d'Or (1er)
   - 🥈 Médaille d'Argent (2e)
   - 🥉 Médaille de Bronze (3e)

## 🐛 Dépannage

### Le jeu ne démarre pas
- Vérifiez que Python 3.8+ est installé : `python --version`
- Installez pygame : `pip install pygame`

### Pas de son
- Vérifiez que pygame.mixer est initialisé
- Ajoutez vos fichiers audio dans les dossiers `music/` et `sounds/`
- Le jeu fonctionnera avec des sons générés si aucun fichier n'est trouvé

### Mode plein écran qui ne fonctionne pas
- Changez `FULLSCREEN = False` dans `game/config.py`
- Relancez le jeu

## 👥 Crédits

**Groupe 1** - JO d'Hiver 2026
- Développement : Groupe 1
- Inspiré par : Milano-Cortina 2026

## 📝 Licence

Projet éducatif - Tous droits réservés