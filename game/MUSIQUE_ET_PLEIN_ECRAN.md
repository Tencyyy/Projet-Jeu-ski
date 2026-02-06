# 🎵 Guide : Musique personnalisée et Plein écran

## 🎶 Comment ajouter votre propre musique

### Structure des dossiers

Créez cette structure de dossiers :

```
votre-projet/
├── winter_runner.py
├── game/
│   └── ...
└── assets/
    ├── music/          ← Créez ce dossier
    │   ├── menu_music.mp3
    │   └── game_music.mp3
    └── sounds/         ← Créez ce dossier (optionnel)
        ├── gate.wav
        ├── bonus.wav
        ├── speed.wav
        └── ...
```

### Étape 1 : Créer les dossiers

```bash
mkdir -p assets/music
mkdir -p assets/sounds
```

### Étape 2 : Ajouter vos fichiers musicaux

**Pour la musique du MENU :**
- Nommez votre fichier : `menu_music.mp3` (ou `.ogg` ou `.wav`)
- Placez-le dans `assets/music/`

**Pour la musique du JEU :**
- Nommez votre fichier : `game_music.mp3` (ou `.ogg` ou `.wav`)
- Placez-le dans `assets/music/`

### Formats supportés

✅ **Musiques (longues pistes)** :
- `.mp3` ⭐ Recommandé
- `.ogg` ⭐ Recommandé
- `.wav` (fichiers lourds)

✅ **Effets sonores (sons courts)** :
- `.wav` ⭐ Recommandé
- `.ogg`

### Étape 3 : Lancer le jeu

Le jeu détectera automatiquement vos fichiers et les chargera !

```bash
python winter_runner.py
```

Vous verrez dans la console :
```
✓ Musique de menu chargée: menu_music.mp3
✓ Musique de jeu chargée: game_music.mp3
```

## 🎵 Effets sonores personnalisés (optionnel)

Si vous voulez aussi personnaliser les sons (collisions, bonus, etc.) :

### Noms des fichiers à placer dans `assets/sounds/`

- `gate.wav` - Son quand on passe une porte
- `bonus.wav` - Son quand on ramasse un bonus
- `speed.wav` - Son du boost de vitesse
- `rock.wav` - Son de collision avec un rocher
- `curling_slide.wav` - Son du curling
- `arrow_shot.wav` - Son du tir à l'arc (biathlon)
- `game_over.wav` - Son de game over
- `pause.wav` - Son de mise en pause
- `resume.wav` - Son de reprise du jeu

**Note :** Si vous ne fournissez pas ces fichiers, le jeu générera des sons automatiquement (comme avant).

## 🖥️ Mode Plein Écran

### Activer le plein écran

1. **Ouvrez le fichier** : `game/config.py`

2. **Trouvez la ligne** :
```python
FULLSCREEN = False
```

3. **Changez en** :
```python
FULLSCREEN = True
```

4. **Sauvegardez et lancez le jeu**

### Comment ça marche

En mode plein écran :
- Le jeu s'adapte automatiquement à la résolution de votre écran
- Le ratio d'aspect est préservé (pas de déformation)
- Des bandes noires apparaissent sur les côtés si nécessaire
- Pour quitter : Appuyez sur **ECHAP** ou **Alt+F4**

### Résolutions testées

✅ 1920x1080 (Full HD)
✅ 1366x768 (Laptop)
✅ 2560x1440 (2K)
✅ 3840x2160 (4K)

## 🎼 Où trouver de la musique libre de droits ?

### Sites recommandés

1. **[Incompetech](https://incompetech.com/)** - Gratuit avec attribution
2. **[FreePD](https://freepd.com/)** - Domaine public
3. **[Bensound](https://www.bensound.com/)** - Gratuit avec attribution
4. **[Purple Planet](https://www.purple-planet.com/)** - Gratuit avec attribution
5. **[CC Mixter](http://ccmixter.org/)** - Creative Commons

### Conseils pour choisir votre musique

**Pour le menu :**
- Musique calme et accueillante
- Tempo moyen (90-120 BPM)
- Ambiance "olympique" ou "sportive"
- 🎵 Genres : Orchestral, Cinématique, Électronique douce

**Pour le jeu :**
- Musique énergique et rythmée
- Tempo rapide (120-140 BPM)
- Crée de l'excitation
- 🎵 Genres : Électronique, Rock, Orchestral épique

### Format recommandé

- **Format** : MP3 (meilleure compatibilité)
- **Bitrate** : 128-192 kbps (bon compromis qualité/taille)
- **Durée** : 1-3 minutes minimum (en boucle)

## 🔧 Dépannage

### ❌ "Musique non trouvée"

**Vérifiez :**
1. Le dossier `assets/music/` existe
2. Le nom du fichier est exactement `menu_music.mp3` ou `game_music.mp3`
3. Le fichier n'est pas corrompu (essayez de le lire dans un lecteur audio)

### ❌ "Erreur lors du chargement"

**Essayez :**
1. Convertir votre fichier en MP3 si c'est un autre format
2. Réduire la taille du fichier (< 10 Mo)
3. Utiliser un convertisseur en ligne : [Online-Convert](https://audio.online-convert.com/convert-to-mp3)

### ❌ "Pas de son"

**Vérifiez :**
1. Le volume de votre ordinateur n'est pas à 0
2. Pygame est bien installé : `pip install pygame --upgrade`
3. Les pilotes audio de votre système fonctionnent

### ❌ "Le plein écran ne marche pas"

**Solutions :**
1. Vérifiez que `FULLSCREEN = True` dans `game/config.py`
2. Redémarrez le jeu après la modification
3. Sur Linux : installez les pilotes graphiques appropriés

## 📝 Exemple de configuration complète

```
votre-projet/
├── winter_runner.py
├── game/
│   ├── __init__.py
│   ├── config.py          ← FULLSCREEN = True
│   ├── main.py
│   ├── menu.py
│   ├── game_manager.py
│   ├── entities.py
│   ├── assets.py
│   └── audio.py
└── assets/
    ├── music/
    │   ├── menu_music.mp3  ← Votre musique de menu
    │   └── game_music.mp3  ← Votre musique de jeu
    ├── sounds/             ← (Optionnel)
    │   ├── gate.wav
    │   ├── bonus.wav
    │   └── speed.wav
    └── (autres assets générés automatiquement)
```

## 🎮 Résultat final

Avec cette configuration :
- ✅ Musique personnalisée dans les menus
- ✅ Musique personnalisée en jeu
- ✅ Transitions fluides entre les musiques
- ✅ Plein écran adaptatif
- ✅ Sons personnalisés (optionnel)

## 💡 Astuces

1. **Volume** : Ajustez le volume de vos fichiers MP3 avant de les ajouter (Audacity est gratuit)
2. **Boucle** : Choisissez des musiques qui bouclent bien (début et fin compatibles)
3. **Taille** : Privilégiez des fichiers < 5 Mo pour un chargement rapide
4. **Tests** : Testez vos musiques en jeu pour vérifier qu'elles collent à l'ambiance

---

**Profitez de votre jeu personnalisé ! 🎿🎵**
