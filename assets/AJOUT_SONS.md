# 🎵 Guide d'Ajout de Musiques et Sons

## 📁 Structure des Dossiers Audio

```
assets/
├── music/          # Musiques de fond
│   ├── menu_music.mp3 (ou .ogg, .wav)
│   └── game_music.mp3 (ou .ogg, .wav)
│
└── sounds/         # Effets sonores
    ├── gate.wav (ou .ogg)
    ├── bonus.wav
    ├── speed.wav
    ├── rock.wav
    ├── curling_slide.wav
    ├── arrow_shot.wav
    ├── game_over.wav
    ├── pause.wav
    └── resume.wav
```

## 🎼 Musiques de Fond

### Menu Principal
**Fichier** : `assets/music/menu_music.mp3`
- **Type** : Musique calme, accueillante
- **Durée** : 1-3 minutes (en boucle)
- **Formats acceptés** : MP3, OGG, WAV
- **Suggestion** : Musique d'ambiance hivernale, orchestrale légère

### En Jeu
**Fichier** : `assets/music/game_music.mp3`
- **Type** : Musique dynamique, énergique
- **Durée** : 1-3 minutes (en boucle)
- **Formats acceptés** : MP3, OGG, WAV
- **Suggestion** : Musique rythmée pour ski de vitesse

## 🔊 Effets Sonores

### Sons de Gameplay

#### gate.wav - Passage de Porte
- **Quand** : Le joueur passe par une porte
- **Type** : Son court, positif, validant
- **Durée** : 0.1-0.3s
- **Exemple** : "Ding!", cloche, validation

#### bonus.wav - Collecte de Bonus
- **Quand** : Le joueur collecte un bonus
- **Type** : Son magique, récompensant
- **Durée** : 0.2-0.5s
- **Exemple** : Scintillement, étoile, power-up

#### speed.wav - Activation Boost
- **Quand** : Le joueur active le boost de vitesse
- **Type** : Son d'accélération, puissant
- **Durée** : 0.2-0.5s
- **Exemple** : Whoosh, turbo, jet

#### rock.wav - Collision
- **Quand** : Le joueur touche un obstacle
- **Type** : Son d'impact, négatif
- **Durée** : 0.1-0.3s
- **Exemple** : Crash, impact, douleur

### Sons de Menu

#### pause.wav - Mise en Pause
- **Quand** : Le joueur met le jeu en pause
- **Type** : Son bref, neutre
- **Durée** : 0.1s
- **Exemple** : Clic bas, pause

#### resume.wav - Reprise
- **Quand** : Le joueur reprend le jeu
- **Type** : Son bref, positif
- **Durée** : 0.1s  
- **Exemple** : Clic aigu, validation

#### game_over.wav - Fin de Partie
- **Quand** : Le joueur termine ou échoue
- **Type** : Son conclusif
- **Durée** : 0.5-1.0s
- **Exemple** : Jingle de fin, fanfare

### Sons Futurs (Modes à venir)

#### curling_slide.wav - Curling
- **Quand** : Pierre de curling glisse
- **Type** : Son de glissement sur glace
- **Durée** : 0.3-0.7s

#### arrow_shot.wav - Biathlon
- **Quand** : Tir de flèche
- **Type** : Son de tir d'arc
- **Durée** : 0.1-0.3s

## 🎹 Comment Ajouter vos Sons

### Méthode 1 : Fichiers Audio Existants
1. Trouvez ou créez vos fichiers audio
2. Renommez-les selon le nom attendu (ex: `gate.wav`)
3. Placez-les dans le bon dossier (`assets/music/` ou `assets/sounds/`)
4. Lancez le jeu - les sons seront automatiquement chargés !

### Méthode 2 : Sons Générés
Si vous ne mettez aucun fichier, le jeu générera automatiquement des sons simples (bips).

## 🛠️ Outils Recommandés

### Pour Créer des Sons
- **Audacity** (gratuit) : Édition audio
- **BFXR** (gratuit) : Générateur de sons de jeu rétro
- **freesound.org** : Bibliothèque de sons gratuits

### Pour Convertir des Formats
- **Online-Convert.com** : Conversion en ligne
- **Audacity** : Export en différents formats

## 📝 Bonnes Pratiques

### Volume
- Normalisez vos sons à un niveau similaire
- Volume recommandé : -6dB à -3dB
- Les musiques ne doivent pas couvrir les effets

### Qualité
- **Musiques** : MP3 128-192 kbps ou OGG
- **Sons** : WAV 44.1kHz 16-bit ou OGG
- Évitez les fichiers trop lourds

### Durée
- **Musiques** : 1-3 minutes (boucle)
- **Sons courts** : < 0.5s
- **Sons moyens** : 0.5-1.0s

## ✅ Checklist

Avant de lancer le jeu :
- [ ] Musique de menu ajoutée
- [ ] Musique de jeu ajoutée
- [ ] Son de porte (gate.wav)
- [ ] Son de bonus (bonus.wav)
- [ ] Son de boost (speed.wav)
- [ ] Son de collision (rock.wav)
- [ ] Tous les fichiers sont dans le bon format
- [ ] Le volume est équilibré

## 🎮 Test

1. Lancez le jeu
2. Vérifiez dans le terminal les messages :
   - ✓ "Musique de menu chargée: menu_music.mp3"
   - ✓ "Son personnalisé chargé: gate"
3. Si vous voyez ⚠️, le jeu utilise des sons générés

---

**Note** : Le jeu fonctionne parfaitement SANS fichiers audio personnalisés. Les sons générés sont fonctionnels mais basiques. Ajoutez vos propres sons pour une expérience optimale !
