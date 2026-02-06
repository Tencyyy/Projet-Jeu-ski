# 🎿 JO d'hiver 2026 - Ski Runner

Un jeu de ski olympique développé par le Groupe 1 pour le projet JO d'hiver 2026.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![Pygame](https://img.shields.io/badge/pygame-2.0+-orange)

## 📋 Description

Dévalez les pistes olympiques dans ce runner de ski palpitant ! Évitez les obstacles, franchissez les portes et battez vos records pour devenir le champion olympique.

### ✨ Fonctionnalités

- **Mode JO** : Progression sur 5 niveaux avec difficulté croissante
- **Mode Entraînement** : Pratiquez librement ou découvrez les mini-jeux
- **Système de score** : Classement des meilleurs joueurs
- **Effets visuels** : Neige animée, vignette, effets de particules
- **Musique et sons** : Ambiance olympique immersive
- **Obstacles variés** : Rochers, arbres, drone avec blocs de glace
- **Bonus** : Boost de vitesse et effet moonwalk
- **Boss Yeti** : À partir du niveau 2, un yeti vous poursuit !

## 🎮 Contrôles

| Touche | Action |
|--------|--------|
| **↑ ↓ ← →** | Déplacer le skieur |
| **P** ou **Espace** | Pause |
| **R** | Rejouer (après game over) |
| **ENTREE** | Valider les choix de menu |
| **ECHAP** | Quitter / Retour au menu |

## 🎵 Musique personnalisée

Vous pouvez ajouter votre propre musique ! Créez simplement :
- `assets/music/menu_music.mp3` - Musique du menu
- `assets/music/game_music.mp3` - Musique du jeu

**Formats supportés** : MP3, OGG, WAV

📖 **Guide complet** : Consultez [MUSIQUE_ET_PLEIN_ECRAN.md](MUSIQUE_ET_PLEIN_ECRAN.md)

## 🖥️ Mode Plein Écran

Pour jouer en plein écran, éditez `game/config.py` :
```python
FULLSCREEN = True  # Changez False en True
```

Le jeu s'adaptera automatiquement à votre écran !

## 🚀 Installation et lancement

### Prérequis

- Python 3.7 ou supérieur
- Pygame 2.0 ou supérieur

### Installation

1. Clonez ou téléchargez ce dépôt
2. Installez Pygame si nécessaire :

```bash
pip install pygame
```

### Lancement

```bash
python winter_runner.py
```

## 📁 Structure du projet

```
ski-runner/
│
├── winter_runner.py          # Lanceur principal
│
├── game/                      # Module principal du jeu
│   ├── __init__.py
│   ├── main.py               # Boucle principale et orchestration
│   ├── config.py             # Configuration et constantes
│   ├── menu.py               # Gestion des menus
│   ├── game_manager.py       # Logique du jeu
│   ├── entities.py           # Classes des entités (joueur, obstacles, etc.)
│   ├── assets.py             # Génération et chargement des assets
│   └── audio.py              # Génération des sons
│
└── assets/                    # Ressources générées automatiquement
    ├── skier_*.png           # Sprites du skieur
    ├── rock_*.png            # Sprites des rochers
    ├── tree_*.png            # Sprites des arbres
    ├── bonus_*.png           # Sprites des bonus
    ├── drone_*.png           # Sprite du drone
    ├── yeti_*.png            # Sprites du yeti
    └── bg_tile_*.png         # Tuile de fond
```

## 🎯 Gameplay

### Mode JO

Progressez à travers 5 niveaux de difficulté croissante :
- **Niveau 1** : Initiation
- **Niveau 2** : Le Yeti apparaît !
- **Niveau 3** : Deux Yetis vous poursuivent
- **Niveau 4** : Vitesse maximale
- **Niveau 5** : Défi ultime

**Objectif** : Franchissez la ligne d'arrivée en passant par toutes les portes. Si vous touchez un arbre ou ratez une porte, c'est game over !

### Points

- **+10 points** par porte franchie
- **Bonus de vitesse** : ⚡ Augmente votre vitesse temporairement
- **Bonus moonwalk** : 🌙 Inverse vos contrôles (et trouble le Yeti !)

### Obstacles

- **Rochers** : Vous ralentissent
- **Arbres** : Game over si collision
- **Blocs de glace** : Largués par le drone, vous figent brièvement
- **Yeti** : Vous ralentit et vous pousse

## 👥 Équipe

**Groupe 1** - Projet JO d'hiver 2026

### Répartition des tâches

- **Personne A** : Gameplay et contrôles du joueur
- **Personne B** : Système d'obstacles et niveaux
- **Personne C** : Interface utilisateur et menus
- **Personne D** : Assets visuels et sonores

## 📝 Historique des versions

### Version 2.0 (Actuelle)
- ✅ Code restructuré en modules séparés
- ✅ Menu professionnel amélioré avec animations
- ✅ Système de musique de fond
- ✅ Effets visuels améliorés
- ✅ Meilleure organisation du code

### Version 1.0
- ✅ Gameplay de base fonctionnel
- ✅ Système de portes et obstacles
- ✅ Score et niveaux
- ✅ Génération procédurale des assets

## 🔧 Développement

### Comment ajouter un nouveau niveau

Modifiez le dictionnaire `LEVEL_SETTINGS` dans `game/config.py` :

```python
LEVEL_SETTINGS = {
    6: {
        "speed_base": 180,
        "max_speed": 310,
        # ... autres paramètres
    }
}
```

### Comment ajouter un nouvel obstacle

1. Ajoutez le sprite dans `game/assets.py`
2. Créez la classe dans `game/entities.py`
3. Intégrez-le dans `game/game_manager.py`

## 🐛 Problèmes connus

- Les mini-jeux Curling et Biathlon sont à implémenter
- Le son peut ne pas fonctionner sur certains systèmes

## 📄 Licence

Projet éducatif - Groupe 1 - JO d'hiver 2026

## 🙏 Remerciements

- Pygame community
- L'équipe enseignante
- Tous les testeurs

---

**Bon ski et bonne chance pour devenir champion olympique ! 🏆**
